from fastapi import FastAPI, Request
import requests
import os
import json

app = FastAPI()

WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN", "")
REVIO_PSA_BASE_URL = os.getenv("REVIO_PSA_BASE_URL", "https://api.psarev.io")
REVIO_PSA_API_KEY = os.getenv("REVIO_PSA_API_KEY", "")
REVIO_PSA_HOST = os.getenv("REVIO_PSA_HOST", "")

WEBEX_HEADERS = {
    "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
    "Content-Type": "application/json",
}

BOT_PERSON_ID = None


@app.get("/")
def home():
    return {"ok": True, "message": "Webex opportunities bot is running"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/webex/webhook")
def webhook_test():
    return {"ok": True, "message": "Webhook route exists"}


def get_me():
    global BOT_PERSON_ID
    r = requests.get(
        "https://webexapis.com/v1/people/me",
        headers={"Authorization": f"Bearer {WEBEX_BOT_TOKEN}"},
        timeout=30,
    )
    print(f"[DEBUG] get_me status: {r.status_code}")
    print(f"[DEBUG] get_me response: {r.text[:1000]}")
    r.raise_for_status()
    me = r.json()
    BOT_PERSON_ID = me.get("id")
    return me


def post_webex_message(room_id: str, text: str):
    r = requests.post(
        "https://webexapis.com/v1/messages",
        headers=WEBEX_HEADERS,
        json={"roomId": room_id, "text": text},
        timeout=30,
    )
    print(f"[DEBUG] Post message status: {r.status_code}")
    print(f"[DEBUG] Post message response: {r.text[:1000]}")
    r.raise_for_status()
    return r.json()


def post_webex_card(room_id: str, fallback_text: str, card_content: dict):
    payload = {
        "roomId": room_id,
        "text": fallback_text,
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_content,
            }
        ],
    }
    r = requests.post(
        "https://webexapis.com/v1/messages",
        headers=WEBEX_HEADERS,
        json=payload,
        timeout=30,
    )
    print(f"[DEBUG] Post card status: {r.status_code}")
    print(f"[DEBUG] Post card response: {r.text[:1000]}")
    r.raise_for_status()
    return r.json()


def post_opportunity_menu_card(room_id: str):
    card_content = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "body": [
            {
                "type": "TextBlock",
                "text": "Bullfrog Opportunities",
                "weight": "Bolder",
                "size": "Large",
            },
            {
                "type": "TextBlock",
                "text": "Choose which opportunity action you want to continue with.",
                "wrap": True,
                "spacing": "Small",
            },
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Create Opportunity",
                "data": {"action": "show_create_opportunity"},
            },
            {
                "type": "Action.Submit",
                "title": "Update Opportunity",
                "data": {"action": "show_update_opportunity"},
            },
            {
                "type": "Action.Submit",
                "title": "Delete Opportunity",
                "data": {"action": "show_delete_opportunity"},
            },
        ],
    }
    return post_webex_card(room_id, "Opportunity menu", card_content)



def post_create_opportunity_card(room_id: str):
    card_content = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "body": [
            {"type": "TextBlock", "text": "Create Opportunity", "weight": "Bolder", "size": "Large"},
            {"type": "Input.Text", "id": "name", "label": "Opportunity Name"},
            {"type": "Input.Text", "id": "customer_id", "label": "Customer ID"},
            {"type": "Input.Text", "id": "amount", "label": "Amount"},
            {"type": "Input.Text", "id": "stage_id", "label": "Stage ID"},
            {"type": "Input.Text", "id": "status_id", "label": "Status ID"},
            {"type": "Input.Text", "id": "type_id", "label": "Type ID"},
            {"type": "Input.Text", "id": "source_id", "label": "Source ID"},
            {"type": "Input.Text", "id": "notes", "label": "Notes", "isMultiline": True},
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Create",
                "data": {"action": "submit_create_opportunity"},
            }
        ],
    }
    return post_webex_card(room_id, "Create opportunity form", card_content)



def post_update_opportunity_card(room_id: str):
    card_content = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "body": [
            {"type": "TextBlock", "text": "Update Opportunity", "weight": "Bolder", "size": "Large"},
            {"type": "Input.Text", "id": "opportunity_id", "label": "Opportunity ID"},
            {"type": "Input.Text", "id": "name", "label": "Opportunity Name"},
            {"type": "Input.Text", "id": "customer_id", "label": "Customer ID"},
            {"type": "Input.Text", "id": "amount", "label": "Amount"},
            {"type": "Input.Text", "id": "stage_id", "label": "Stage ID"},
            {"type": "Input.Text", "id": "status_id", "label": "Status ID"},
            {"type": "Input.Text", "id": "type_id", "label": "Type ID"},
            {"type": "Input.Text", "id": "source_id", "label": "Source ID"},
            {"type": "Input.Text", "id": "notes", "label": "Notes", "isMultiline": True},
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Update",
                "data": {"action": "submit_update_opportunity"},
            }
        ],
    }
    return post_webex_card(room_id, "Update opportunity form", card_content)



