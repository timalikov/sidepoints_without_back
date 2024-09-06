from typing import Callable
import json
import requests
import time
import boto3
import resource
import os
import threading
from dotenv import load_dotenv
load_dotenv()

client = boto3.client(
    'sqs',
    aws_access_key_id="AKIARQOJDAVZLXZGJB4Q",
    aws_secret_access_key="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",
    region_name='eu-central-1'
)

QUEUE_URL = "https://sqs.eu-central-1.amazonaws.com/104037811570/sidekick_bot_deliveries.fifo"
QUEUE_NOTIFICATION_URL = "https://sqs.eu-central-1.amazonaws.com/104037811570/sidekick_bot_new_purchases.fifo"


def send_request(url: str, message_body: dict) -> requests.Response:
    try:
        response = requests.post(url, json=message_body)
        if response.status_code == 200:
            print(f"Message sent successfully: {message_body}")
            return True
        else:
            print(f"Failed to send message, status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    print(f"Failedmessage: {message_body}")
    return False


def receive_messages(queue: str):
    messages_list = []
    try:
        response = client.receive_message(
            QueueUrl=queue,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10
        )
        if 'Messages' in response:
            print(f"FIND MESSAGE: {queue} ::: {response}")
            for message in response['Messages']:
                body = json.loads(message['Body'])
                messages_list.append(body)
                client.delete_message(
                    QueueUrl=queue,
                    ReceiptHandle=message['ReceiptHandle']
                )
    except Exception as e:
        print("Error receiving messages:", e)

    return messages_list


def send_message_to_endpoint(message_body):
    url = f"{os.getenv('WEB_APP_URL')}/discord_api/create_private_channel"
    _ = send_request(url, message_body)


def send_notification_to_endpoint(message_body):
    url = f"{os.getenv('WEB_APP_URL')}/discord_api/notification"
    _ = send_request(url, message_body)


def process_messages(queue: str, callable_func: Callable):
    port_id = 2028

    while True:
        messages = receive_messages(queue)
        for message in messages:
            callable_func(message)
        time.sleep(5)

def main():
    if os.path.isfile('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
        with open('/sys/fs/cgroup/memory/memory.limit_in_bytes') as limit:
            mem = int(int(limit.read()) / 3)
            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
    tasks = [
        threading.Thread(target=process_messages, args=(QUEUE_URL, send_message_to_endpoint)),
        threading.Thread(target=process_messages, args=(QUEUE_NOTIFICATION_URL, send_notification_to_endpoint))
    ]
    print("Tasks started!")
    for task in tasks:
        task.start()
    for task in tasks:
        task.join()

if __name__ == '__main__':
    main()
