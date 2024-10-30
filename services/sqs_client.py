import uuid
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
        self.queue_router = "sidekick_dev_" if TEST else "sidekick_prod_"
        self.queue_host = f"https://sqs.eu-central-1.amazonaws.com/104037811570/{self.queue_router}"

    def send_message(self, purchase_id: int) -> bool:
        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_host + "refund",
                DelaySeconds=10,
                MessageBody=json.dumps({'purchaseId': purchase_id})
            )
            print(f"SQS Message sent! ID: {response['MessageId']}")
            return True  
        except Exception as e:
            print(f"Failed to send message to SQS: {str(e)}")
            return False 
        
    def send_order_confirm_message(self, order_id: uuid.UUID, service_id: int) -> bool:
        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_host + "be_orders_kicker_accepts",
                DelaySeconds=10,
                MessageBody=json.dumps(
                    {
                        'orderId': str(order_id),
                        'serviceId': str(service_id)
                    }
                )
            )
            print(f"SQS Message sent! ID: {response['MessageId']}")
            return True  
        except Exception as e:
            print(f"Failed to send message to SQS: {str(e)}")
            return False
        
    def send_task_records_message(self, discord_id: int, type: str) -> bool:
        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_host + "discord_task_records",
                DelaySeconds=10,
                MessageBody=json.dumps({
                    'discordId': discord_id,
                    'type': type
                    }
                )
            )
            print(f"SQS Message sent! ID: {response['MessageId']} to {self.queue_host + 'discord_task_records'}")
            return True  
        except Exception as e:
            print(f"Failed to send message to SQS: {str(e)}")
            return False