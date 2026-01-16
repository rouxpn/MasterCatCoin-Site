import json
import requests
import os
from datetime import datetime, timezone

TOKEN_ACCOUNT = "8FEUZoTDxCQf9Pr2eWmgAHoADdMbrb4Nv1bivDeva9GW"

RPCS = [
    "https://api.mainnet-beta.solana.com",
    "https://ssc-dao.genesysgo.net",
    "https://solana-api.projectserum.com",
]

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTokenAccountBalance",
    "params": [TOKEN_ACCOUNT],
}

last_err = None

for rpc in RPCS:
    try:
        r = requests.post(rpc, json=payload, timeout=20)
        r.raise_for_status()

        data = r.json()
        if "error" in data:
            raise RuntimeError(f"RPC error: {data['error']}")

        value = data["result"]["value"]
        amount = value.get("uiAmountString") or value.get("amount")

        # 🔹 Timestamp when script runs (UTC)
        updated_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")

        out = {
            "amount": amount,
            "updated_utc": updated_utc
        }

        # ensure data/ exists
        os.makedirs("data", exist_ok=True)

        with open("data/pool.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)

        print(f"Updated using {rpc}: {out}")
        break

    except Exception as e:
        last_err = e

else:
    raise SystemExit(f"All RPCs failed. Last error: {last_err}")
    
import subprocess
from pathlib import Path
import time 

time.sleep(3)
# Resolve repo root (one level above /scripts)
REPO_ROOT = Path(__file__).resolve().parent.parent
POOL_FILE = REPO_ROOT / "data" / "pool.json"

def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.run(cmd, cwd=REPO_ROOT, check=False)

run(["git", "add", "data/pool.json"])
run(["git", "commit", "-m", "Auto-update pool.json"])
run(["git", "push"])
