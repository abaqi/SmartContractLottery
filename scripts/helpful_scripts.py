from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    )
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local", "ganache-locak"]

def get_account(index=None, id=None):
    #accounts[0] -> Brownie's ganache accounts
    #accounts.add("env")
    #accounts.load("id")
    if index:
        return accounts[index]
    elif id:
        return accounts.load(id)
    elif network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0] 
    else:
        return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}


def get_contract(contract_name):
    """
    This will grab the contract addresses from teh brownie config if defined otherwise if will deploy a ock 
    version of that contract and return that mock contract

    Args: contract name - string

    Returns: brownie.network.contract.ProjectContract: the most recent ly deployed version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            # Checking how many mockv3 aggregators have been deployed
            deploy_mocks()
        # grab teh most recent deployment of teh mock vs agg contract
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address and ABI
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)

    return contract

DECIMALS = 8
STARTING_PRICE = 200000000000

def deploy_mocks(decimals=DECIMALS, initial_value=STARTING_PRICE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from":get_account()})
    link_token = LinkToken.deploy({"from":account})
    VRFCoordinatorMock.deploy(link_token.address, {"from":account})
    print("Mocks Deplouyed")

def fund_with_link(contract_address, account= None, link_token=None, amount=100000000000000000): #0.1 LINK
    """You can work with contracts but sometimes will have to work with interfaces"""
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address) # Another way to interact with contracts that already exist
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund Contract!")
    return tx
