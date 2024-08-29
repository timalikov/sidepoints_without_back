import json
import requests
import time
import boto3
import resource
import os

client = boto3.client(
    'sqs',
    aws_access_key_id="AKIARQOJDAVZLXZGJB4Q",
    aws_secret_access_key="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",
    region_name='eu-central-1'
)

QUEUE_URL = "https://sqs.eu-central-1.amazonaws.com/104037811570/sidekick_bot_deliveries.fifo"


def receive_messages():
    messages_list = []

    try:
        response = client.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10
        )

        if 'Messages' in response:
            for message in response['Messages']:
                body = json.loads(message['Body'])
                messages_list.append(body)

                client.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
        # else:
        #     print("No messages available.")
    except Exception as e:
        print("Error receiving messages:", e)

    return messages_list

def send_message_to_endpoint(message_body, port_id):
    # url = f"http://localhost:{port_id}/create_private_channel"
    url = f"{os.getenv('WEB_APP_URL')}/discord_api/create_private_channel"
    try:
        response = requests.post(url, json=message_body)
        if response.status_code == 200:
            print(f"Message sent successfully: {message_body}")
            return True
        else:
            print(f"Failed to send message, status code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred: {e}")
    print(f"Failed to create channel for message: {message_body['channelName']}")
    return False

def process_messages():
    port_id = 2028

    while True:
        messages = receive_messages()

        for message in messages:
            send_message_to_endpoint(message, port_id)
        time.sleep(5)

def main():
    if os.path.isfile('/sys/fs/cgroup/memory/memory.limit_in_bytes'):
        with open('/sys/fs/cgroup/memory/memory.limit_in_bytes') as limit:
            mem = int(int(limit.read()) / 3)
            resource.setrlimit(resource.RLIMIT_AS, (mem, mem))
    process_messages()

if __name__ == '__main__':
    main()
