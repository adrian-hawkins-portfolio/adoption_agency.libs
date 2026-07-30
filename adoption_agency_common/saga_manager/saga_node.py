import asyncio
import json
from typing import List

import aio_pika

from adoption_agency_common.saga_manager.rabbit_broker import RabbitMQClient
from adoption_agency_common.util import correlation_guid

message_handlers = {}

class SagaNode:
    def __init__(self, handlers: List, outgoing_messages: List = ()):
        self.broker = RabbitMQClient()
        self.outgoing_messages = [x.get_message_name(x) for x in outgoing_messages]

    async def initialise(self):
        await self.broker.initialize(quorum_queues=[str(x) for x in message_handlers.keys()])
        await self.broker.start_consuming([str(x) for x in message_handlers.keys()], self.process_message)
        # self.declare_input_queues()

    # def declare_input_queues(self):
    #     queues = [str(x) for x in message_handlers.keys()]
    #     self.broker.declare_quorum_queues(queues)
    #     self.broker.start_consuming(queues, self.process_message)

    def start_node(self):
        pass

    async def process_message(self, message: aio_pika.IncomingMessage) -> None:
        # await asyncio.sleep(1)
        print(message.routing_key)
        msg_raw = json.loads(message.body.decode())
        msg_cls = message_handlers[message.routing_key]["message_class"](payload=msg_raw["payload"])
        msg_cls.headers = msg_raw["headers"]
        correlation_guid.set(msg_raw["headers"]["guid"])
        handler_cls = message_handlers[message.routing_key]["cls"]()
        method = getattr(handler_cls, message_handlers[message.routing_key]["method"])
        if message_handlers[message.routing_key]["is_async"]:
            await method(msg_cls)
        else:
            method(msg_cls)
        print(f" Received async message: {message.body.decode()}")