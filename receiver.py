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


QUEUE_URL = "https://sqs.eu-central-1.amazonaws.com/104037811570/sidekick_bot_deliveries.fifo"
QUEUE_NOTIFICATION_URL = "https://sqs.eu-central-1.amazonaws.com/104037811570/sidekick_bot_new_purchases.fifo"
QUEUE_BOOST_NOTIFICATION = "https://sqs.eu-central-1.amazonaws.com/104037811570/sidekick_bot_boost_messages.fifo"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Receiver:
    
    def __init__(self) -> None:
        self.client = boto3.client(
            'sqs',
            aws_access_key_id="AKIARQOJDAVZLXZGJB4Q",
            aws_secret_access_key="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",
            region_name='eu-central-1'
        )
        self.queue_host = "https://sqs.eu-central-1.amazonaws.com/"
        self.queues = {}

    def receive_messages(self, queue: str):
        messages_list = []
        try:
            response = self.client.receive_message(
                QueueUrl=queue,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=10
            )
            if 'Messages' in response:
                print(f"{bcolors.OKGREEN}FIND MESSAGE: {bcolors.ENDC}{queue}")
                for message in response['Messages']:
                    body = json.loads(message['Body'])
                    messages_list.append(body)
                    self.client.delete_message(
                        QueueUrl=queue,
                        ReceiptHandle=message['ReceiptHandle']
                    )
        except Exception as e:
            print("Error receiving messages:", e)

        return messages_list

    def process_messages(self, queue: str, callable_func: Callable):
        while True:
            messages = self.receive_messages(queue)
            for message in messages:
                callable_func(message)
            time.sleep(5)

    def receive(self, queue: str):
        def decorator(func):
            self.queues[self.queue_host + queue] = func
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
            return wrapper
        return decorator
    
    def start(self) -> None:
        if os.path.isfile('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
            with open('/sys/fs/cgroup/memory/memory.limit_in_bytes') as limit:
                mem = int(int(limit.read()) / 3)
                resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
        tasks = [
            threading.Thread(
                target=self.process_messages,
                args=( q, func)
            )
            for q, func in self.queues.items()
        ]
        print("Tasks started!")
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()


# ===========================================================================
# ROUTERS ===================================================================

sqs_receiver = Receiver()

def send_request(url: str, message_body: dict) -> requests.Response:
    try:
        response = requests.post(url, json=message_body)
        if response.status_code == 200:
            print(f"{bcolors.OKGREEN}[200]{bcolors.ENDC}: {url}")
            return True
        else:
            print(f"{bcolors.FAIL}[{response.status_code}]{bcolors.ENDC} {url} \n{response.text}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    return False


@sqs_receiver.receive(queue="104037811570/sidekick_bot_deliveries.fifo")
def send_message_to_endpoint(message_body):
    url = f"{os.getenv('WEB_APP_URL')}/discord_api/create_private_channel"
    _ = send_request(url, message_body)


@sqs_receiver.receive(queue="104037811570/sidekick_bot_new_purchases.fifo")
def send_notification_to_endpoint(message_body):
    url = f"{os.getenv('WEB_APP_URL')}/discord_api/notification"
    _ = send_request(url, message_body)


@sqs_receiver.receive(queue="104037811570/sidekick_bot_boost_messages.fifo")
def send_boost_notification(message_body):
    url = f"{os.getenv('WEB_APP_URL')}/discord_api/boost"
    print(message_body)
    _ = send_request(url, message_body)


def main():
    sqs_receiver.start()

if __name__ == '__main__':
    main()
