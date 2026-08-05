import asyncio
import json
from typing import List

import aio_pika

from adoption_agency_common.saga_manager.base_saga import pending_futures
from adoption_agency_common.saga_manager.rabbit_broker import RabbitMQClient
from adoption_agency_common.util import correlation_guid, consts,logger
from adoption_agency_common.util.consts import service_callback_queue

message_handlers = {}

class SagaNode:
    def __init__(self, handlers: List, outgoing_messages: List = ()):
        self.broker = RabbitMQClient()
        self.outgoing_messages = [x.get_message_name(x) for x in outgoing_messages]

    async def initialise(self):
        await self.broker.initialize(quorum_queues=[str(x) for x in message_handlers.keys()])
        await self.broker.start_consuming([str(x) for x in message_handlers.keys()], self.process_message)


    def start_node(self):
        pass

    async def process_message(self, message: aio_pika.IncomingMessage) -> None:
        logger.debug(f"Received {message.routing_key}")
        if message.routing_key == consts.service_callback_queue:
            guid = json.loads(message.body.decode())["headers"]["guid"]
            fut = pending_futures.get(guid)
            if fut:
                fut.set_result(json.loads(message.body.decode()))
            return

        msg_cls = message_handlers[message.routing_key]["message_class"].model_validate_json(message.body.decode())

        handler_cls = message_handlers[message.routing_key]["cls"]()
        method = getattr(handler_cls, message_handlers[message.routing_key]["method"])
        correlation_guid.set(msg_cls.headers.guid)
        if message_handlers[message.routing_key]["is_async"]:
            await method(msg_cls)
        else:
            method(msg_cls)
        logger.debug(f"Received async message: {message.body.decode()}")