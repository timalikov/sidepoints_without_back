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