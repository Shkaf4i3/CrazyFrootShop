from faststream.rabbit.broker import RabbitBroker

from ..settings import settings


broker = RabbitBroker(url=settings.rabbitmq_url)
