import random
from locust import HttpUser, task, between


class NexBankCustomerUser(HttpUser):
    """
    Locust Load Testing script simulating 500 concurrent customers executing
    authentication, balance enquiries, statement requests, RAG searches, and chat turns.
    """
    wait_time = between(1, 3)

    def on_start(self):
        # Register and Login
        email = f"loadtest_{random.randint(1000, 9999)}@nexbank.in"
        reg_payload = {"email": email, "password": "Password123!", "full_name": "Load Test User", "role": "CUSTOMER"}
        self.client.post("/api/v1/auth/register", json=reg_payload)

        login_res = self.client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
        if login_res.status_code == 200:
            token = login_res.json()["data"]["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
            
            # Start Chat Session
            start_res = self.client.post("/api/v1/chat/start", json={"channel": "web"}, headers=self.headers)
            if start_res.status_code == 201:
                self.conv_id = start_res.json()["data"]["conversation_id"]

    @task(3)
    def chat_turn_balance(self):
        if hasattr(self, "conv_id"):
            self.client.post("/api/v1/chat/message", json={"conversation_id": self.conv_id, "message": "Check my savings balance"}, headers=self.headers)

    @task(2)
    def search_knowledge(self):
        self.client.post("/api/v1/knowledge/search", json={"query": "What is the interest rate for savings account?", "top_k": 5})

    @task(1)
    def check_health(self):
        self.client.get("/api/v1/health")
