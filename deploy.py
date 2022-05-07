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
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x3C5c9555697a21651D822e872Aac3854888f7Fd7"
private_key = os.getenv("PRIVATE_KEY")


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
