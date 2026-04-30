import os
import random
from uuid import uuid4

from locust import HttpUser, between, task


class SentinelUser(HttpUser):
    wait_time = between(0.001, 0.02)
    token = ""
    merchant_ids = ["merchant-a", "merchant-b", "merchant-c", "merchant-d"]
    countries = ["US", "US", "US", "GB", "SG", "IN"]
    user_count = int(os.getenv("LOCUST_USER_POOL", "1000"))

    def on_start(self):
        response = self.client.post(
            "/v1/auth/token",
            data={"username": "load-user", "password": "load-pass"},
        )
        self.token = response.json().get("access_token", "")

    @task
    def post_transaction(self):
        user_id = f"load-user-{random.randint(1, self.user_count)}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Idempotency-Key": str(uuid4()),
        }
        payload = {
            "user_id": user_id,
            "merchant_id": random.choice(self.merchant_ids),
            "amount": f"{random.uniform(10, 10000):.2f}",
            "currency": "USD",
            "country": random.choice(self.countries),
        }
        self.client.post("/v1/transactions", json=payload, headers=headers)