def post_delete_opportunity_card(room_id: str):
    card_content = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.3",
        "body": [
            {"type": "TextBlock", "text": "Delete Opportunity", "weight": "Bolder", "size": "Large"},
            {"type": "Input.Text", "id": "opportunity_id", "label": "Opportunity ID"},
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Delete",
                "data": {"action": "submit_delete_opportunity"},
            }
        ],
    }
    return post_webex_card(room_id, "Delete opportunity form", card_content)



def get_message(message_id: str):
    r = requests.get(
        f"https://webexapis.com/v1/messages/{message_id}",
        headers={"Authorization": f"Bearer {WEBEX_BOT_TOKEN}"},
        timeout=30,
    )
    print(f"[DEBUG] Get message status: {r.status_code}")
    print(f"[DEBUG] Get message response: {r.text[:1000]}")
    r.raise_for_status()
    return r.json()



def get_attachment_action(action_id: str):
    r = requests.get(
        f"https://webexapis.com/v1/attachment/actions/{action_id}",
        headers={"Authorization": f"Bearer {WEBEX_BOT_TOKEN}"},
        timeout=30,
    )
    print(f"[DEBUG] Attachment action status: {r.status_code}")
    print(f"[DEBUG] Attachment action response: {r.text[:1000]}")
    r.raise_for_status()
    return r.json()



def get_revio_psa_token():
    url = f"{REVIO_PSA_BASE_URL}/api/v1/auth/api-key/exchange"
    payload = {"apiKey": REVIO_PSA_API_KEY}

    r = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    print(f"[DEBUG] PSA token exchange status: {r.status_code}")
    print(f"[DEBUG] PSA token exchange response: {r.text[:2000]}")
    r.raise_for_status()

    data = r.json()
    token = data.get("data", {}).get("token")
    if not token:
        raise Exception("No PSA token returned from API key exchange")

    return token



def get_psa_headers():
    token = get_revio_psa_token()
    return {
        "Authorization": f"Bearer {token}",
        "X-Revio-Host": REVIO_PSA_HOST,
        "Content-Type": "application/json",
    }



def clean_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value



def build_opportunity_payload(inputs: dict):
    payload = {
        "name": clean_value(inputs.get("name")),
        "customer_id": clean_value(inputs.get("customer_id")),
        "amount": clean_value(inputs.get("amount")),
        "stage_id": clean_value(inputs.get("stage_id")),
        "status_id": clean_value(inputs.get("status_id")),
        "type_id": clean_value(inputs.get("type_id")),
        "source_id": clean_value(inputs.get("source_id")),
        "notes": clean_value(inputs.get("notes")),
    }
    return {k: v for k, v in payload.items() if v is not None}



def create_revio_opportunity(inputs: dict):
    headers = get_psa_headers()
    payload = build_opportunity_payload(inputs)
    url = f"{REVIO_PSA_BASE_URL}/billing/api/v1/opportunities"

    print(f"[DEBUG] Create opportunity URL: {url}")
    print(f"[DEBUG] Create opportunity payload: {json.dumps(payload)}")

    r = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"[DEBUG] Create opportunity status: {r.status_code}")
    print(f"[DEBUG] Create opportunity response: {r.text[:4000]}")

    if not r.ok:
        raise Exception(f"Rev.io create opportunity {r.status_code}: {r.text[:1500]}")

    return r.json() if r.text.strip() else {"ok": True}



def update_revio_opportunity(opportunity_id: str, inputs: dict):
    headers = get_psa_headers()
    payload = build_opportunity_payload(inputs)
    url = f"{REVIO_PSA_BASE_URL}/billing/api/v1/opportunities/{opportunity_id}"

    print(f"[DEBUG] Update opportunity URL: {url}")
    print(f"[DEBUG] Update opportunity payload: {json.dumps(payload)}")

    r = requests.put(url, headers=headers, json=payload, timeout=30)
    print(f"[DEBUG] Update opportunity status: {r.status_code}")
    print(f"[DEBUG] Update opportunity response: {r.text[:4000]}")

    if not r.ok:
        raise Exception(f"Rev.io update opportunity {r.status_code}: {r.text[:1500]}")

    return r.json() if r.text.strip() else {"ok": True}



def delete_revio_opportunity(opportunity_id: str):
    headers = get_psa_headers()
    url = f"{REVIO_PSA_BASE_URL}/billing/api/v1/opportunities/{opportunity_id}"

    print(f"[DEBUG] Delete opportunity URL: {url}")

    r = requests.delete(url, headers=headers, timeout=30)
    print(f"[DEBUG] Delete opportunity status: {r.status_code}")
    print(f"[DEBUG] Delete opportunity response: {r.text[:4000]}")

    if not r.ok:
        raise Exception(f"Rev.io delete opportunity {r.status_code}: {r.text[:1500]}")

    return {"ok": True}


