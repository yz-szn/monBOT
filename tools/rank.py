import requests
from utils.logger import log

WALLETS_URL = "https://layerhub.xyz/be-api/wallets"

HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,id;q=0.8",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "referer": "https://layerhub.xyz/search?p=monad_testnet",
    "origin": "https://layerhub.xyz",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}

COOKIES = {
    "_ga": "GA1.1.1193262269.1740292040",
    "_clck": "1cpazmp|2|ftp|0|1880",
    "_clsk": "1x2ddwr|1740424248111|3|1|e.clarity.ms/collect",
    "_ga_JDVWTH2QBN": "GS1.1.1740424220.2.1.1740424261.0.0.0",
}

def fetch_wallet_data(address):
    payload = {
        "chainId": "monad_testnet",
        "addresses": [
            {
                "searchIndex": 0,
                "address": address
            }
        ]
    }
    
    response = requests.post(WALLETS_URL, json=payload, headers=HEADERS, cookies=COOKIES)
    
    if response.status_code == 200:
        return response.json()
    else:
        log("MonadBOT", f"Error fetching data for {address}: {response.status_code} - {response.text}", "ERROR")
        return None

def display_wallet_info(address, wallet_data):
    if wallet_data and "rows" in wallet_data and len(wallet_data["rows"]) > 0:
        row = wallet_data["rows"][0]
        columns = row["columns"]

        ranking = next((col["value"] for col in columns if col["title"] == "Ranking"), "N/A")
        transaction_count = next((col["value"] for col in columns if col["title"] == "Transaction Count"), "N/A")
        interacted_contracts = next((col["value"] for col in columns if col["title"] == "Interacted Contracts"), "N/A")
        active_days = next((col["value"] for col in columns if col["title"] == "Active Days"), "N/A")
        active_months = next((col["value"] for col in columns if col["title"] == "Active Months"), "N/A")
        wallet_balance = next((col["value"] for col in columns if col["title"] == "Wallet Balance"), "N/A")
        
        log("MonadBOT", f"Wallet : {address}", "INFO")
        log("MonadBOT", f"Ranking: {ranking}", "INFO")
        log("MonadBOT", f"Transaction Count: {transaction_count}", "INFO")
        log("MonadBOT", f"Interacted Contracts: {interacted_contracts}", "INFO")
        log("MonadBOT", f"Active Days: {active_days}", "INFO")
        log("MonadBOT", f"Active Months: {active_months}", "INFO")
        log("MonadBOT", f"Wallet Balance: {wallet_balance}", "INFO")
        log("MonadBOT", "-" * 40, "INFO")
    else:
        log("MonadBOT", f"Tidak ada data untuk wallet: {address}", "WARN")

def main():
    try:
        with open("data/wallet.txt", "r") as file:
            addresses = file.read().splitlines()  
    except FileNotFoundError:
        log("MonadBOT", "File wallet.txt tidak ditemukan!", "ERROR")
        return

    for address in addresses:
        if address.strip(): 
            wallet_data = fetch_wallet_data(address.strip())
            if wallet_data:
                display_wallet_info(address.strip(), wallet_data)

if __name__ == "__main__":
    main()