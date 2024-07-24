import os
import sys

from fastapi import FastAPI, HTTPException
from app.requests.UserEventRequest import UserEventRequest
import pika
import threading
from app.controllers.MessageController import handleUsersEvent
import asyncio
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# RabbitMQ connection parameters
rabbitmq_host = os.getenv('RABBITMQ_DEFAULT_HOST')
queue_name = os.getenv('RABBITMQ_DEFAULT_QUEUE')
rabbitmq_user = os.getenv('RABBITMQ_DEFAULT_USER')
rabbitmq_password = os.getenv('RABBITMQ_DEFAULT_PASS')


class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def get_channel(self):
        if self.channel is None or self.channel.is_closed:
            self.connect()
        return self.channel

    def close(self):
        if self.connection:
            self.connection.close()

    async def send_message_to_rabbitmq(self, message):
        try:
            channel = self.get_channel()

            channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)  # Make the message persistent
            )
            return {"message": "Message sent to RabbitMQ"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error sending message to RabbitMQ: {e}")

    def consume_message(self, channel, method, properties, body):
        try:
            # Convert body to string and then load JSON
            body_str = body.decode('utf-8')
            print(f"Received message: {body_str}")

            # Deserialize JSON to UserEventRequest
            item = UserEventRequest.parse_raw(body_str)

            # Call the async handler function
            result = handleUsersEvent(item)

            # Print or log the result of handling
            print(f"Result: {result}")

        except Exception as e:
            print(f"Error processing message: {e}")

    def start_consuming(self):
        channel = self.get_channel()
        channel.basic_consume(queue=queue_name, on_message_callback=self.consume_message, auto_ack=True)
        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
