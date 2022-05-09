from brownie import accounts
import os


def deploy_simple_storage():
    # account = accounts[0]
    # print(account)
    account = accounts.add("freecodecamp-account")
    print(account)


def main():
    deploy_simple_storage()
