import asyncio
import json
from asyncio import Future
from typing import Dict

from adoption_agency_common.saga_manager.base_message import BaseMessage
from adoption_agency_common.saga_manager.rabbit_broker import RabbitMQClient
from adoption_agency_common.util import correlation_guid, consts

pending_futures: Dict[str, Future] = {}

class SagaBase:
    def __init__(self):
        self.broker = RabbitMQClient()

    async def send_message(self, message: BaseMessage):
        queue_name = routing_key = message.headers.get("callback_queue", message.get_message_name(message.__class__))
        message.headers.pop("callback_queue", None)
        if not message.headers.get("guid"):
            message.headers["guid"] = correlation_guid.get()
        body = json.dumps({
            "payload": message.payload,
            "headers": message.headers
        })
        await self.broker.publish(queue_name, body, routing_key)


    async def send_response(self, message: BaseMessage):
        fut = pending_futures.get(message.headers["guid"])
        if fut:
            fut.set_result(message.payload)

    async def send_message_and_respond(self, message: BaseMessage):
        message.headers["callback_queue"] = consts.service_callback_queue
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        pending_futures[correlation_guid.get()] = future
        queue_name = routing_key = message.get_message_name(message.__class__)

        body = json.dumps({
            "payload": message.payload,
            "headers": message.headers
        })
        await self.broker.publish(queue_name, body, routing_key)
        message.headers.pop("callback_queue", None)

        return await future
