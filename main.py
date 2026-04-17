import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN", "").strip()
WEBEX_API = "https://webexapis.com/v1"

def webex_headers():
    return {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"INCOMING {request.method} {request.url.path}", flush=True)
    response = await call_next(request)
    print(f"COMPLETED {request.method} {request.url.path} -> {response.status_code}", flush=True)
    return response

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/webhook")
def webhook_get():
    print("GET /webhook hit", flush=True)
    return {"status": "webhook route exists"}

@app.post("/webhook")
async def webhook(request: Request):
    print("POST /webhook hit", flush=True)
    body = await request.json()
    print("WEBHOOK BODY:", body, flush=True)

    resource = body.get("resource")
    event = body.get("event")
    data = body.get("data", {})

    if resource == "messages" and event == "created":
        room_id = data.get("roomId")
        person_email = data.get("personEmail", "")
        print(f"Message event from: {person_email} room: {room_id}", flush=True)

        # Pull full message details
        message_id = data.get("id")
        msg = requests.get(
            f"{WEBEX_API}/messages/{message_id}",
            headers=webex_headers(),
            timeout=30,
        )
        print("GET MESSAGE STATUS:", msg.status_code, flush=True)
        print("GET MESSAGE BODY:", msg.text, flush=True)

        if msg.ok and room_id:
            msg_json = msg.json()
            text = (msg_json.get("text") or "").strip()
            print("MESSAGE TEXT:", text, flush=True)

            send = requests.post(
                f"{WEBEX_API}/messages",
                headers=webex_headers(),
                json={
                    "roomId": room_id,
                    "text": f"I received: {text}"
                },
                timeout=30,
            )
            print("SEND MESSAGE STATUS:", send.status_code, flush=True)
            print("SEND MESSAGE BODY:", send.text, flush=True)

    return JSONResponse({"status": "received"})
