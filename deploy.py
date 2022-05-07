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
print(private_key)

# create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

#Get the latest transaction
nonce =w3.eth.getTransactionCount(my_address)
print(nonce)
#1. Build a transaction
#2. Sign a transaction
#3. Send a transaction

transaction=SimpleStorage.constructor().buildTransaction(
    {"gasPrice": w3.eth.gas_price,"chainId":chain_id,"from":my_address,"nonce":nonce}
)
signed_txn=w3.eth.account.sign_transaction(transaction,private_key =private_key)
print(signed_txn)

#send this signed transaction
tx_hash=w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Working with contract, you need:
#Contract ABI
#contract Address