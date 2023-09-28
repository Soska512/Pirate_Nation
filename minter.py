import json
from web3 import Web3
from web3.auto import w3
import asyncio, random
from loguru import logger
from typing import Awaitable

rpc = 'https://rpc.ankr.com/eth'
eth_w3 = Web3(Web3.HTTPProvider(rpc))
with open('keys.txt', 'r', encoding='utf-8-sig') as file:
    private_keys = [line.strip() for line in file]
contract_address = w3.to_checksum_address('0x1EB73FEE2090fB1C20105d5Ba887e3c3bA14a17E')
abi = json.load(open('./abi.json'))
contract = eth_w3.eth.contract(contract_address, abi=abi)

async def mint(key):
    try:
        account = eth_w3.eth.account.from_key(key)
        address = w3.to_checksum_address(account.address)
        nonce = eth_w3.eth.get_transaction_count(address)
        tx = contract.functions.mint(
        '0xd2bDd497db05622576b6CB8082FB08De042987cA',
        75866352,
        0,
        [],
        address).build_transaction({
        'from':address,
        'value': eth_w3.to_wei(0.0005, 'ether'),
        'nonce': nonce})
        tx.update({'maxFeePerGas': eth_w3.eth.get_block(eth_w3.eth.get_block_number())['baseFeePerGas'] + eth_w3.eth.max_priority_fee})
        tx.update({'maxPriorityFeePerGas': eth_w3.eth.max_priority_fee})

        gasLimit = eth_w3.eth.estimate_gas(tx)
        tx.update({'gas': gasLimit})
    
        signed_tx = eth_w3.eth.account.sign_transaction(tx, key)
        raw_tx_hash = eth_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash = eth_w3.to_hex(raw_tx_hash)
        logger.success(
            f'Minted 1 NFT | TX: https://etherscan.io/tx/{tx_hash}')
    except Exception as e:
        logger.error(e)

async def main() -> None:
    tasks = []
    for private_key in private_keys:
        task = asyncio.create_task(mint(private_key))
        tasks.append(task)
        delay = random.randint(10, 20)
        time_to_sleep = delay
        logger.info(f'Sleeping {time_to_sleep} seconds...')
        await asyncio.sleep(time_to_sleep)
    await asyncio.gather(*tasks)

def start_event_loop(awaitable: Awaitable[object]) -> None:
    asyncio.run(awaitable)

if __name__ == '__main__':
    async def tracked_main():
        await main()
    start_event_loop(tracked_main())
