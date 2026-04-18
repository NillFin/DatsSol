import requests
import time
from config import API_BASE, TOKEN

class GameAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "X-Auth-Token": TOKEN
        })

    def get_round_info(self):
        r = self.session.get(
            f"{API_BASE}/api/rounds/d596e058-a080-305b-f380-68b0753bcb9c"
        )
        r.raise_for_status()
        return r.json()

    def get_arena(self):
        while True:
            r = self.session.get(f"{API_BASE}/api/arena")

            if r.status_code == 429:
                print("⚠ Rate limited. Sleeping 1 sec...")
                time.sleep(1)
                continue

            r.raise_for_status()
            return r.json()

    def send_command(self, command=None, upgrade=None, relocate=None):
        payload = {}

        if command:
            payload["command"] = command
        if upgrade:
            payload["plantationUpgrade"] = upgrade
        if relocate:
            payload["relocateMain"] = relocate

        r = self.session.post(f"{API_BASE}/api/command", json=payload)
        r.raise_for_status()
        return r.json()

    def get_logs(self):
        r = self.session.get(f"{API_BASE}/api/logs")
        r.raise_for_status()
        return r.json()
