from asyncio import Future

from fastapi import APIRouter
import json
import asyncio

from pydantic import BaseModel

from adoption_agency_common.saga_manager.base_saga import pending_futures
from adoption_agency_common.saga_manager.rabbit_broker import RabbitMQClient
from adoption_agency_common.saga_manager.base_message import BaseMessage
from adoption_agency_common.util import correlation_guid

class BOARouter(APIRouter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.broker = RabbitMQClient()

    async def send_message(self, message: BaseMessage, res_model: type[BaseModel] = None, ):
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        pending_futures[correlation_guid.get()] = future
        await self.send_message_and_forget(message)
        res = await future
        if res_model:
            return res_model.model_validate(res)
        return res

    async def send_message_and_forget(self, message: BaseMessage):
        queue_name = routing_key = message.get_message_name(message.__class__)
        if not message.headers.get("guid"):
            message.headers["guid"] = correlation_guid.get()
        body = json.dumps({
            "payload": message.payload,
            "headers": message.headers
        })
        await self.broker.publish(queue_name, body, routing_key)