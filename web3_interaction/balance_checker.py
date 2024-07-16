from web3 import Web3
import json

def get_usdt_balance(user_wallet_address):
    # Connect to BNB Smart Chain
    opbnb_url = 'https://opbnb-mainnet-rpc.bnbchain.org'
    web3 = Web3(Web3.HTTPProvider(opbnb_url))

    # Check if connected successfully
    if not web3.is_connected():
        return "Failed to connect to BNB Smart Chain"

    # USDT Contract Address and ABI
    usdt_contract_address = web3.to_checksum_address('0x9e5aac1ba1a2e6aed6b32689dfcf62a509ca96f3')

    # Load the ABI
    with open('web3_interaction/usdt_abi_main.json', 'r') as abi_file:
        usdt_abi = json.load(abi_file)

    # Create Contract Object
    usdt_contract = web3.eth.contract(address=usdt_contract_address, abi=usdt_abi)

    # Query the decimals
    decimals = usdt_contract.functions.decimals().call()

    # Convert the user wallet address to checksum address
    address_to_check = web3.to_checksum_address(user_wallet_address)

    # Query the balance
    balance = usdt_contract.functions.balanceOf(address_to_check).call()

    # Convert balance to human-readable format
    usdt_balance = balance / 10**decimals
    return usdt_balance

# # Example usage
user_wallet_address = '0xD8436d107b7736d43682Df5a3048EC9bD2A30910'
print(get_usdt_balance(user_wallet_address))
