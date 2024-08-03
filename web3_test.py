# from web3_interaction import Web3
# import asyncio
# import json
# import aiohttp
# from config import PORT_ID
# # connection to the Binance Smart Chain testnet
# bsc = "https://opbnb-mainnet-rpc.bnbchain.org"
# web3_interaction = Web3(Web3.HTTPProvider(bsc))
# with open('usdt_abi.json', 'r') as abi_definition:
#     contract_abi = json.load(abi_definition)
# # ensure the connection is successful
# assert web3_interaction.is_connected(), "Web3 connection failed"
#
# # contract address and ABI
# contract_address = '0xAcb68Eab051BCE90B3d76B21fd871dadd6da332b'
#
# # a contract instance
# contract = web3_interaction.eth.contract(address=contract_address, abi=contract_abi)
#
# async def handle_event(event):
#     uuid = event['args']['challengeId']
#     if len(uuid) <= 32:
#         return None
#
#     print(f"UUID: {uuid}")
#     with open('uuids.txt', 'a') as file:
#         file.write(uuid + '\n')
#     json_data = {"challenge_id": uuid}
#     async with aiohttp.ClientSession() as session:
#         async with session.post(f'http://localhost:{PORT_ID}/create_private_channel', json=json_data) as response:
#             if response.status == 200:
#                 response_data = await response.json()
#                 print("Success:", response_data)
#             else:
#                 print("Failed to make POST request:", response.status)
#
#
# async def log_loop(event_filter, poll_interval, event_name):
#     while True:
#         for event in event_filter.get_new_entries():
#             await handle_event(event)
#         await asyncio.sleep(poll_interval)

# def main():
#     creat_transaction_event = contract.events.CreateTransactionEvent.create_filter(fromBlock='latest')
#     loop = asyncio.get_event_loop()
#     try:
#         loop.run_until_complete(
#             asyncio.gather(
#                 log_loop(creat_transaction_event, 2, "CreateTransactionEvent"),
#                 )
#         )
#     finally:
#         loop.close()
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
    url = f"https://app.sidekick.fans/discord_api/create_private_channel"
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
