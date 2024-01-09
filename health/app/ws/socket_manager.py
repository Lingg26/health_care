from datetime import datetime
from typing import Union, List

import socketio
from socketio import AsyncNamespace

from fastapi import FastAPI
from health import models

from health.tools.deps import get_current_authenticated_user
from health.shared.database import SessionLocal

connected_clients = {}
room_clients = {}


class ChatNamespace(AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        user = get_current_authenticated_user(SessionLocal(), auth)
        connected_clients[sid] = set()
        # Initializing user session
        async with self.session(sid) as session:
            session["account_id"] = user.id

    async def on_disconnect(self, sid):
        pass
        # rooms = connected_clients.pop(sid, [])
        # for room in rooms:
        #     room_clients[room].remove(sid)

    async def on_join_room(self, sid, room):
        await self.enter_room(sid, room)
        # connected_clients[sid].add(room)
        # room_clients.setdefault(room, set()).add(sid)

    def on_leave_room(self, sid, room):
        self.leave_room(sid, room)

    async def on_send_message(self, sid, data):
        async with self.session(sid) as session:
            account_id = session.get("account_id", "Anonymous")

        room = data.get('room')
        message = data.get('message')

        db = SessionLocal()
        new_chat = models.ChatHistory(
            account_id=room,
            message=message,
            sent_account_id=account_id,
            status="sent"
        )
        db.add(new_chat)
        db.commit()
        chat_obj = new_chat.dict()
        chat_obj["created_at"] = str(new_chat.created_at)
        await self.emit(
            'new_message',
            {
                'message': message,
                'data': {'chat_obj': chat_obj},
            },
            room=room,  # Send the message to the recipient
        )


class SocketManager:
    def __init__(
            self,
            app: FastAPI,
            mount_location: str = "/ws",
            socketio_path: str = "socket.io",
            cors_origins: Union[str, List[str]] = [],
    ):
        self._server = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=cors_origins)
        self._app = socketio.ASGIApp(self._server, socketio_path=socketio_path)
        app.mount(mount_location, self._app)
        app.sio = self._server
        self._server.register_namespace(ChatNamespace('/chat'))

    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying Socket.IO server instance.

        :param name: The attribute name.
        :return: Attribute from the Socket.IO server instance.
        """
        return getattr(self._server, name)
