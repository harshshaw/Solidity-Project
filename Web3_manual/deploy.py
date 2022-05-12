from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
with open(".\SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w")as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

# for connecting to ganache
w3 = Web3(Web3.HTTPProvider(
    "https://rinkeby.infura.io/v3/95c0c9fa53e44cbfbd1aee74a2319ed2"))
chain_id = 4
my_address = "0x7789F7aB6D3f3626b4daae8Dc43D3da1D77014Ca"
private_key = "729ab52e9065ce3247cf20850357c63c14c560f93a47286b043132e5280e6e44"


# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction

transaction = SimpleStorage.constructor().buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id,
        "from": my_address, "nonce": nonce}
)
signed_txn = w3.eth.account.sign_transaction(
    transaction, private_key=private_key)

print("Deploying contracts...")
# send this signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!")
# Working with contract, you need:
# Contract ABI
# contract Address
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# call->Simulate  making the call and getting a return value
# transact->Actually make a state change
print(simple_storage.functions.retrieve().call())
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id,
        "from": my_address, "nonce": nonce+1}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
# transaction_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)

print(simple_storage.functions.retrieve().call())
