from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def get_weth():
    """
    Mints WETH by depositing ETH.
    """
    # ABI
    # Address
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print(f"Recived 0.1 WETH")
    return tx


def main():
    get_weth()
    pass