@app.on_event("startup")
def startup_event():
    try:
        get_me()
        print(f"[DEBUG] BOT_PERSON_ID: {BOT_PERSON_ID}")
    except Exception as e:
        print(f"[ERROR] Failed to get bot identity on startup: {e}")


@app.post("/webex/webhook")
async def webex_webhook(request: Request):
    global BOT_PERSON_ID

    body = await request.json()
    print(f"[DEBUG] Incoming webhook body: {json.dumps(body)}")

    resource = body.get("resource")
    event = body.get("event")
    data = body.get("data", {})

    if event != "created":
        return {"ok": True, "ignored": True}

    if not BOT_PERSON_ID:
        get_me()

    if resource == "messages":
        message_id = data.get("id")
        room_id = data.get("roomId")
        sender_id = data.get("personId")

        if sender_id == BOT_PERSON_ID:
            print("[DEBUG] Ignoring bot's own message")
            return {"ok": True, "ignored": "self_message"}

        if not message_id or not room_id:
            return {"ok": False, "error": "Missing message ID or room ID"}

        msg = get_message(message_id)
        text = (msg.get("text") or "").strip().lower()

        if text in ["bot opprotunities", "bot opportunities"]:
            post_opportunity_menu_card(room_id)
        else:
            post_webex_message(
                room_id,
                "Say 'Bot opprotunities' to manage opportunities.",
            )

        return {"ok": True, "type": "message"}

    if resource == "attachmentActions":
        action_id = data.get("id")
        if not action_id:
            return {"ok": False, "error": "Missing action ID"}

        action = get_attachment_action(action_id)
        inputs = action.get("inputs", {})
        room_id = action.get("roomId")
        action_name = inputs.get("action")

        if not room_id:
            return {"ok": False, "error": "Missing roomId"}

        if action_name == "show_create_opportunity":
            post_create_opportunity_card(room_id)
            return {"ok": True, "type": "attachmentAction", "action": action_name}

        if action_name == "show_update_opportunity":
            post_update_opportunity_card(room_id)
            return {"ok": True, "type": "attachmentAction", "action": action_name}

        if action_name == "show_delete_opportunity":
            post_delete_opportunity_card(room_id)
            return {"ok": True, "type": "attachmentAction", "action": action_name}

        if action_name == "submit_create_opportunity":
            try:
                result = create_revio_opportunity(inputs)
                opportunity_id = result.get("id") or result.get("opportunity_id") or "created"
                post_webex_message(room_id, f"Opportunity created successfully. Opportunity ID: {opportunity_id}")
                return {"ok": True, "type": "attachmentAction", "result": result}
            except Exception as e:
                print(f"[ERROR] Rev.io create opportunity failed: {e}")
                post_webex_message(room_id, f"Opportunity creation failed. Error: {str(e)[:400]}")
                return {"ok": False, "error": str(e)}

        if action_name == "submit_update_opportunity":
            opportunity_id = clean_value(inputs.get("opportunity_id"))
            if not opportunity_id:
                post_webex_message(room_id, "Update failed. Opportunity ID is required.")
                return {"ok": False, "error": "Missing opportunity ID"}

            try:
                result = update_revio_opportunity(opportunity_id, inputs)
                post_webex_message(room_id, f"Opportunity {opportunity_id} updated successfully.")
                return {"ok": True, "type": "attachmentAction", "result": result}
            except Exception as e:
                print(f"[ERROR] Rev.io update opportunity failed: {e}")
                post_webex_message(room_id, f"Opportunity update failed. Error: {str(e)[:400]}")
                return {"ok": False, "error": str(e)}

        if action_name == "submit_delete_opportunity":
            opportunity_id = clean_value(inputs.get("opportunity_id"))
            if not opportunity_id:
                post_webex_message(room_id, "Delete failed. Opportunity ID is required.")
                return {"ok": False, "error": "Missing opportunity ID"}

            try:
                delete_revio_opportunity(opportunity_id)
                post_webex_message(room_id, f"Opportunity {opportunity_id} deleted successfully.")
                return {"ok": True, "type": "attachmentAction", "deleted": opportunity_id}
            except Exception as e:
                print(f"[ERROR] Rev.io delete opportunity failed: {e}")
                post_webex_message(room_id, f"Opportunity delete failed. Error: {str(e)[:400]}")
                return {"ok": False, "error": str(e)}

        post_webex_message(room_id, "Unknown action received.")
        return {"ok": False, "error": f"Unknown action: {action_name}"}

    return {"ok": True, "ignored": True}
