import asyncio
import json
import os
from typing import Any, Awaitable, Callable, List, Optional, Union
import aio_pika

from adoption_agency_common.util import consts

class RabbitMQClient:
    _instance: Optional["RabbitMQClient"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self):
        self.callback_queue = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RabbitMQClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    async def initialize(
            self,
            quorum_queues: Optional[List[str]] = None,
    ):
        """Initializes connection and channels asynchronously."""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            self.url = os.getenv("RABBIT_CONNECTION_STRING", f"amqp://user:password@127.0.0.1:5672/")
            self.connection: Optional[aio_pika.RobustConnection] = None
            self.pub_channel: Optional[aio_pika.RobustChannel] = None
            self.sub_channel: Optional[aio_pika.RobustChannel] = None

            await self._connect()

            if quorum_queues:
                await self.declare_quorum_queues(quorum_queues)

            self._initialized = True

    async def _connect(self) -> None:
        """Connects and sets up separate channels for pub and sub."""
        self.connection = await aio_pika.connect_robust(self.url)

        # Separate read and write channels
        self.pub_channel = await self.connection.channel()
        self.sub_channel = await self.connection.channel()

    async def declare_quorum_queues(self, queue_names: List[str]) -> None:
        """Declares quorum queues using the publish channel."""
        for q_name in queue_names:
            await self.pub_channel.declare_queue(
                name=q_name, durable=True, arguments={"x-queue-type": "quorum"}
            )

    async def publish(
            self,
            queue_name: str,
            body: Union[str, dict, bytes],
            routing_key: Optional[str] = None,
    ) -> None:
        """Publishes a message asynchronously."""
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        if isinstance(body, str):
            body = body.encode("utf-8")

        target_routing_key = routing_key if routing_key else queue_name

        message = aio_pika.Message(
            body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        await self.pub_channel.default_exchange.publish(
            message, routing_key=target_routing_key
        )

    async def start_consuming(
            self,
            queue_names: List[str],
            callback: Callable[[aio_pika.IncomingMessage], Awaitable[None]],
    ) -> None:
        """Starts consuming from queues with an async callback."""
        await self.sub_channel.set_qos(prefetch_count=1)

        async def message_handler(message: aio_pika.IncomingMessage):
            async with message.process():
                await callback(message)
        await self.generate_callback_queue()
        await self.callback_queue.consume(message_handler)
        for q_name in queue_names:
            queue = await self.sub_channel.declare_queue(q_name, passive=True)

            await queue.consume(message_handler)
        print(f"[*] Async consumer listening on: {queue_names}")

    async def generate_callback_queue(self) -> str:
        queue = await self.sub_channel.declare_queue(
            name="",  # Leaving name empty asks RabbitMQ to assign a unique random name
            exclusive=True,
            auto_delete=True,
        )
        self.callback_queue = queue
        consts.service_callback_queue = queue.name
        return queue.name