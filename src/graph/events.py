from asyncio import CancelledError

import aio_pika
import ujson
from aio_pika import Queue
from fastapi import FastAPI


async def event_consumer(app: FastAPI, exchange_name: str = "events", queue_name: str = "events"):
    app.logger.info("Start event consumer")  # type: ignore

    exchange = await app.state.rabbitmq_channel.declare_exchange(exchange_name, aio_pika.ExchangeType.FANOUT)
    queue: Queue = await app.state.rabbitmq_channel.declare_queue(queue_name, durable=True)
    await queue.bind(exchange)

    try:
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = message.body.decode("utf-8")
                    if message.content_type == "application/json":
                        try:
                            body = ujson.loads(body)
                        except ValueError:
                            continue

                    app.logger.info("Receive message from queue", message=body)  # type: ignore

    except CancelledError:
        app.logger.info("Shutdown event consumer")  # type: ignore
