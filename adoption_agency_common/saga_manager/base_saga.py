import asyncio
import json
from asyncio import Future
from typing import Dict, Optional

from pydantic import BaseModel

from adoption_agency_common.saga_manager.base_message import BaseMessage
from adoption_agency_common.saga_manager.rabbit_broker import RabbitMQClient
from adoption_agency_common.util import correlation_guid, consts

pending_futures: Dict[str, Future] = {}

class SagaBase:
    def __init__(self):
        self.broker = RabbitMQClient()

    async def send_message(self, message: BaseMessage):
        queue_name = routing_key = message.headers.callback_queue or message.get_message_name(message.__class__)
        message.headers.callback_queue = None
        message.headers.guid = message.headers.guid or correlation_guid.get()
        body = message.model_dump_json()
        await self.broker.publish(queue_name, body, routing_key)


    async def send_response(self, message: BaseMessage):
        fut = pending_futures.get(message.headers.guid)
        if fut:
            fut.set_result(message.model_dump())

    async def send_message_and_respond(self, message: BaseMessage, result_model: Optional[type[BaseModel]] = None):
        message.headers.callback_queue = consts.service_callback_queue
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        pending_futures[correlation_guid.get()] = future
        queue_name = routing_key = message.get_message_name(message.__class__)

        body = message.model_dump_json()
        await self.broker.publish(queue_name, body, routing_key)
        message.headers.callback_queue = None

        res =  await future
        return result_model.model_validate(res) if result_model else res
