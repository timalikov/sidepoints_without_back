import os
import boto3
import json

from config import TEST


class SQSClient:
    def __init__(self) -> None:
        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id="AKIARQOJDAVZLXZGJB4Q",
            aws_secret_access_key="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",
            region_name='eu-central-1'
        )
        self.queue_router = "sidekick_dev_bot_" if TEST else "sidekick_prod_bot_"
        self.queue_host = f"https://sqs.eu-central-1.amazonaws.com/104037811570/{self.queue_router}"

    def send_message(self, purchase_id: int) -> bool:
        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_host,
                DelaySeconds=10,
                MessageBody=json.dumps({'purchaseId': purchase_id})
            )
            print(f"SQS Message sent! ID: {response['MessageId']}")
            return True  
        except Exception as e:
            print(f"Failed to send message to SQS: {str(e)}")
            return False  