import os
import requests
import time
import random
from faker import Faker
from threading import Thread
from itertools import cycle
from flask import Flask

YOUR_INVITE_CODE = "dark1000knight"
fake = Faker('en_US')

def fetch_proxies():
    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000"
        response = requests.get(url, timeout=5)
        return cycle(response.text.splitlines())
    except:
        return cycle(["http://20.235.107.123:80"])

PROXIES = fetch_proxies()
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 Version/14.1 Mobile/15E148 Safari/604.1",
]
PI_API_BASE = "https://api.minepi.com/v2"  # Swap real endpoint if you’ve got it

def create_fake_account(proxy_pool):
    proxy = {"http": next(proxy_pool)}
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    phone = fake.phone_number()
    while not phone.startswith("+1") or len(phone) < 12:
        phone = fake.phone_number()
    payload = {"phone_number": phone, "invite_code": YOUR_INVITE_CODE, "device_id": fake.uuid4()}
    try:
        response = requests.post(f"{PI_API_BASE}/signup", json=payload, headers=headers, proxies=proxy, timeout=5, verify=False)
        if response.status_code == 200:
            print(f"[SUCCESS] Created: {phone}")
            return {"phone": phone, "session": fake.uuid4()}
        else:
            print(f"[FAIL] {phone} - Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] {phone}: {e}")
        return None

def mine_pi(account, proxy_pool):
    while True:
        proxy = {"http": next(proxy_pool)}
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        payload = {"phone_number": account["phone"], "session_id": account["session"]}
        try:
            response = requests.post(f"{PI_API_BASE}/mine", json=payload, headers=headers, proxies=proxy, timeout=5, verify=False)
            print(f"[MINING] {account['phone']} - Status: {response.status_code}")
        except Exception as e:
            print(f"[MINING ERROR] {account['phone']}: {e}")
        time.sleep(random.randint(82800, 90000))

def launch_swarm(num_accounts=5):  # Smaller batch for free tier
    print(f"Deploying swarm: {num_accounts} accounts...")
    accounts = []
    proxy_pool = fetch_proxies()
    for _ in range(num_accounts):
        account = create_fake_account(proxy_pool)
        if account:
            accounts.append(account)
        time.sleep(random.uniform(2, 5))
    for account in accounts:
        Thread(target=mine_pi, args=(account, proxy_pool), daemon=True).start()
    print(f"Swarm live! {len(accounts)} boosting {YOUR_INVITE_CODE}")

app = Flask(__name__)

@app.route('/')
def run():
    Thread(target=launch_swarm, args=(5,), daemon=True).start()
    return "Swarm unleashed!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses PORT env
    app.run(host="0.0.0.0", port=port)