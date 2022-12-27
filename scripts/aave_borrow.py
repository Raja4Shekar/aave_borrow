from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import interface, config, network, interface
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # withdraw_weth(account)
    # ABI
    # Address
    lending_pool = get_lending_pool()
    # Approve sending our ERC-20 tokens
    # approve_erc20(amount, lending_pool.address, erc20_address, account)
    # print("Depositing...")
    # print(erc20_address, amount, account.address, lending_pool.address)
    # tx = lending_pool.deposit(
    #     erc20_address, amount, account.address, 0, {"from": account}
    # )
    # tx.wait(1)
    # print("Deposited!")
    # how much we can borrow?
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow!")
    # DAI in terms of ETH
    eth_usd_price = get_asset_price(
        config["networks"][network.show_active()]["eth_usd_price_feed"]
    )
    print(f"the ETH/USD price is {eth_usd_price}")
    amount_dai_to_borrow = 15  # (eth_usd_price) * borrowable_eth * 0.95
    print(f"We are going to borrow {amount_dai_to_borrow} DAI")
    # Now we will borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    # repay_all(amount, lending_pool, account)
    print("You just deposited, borrowed and repayed using Aave, Brownie and Chainlink")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("Repayed!")


def get_asset_price(price_feed_address):
    # ABI
    # Address
    price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = price_feed.latestRoundData()[1]
    return float(latest_price / (10**8))


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited")
    print(f"You have {total_debt_eth} worth of ETH borrowed")
    print(f"You have {available_borrow_eth} worth of ETH that can be borrowed")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    print("Approved!")
    return tx


def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # Address
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def withdraw_weth(account):
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.withdraw(account.address, {"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print(f"Recived 0.1 ETH")
    return tx
