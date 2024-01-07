import json
from fastapi import Request
from pydantic import BaseModel

from health.app.ws.messages import NOTI_MESSAGE, CHAT_MESSAGE
from health.main import sio


class EventEmitter:
    def __init__(self, request: Request) -> None:
        self.request = request

    async def _emit_event_to_room(self, event_name, data, room, **kwargs):
        payload_data = data.dict() if isinstance(data, BaseModel) else data
        payload = {'data': payload_data, 'room': room, **kwargs}
        await sio.emit(event_name, payload, room=room)

    async def send_noti_message(self, data, room, **kwargs):
        await self._emit_event_to_room(event_name=NOTI_MESSAGE, data=data, room=room, **kwargs)

    async def send_chat_message(self, data, room, **kwargs):
        await self._emit_event_to_room(event_name=CHAT_MESSAGE, data=data, room=room, **kwargs)
