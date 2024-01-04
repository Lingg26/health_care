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
            session["account_id"] = user.account_id

    async def on_disconnect(self, sid):
        rooms = connected_clients.pop(sid, [])
        for room in rooms:
            room_clients[room].remove(sid)

    def on_join_room(self, sid, room):
        self.enter_room(sid, room)
        connected_clients[sid].add(room)
        room_clients.setdefault(room, set()).add(sid)

    def on_leave_room(self, sid, room):
        self.leave_room(sid, room)

    async def on_send_message(self, sid, data):
        async with self.session(sid) as session:
            account_id = session.get("account_id", "Anonymous")

        room = data.get('room')
        message = data.get('message')
        account_name = data.get("account_name")
        display_name = data.get("display_name")
        upload_file_path = data.get("upload_file_path")

        db = SessionLocal()
        matching = db.query(models.Matching).filter(models.Matching.matching_id == room).first()
        if matching:
            new_chat = models.Chat(
                matching_id=room,
                chat_text=message,
                send_account_id=account_id,
                is_read=0,
                is_system_write=0,
            )
            db.add(new_chat)
            db.commit()

            # Check who is in the room
            clients = list(room_clients.get(room, []))
            if sid in clients:
                clients.remove(sid)  # Remove the sender's sid

            chat_obj = new_chat.dict()
            chat_obj['account_name'] = account_name
            chat_obj['display_name'] = display_name
            chat_obj['upload_file_path'] = upload_file_path

            if not clients:
                target_account_id = matching.account_id if matching.target_account_id == account_id else matching.target_account_id
                existing_notice = (
                    db.query(models.Notice)
                    .filter(
                        models.Notice.account_id == target_account_id,
                        models.Notice.notice_type == 5,
                        models.Notice.matching_id == matching.matching_id
                    )
                    .first()
                )
                if not existing_notice:
                    # Register notice
                    notification = models.Notice(
                        matching_id=new_chat.matching_id,
                        account_id=matching.account_id if matching.target_account_id == account_id else matching.target_account_id,
                        display_text=f'{display_name}さんから新規チャットが届いています。',
                        notice_type=5,
                    )
                    new_notice = notice_service.register(db, notification)

                    notice = notification.dict()
                    notice["notice_id"] = new_notice.notice_id
                    notice["created_at"] = str(new_notice.created_at)
                    await self.emit(
                        'new_notice',
                        {
                            "Notice": notice,
                            "matching_status": matching.matching_status
                        },
                        room=f"account_{target_account_id}",  # Send the message to the recipient
                    )
                else:
                    existing_notice.created_at = datetime.now()
                    db.commit()
            await self.emit(
                'new_message',
                {
                    'account_id': account_id,
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
