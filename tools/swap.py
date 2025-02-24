import time
from web3 import Web3
from utils.logger import log
from colorama import Fore, Style, init

init(autoreset=True)

RPC_URL = 'https://testnet-rpc.monad.xyz/'
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    log("MonadBOT", "Gagal terhubung ke Monad Testnet RPC! Periksa koneksi Anda.", "ERROR")
    exit()

CHAIN_ID = web3.eth.chain_id
log("MonadBOT", f"Terhubung ke Monad Testnet! Chain ID: {CHAIN_ID}", "INFO")

WMON = Web3.to_checksum_address("0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701")

def send_transaction_with_retry(transaction, private_key, max_retries=10, delay=10):
    retries = 0
    while retries < max_retries:
        try:
            nonce = web3.eth.get_transaction_count(transaction['from'], 'pending')
            transaction['nonce'] = nonce
            transaction['gas'] = web3.eth.estimate_gas(transaction)
            signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction) 
            log("MonadBOT", f"Transaksi berhasil! TX Hash: {tx_hash.hex()}", "SUCCESS")
            return tx_hash
        except Exception as e:
            if 'nonce too low' in str(e):
                log("MonadBOT", "Nonce terlalu rendah, mencoba lagi...", "WARN")
                time.sleep(5)
                continue
            log("MonadBOT", f"Gagal mengirim transaksi: {e}. Mencoba ulang dalam {delay} detik...", "ERROR")
            time.sleep(delay)
            retries += 1
    log("MonadBOT", "Gagal mengirim transaksi setelah beberapa kali percobaan.", "ERROR")
    return None

def deposit_mon_to_wmon(wallet, amount_in_mon, gas_price):
    try:
        amount_in_wei = web3.to_wei(amount_in_mon, 'ether')
        deposit_function_selector = web3.keccak(text="deposit()")[:4]
        txn = {
            'from': Web3.to_checksum_address(wallet.address),
            'to': WMON,
            'value': amount_in_wei,
            'gasPrice': web3.to_wei(gas_price, 'gwei'),
            'nonce': web3.eth.get_transaction_count(wallet.address, 'pending'),
            'chainId': CHAIN_ID,
            'data': deposit_function_selector.hex()
        }
        send_transaction_with_retry(txn, wallet.key)
        log("MonadBOT", f"[{wallet.address}] Berhasil deposit MON ke WMON", "SUCCESS")
        time.sleep(5)
        withdraw_wmon_to_mon(wallet, amount_in_wei, gas_price)
    except Exception as error:
        log("MonadBOT", f"[{wallet.address}] Gagal deposit MON ke WMON: {error}", "ERROR")

def withdraw_wmon_to_mon(wallet, amount_in_wei, gas_price):
    try:
        amount_in_wei = int(amount_in_wei)
        withdraw_function_selector = web3.keccak(text="withdraw(uint256)")[:4]
        amount_padded = amount_in_wei.to_bytes(32, 'big')
        data = withdraw_function_selector + amount_padded
        txn = {
            'from': Web3.to_checksum_address(wallet.address),
            'to': WMON,
            'gasPrice': web3.to_wei(gas_price, 'gwei'),
            'nonce': web3.eth.get_transaction_count(wallet.address, 'pending'),
            'chainId': CHAIN_ID,
            'data': data.hex()
        }
        send_transaction_with_retry(txn, wallet.key)
        log("MonadBOT", f"[{wallet.address}] Berhasil withdraw WMON ke MON sebanyak {amount_in_wei} Wei", "SUCCESS")
        time.sleep(5) 
    except Exception as error:
        log("MonadBOT", f"[{wallet.address}] Gagal withdraw WMON ke MON: {error}", "ERROR")

def process_wallets(wallets, amount, transactions_per_wallet, gas_price):
    for wallet in wallets:
        log("MonadBOT", f"Memulai transaksi untuk wallet: {wallet.address}", "INFO")
        for i in range(transactions_per_wallet):
            log("MonadBOT", f"Transaksi {i + 1} dari {transactions_per_wallet} untuk {wallet.address}", "INFO")
            deposit_mon_to_wmon(wallet, amount, gas_price)

def load_wallets():
    try:
        with open("data/pk.txt", "r") as file:
            private_keys = [line.strip() for line in file.readlines() if line.strip()]
        return [web3.eth.account.from_key(pk) for pk in private_keys]
    except Exception as e:
        log("MonadBOT", f"Gagal memuat wallet: {e}", "ERROR")
        return []

async def run():
    amount = float(input("\nMasukkan jumlah MON yang ingin di-deposit ke WMON: "))
    if amount <= 0:
        log("MonadBOT", "Masukkan jumlah yang valid!", "ERROR")
        return

    transactions = int(input("\nMasukkan jumlah transaksi per wallet: "))
    if transactions <= 0:
        log("MonadBOT", "Masukkan jumlah transaksi yang valid!", "ERROR")
        return

    # Set gas price tetap ke 52 Gwei
    gas_price = 52  # Gas price diatur ke 52 Gwei
    log("MonadBOT", f"Gas price diatur ke {gas_price} Gwei", "INFO")

    wallets = load_wallets()
    if not wallets:
        log("MonadBOT", "Tidak ada wallet ditemukan di data/pk.txt!", "ERROR")
        return

    log("MonadBOT", "Memulai deposit dan withdraw...", "INFO")
    process_wallets(wallets, amount, transactions, gas_price)
    log("MonadBOT", "Semua transaksi selesai!", "SUCCESS")