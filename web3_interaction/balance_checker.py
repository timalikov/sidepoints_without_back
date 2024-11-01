from decimal import Decimal
from typing import Literal

from config import (
    OPBNB_URL,
    USDT_ADDRESS,
    ABI_FILE_PATH
)

from web3 import Web3
import json


def get_usdt_balance(user_wallet_address: str) -> (
    int | Decimal | Literal['Failed to connect to BNB Smart Chain']
):
    # Connect to BNB Smart Chain
    web3 = Web3(Web3.HTTPProvider(OPBNB_URL))
    if not web3.is_connected():
        return "Failed to connect to BNB Smart Chain"

    usdt_contract_address = web3.to_checksum_address(USDT_ADDRESS)
    with open(ABI_FILE_PATH, 'r') as abi_file:
        usdt_abi = json.load(abi_file)
    usdt_contract = web3.eth.contract(address=usdt_contract_address, abi=usdt_abi)
    address_to_check = web3.to_checksum_address(user_wallet_address)
    usdt_balance = usdt_contract.functions.balanceOf(address_to_check).call()
    usdt_balance_formatted = web3.from_wei(usdt_balance, 'ether')
    return usdt_balance_formatted
