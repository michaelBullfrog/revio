import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# -----------------------------
# Environment variables
# -----------------------------
WEBEX_BOT_TOKEN = os.getenv("WEBEX_BOT_TOKEN", "").strip()

REVIO_API_KEY = os.getenv("REVIO_API_KEY", "").strip()
REVIO_AUTH_URL = "https://api.psarev.io/api/v1/auth/api-key/exchange"
REVIO_BASE_URL = "https://api.psarev.io"
REVIO_HOST = os.getenv("REVIO_HOST", "bullfrog.psarev.io").strip()

WEBEX_API = "https://webexapis.com/v1"

if not WEBEX_BOT_TOKEN:
    print("WARNING: WEBEX_BOT_TOKEN is not set.")
if not REVIO_API_KEY:
    print("WARNING: REVIO_API_KEY is not set.")


# -----------------------------
# Webex helpers
# -----------------------------
def webex_headers() -> dict:
    return {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json",
    }


def send_webex_message(room_id: str, text: str = None, card: dict = None) -> dict:
    payload = {"roomId": room_id}

    if text:
        payload["text"] = text

    if card:
        payload["attachments"] = [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card,
            }
        ]

    response = requests.post(
        f"{WEBEX_API}/messages",
        headers=webex_headers(),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_webex_message(message_id: str) -> dict:
    response = requests.get(
        f"{WEBEX_API}/messages/{message_id}",
        headers=webex_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_attachment_action(action_id: str) -> dict:
    response = requests.get(
        f"{WEBEX_API}/attachment/actions/{action_id}",
        headers=webex_headers(),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# -----------------------------
# Rev.io helpers
# -----------------------------
def get_revio_jwt() -> str:
    response = requests.post(
        REVIO_AUTH_URL,
        headers={"Content-Type": "application/json"},
        json={"apiKey": REVIO_API_KEY},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    token = data.get("data", {}).get("token")
    if not token:
        raise ValueError(f"Token not found in Rev.io auth response: {data}")

    return token


def revio_headers() -> dict:
    token = get_revio_jwt()
    return {
        "Authorization": f"Bearer {token}",
        "X-Revio-Host": REVIO_HOST,
        "Content-Type": "application/json",
    }


def create_opportunity(payload: dict) -> requests.Response:
    url = f"{REVIO_BASE_URL}/billing/api/v1/opportunities"
    return requests.post(url, headers=revio_headers(), json=payload, timeout=60)


def update_opportunity(opportunity_id: str, payload: dict) -> requests.Response:
    url = f"{REVIO_BASE_URL}/billing/api/v1/opportunities/{opportunity_id}"
    return requests.put(url, headers=revio_headers(), json=payload, timeout=60)


def delete_opportunity(opportunity_id: str) -> requests.Response:
    url = f"{REVIO_BASE_URL}/billing/api/v1/opportunities/{opportunity_id}"
    return requests.delete(url, headers=revio_headers(), timeout=60)


# -----------------------------
# Adaptive cards
# -----------------------------
def main_menu_card() -> dict:
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": "Opportunity Actions",
                "weight": "Bolder",
                "size": "Medium",
            },
            {
                "type": "TextBlock",
                "text": "Choose which opportunity action you want to continue with.",
                "wrap": True,
            },
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Create Opportunity",
                "data": {"action": "show_create_form"},
            },
            {
                "type": "Action.Submit",
                "title": "Update Opportunity",
                "data": {"action": "show_update_form"},
            },
            {
                "type": "Action.Submit",
                "title": "Delete Opportunity",
                "data": {"action": "show_delete_form"},
            },
        ],
    }


def create_form_card() -> dict:
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "text": "Create Opportunity", "weight": "Bolder", "size": "Medium"},
            {"type": "Input.Text", "id": "name", "label": "Opportunity Name"},
            {"type": "Input.Text", "id": "customerId", "label": "Customer ID"},
            {"type": "Input.Text", "id": "amount", "label": "Amount"},
            {"type": "Input.Text", "id": "stageId", "label": "Stage ID"},
            {"type": "Input.Text", "id": "statusId", "label": "Status ID"},
            {"type": "Input.Text", "id": "typeId", "label": "Type ID"},
            {"type": "Input.Text", "id": "sourceId", "label": "Source ID"},
            {"type": "Input.Text", "id": "notes", "label": "Notes", "isMultiline": True},
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit Create",
                "data": {"action": "submit_create"},
            }
        ],
    }


def update_form_card() -> dict:
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "text": "Update Opportunity", "weight": "Bolder", "size": "Medium"},
            {"type": "Input.Text", "id": "opportunityId", "label": "Opportunity ID"},
            {"type": "Input.Text", "id": "name", "label": "Opportunity Name"},
            {"type": "Input.Text", "id": "customerId", "label": "Customer ID"},
            {"type": "Input.Text", "id": "amount", "label": "Amount"},
            {"type": "Input.Text", "id": "stageId", "label": "Stage ID"},
            {"type": "Input.Text", "id": "statusId", "label": "Status ID"},
            {"type": "Input.Text", "id": "typeId", "label": "Type ID"},
            {"type": "Input.Text", "id": "sourceId", "label": "Source ID"},
            {"type": "Input.Text", "id": "notes", "label": "Notes", "isMultiline": True},
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit Update",
                "data": {"action": "submit_update"},
            }
        ],
    }


def delete_form_card() -> dict:
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {"type": "TextBlock", "text": "Delete Opportunity", "weight": "Bolder", "size": "Medium"},
            {"type": "Input.Text", "id": "opportunityId", "label": "Opportunity ID"},
        ],
        "actions": [
            {
                "type": "Action.Submit",
                "title": "Submit Delete",
                "data": {"action": "submit_delete"},
            }
        ],
    }


# -----------------------------
# Payload mapping
# -----------------------------
def clean_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value != "" else None
    return value


def build_create_payload(inputs: dict) -> dict:
    payload = {
        "name": clean_value(inputs.get("name")),
        "customer_id": clean_value(inputs.get("customerId")),
        "amount": clean_value(inputs.get("amount")),
        "stage_id": clean_value(inputs.get("stageId")),
        "status_id": clean_value(inputs.get("statusId")),
        "type_id": clean_value(inputs.get("typeId")),
        "source_id": clean_value(inputs.get("sourceId")),
        "notes": clean_value(inputs.get("notes")),
    }

    return {k: v for k, v in payload.items() if v is not None}


def build_update_payload(inputs: dict) -> dict:
    payload = {
        "name": clean_value(inputs.get("name")),
        "customer_id": clean_value(inputs.get("customerId")),
        "amount": clean_value(inputs.get("amount")),
        "stage_id": clean_value(inputs.get("stageId")),
        "status_id": clean_value(inputs.get("statusId")),
        "type_id": clean_value(inputs.get("typeId")),
        "source_id": clean_value(inputs.get("sourceId")),
        "notes": clean_value(inputs.get("notes")),
    }

    return {k: v for k, v in payload.items() if v is not None}


# -----------------------------
# Formatting helper
# -----------------------------
def short_response_text(response: requests.Response) -> str:
    try:
        body = response.json()
    except Exception:
        body = response.text

    return f"Status: {response.status_code}\nResponse: {body}"


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")

    resource = body.get("resource")
    event = body.get("event")
    data = body.get("data", {})

    # --------------------------------------------------
    # Handle normal text messages
    # --------------------------------------------------
    if resource == "messages" and event == "created":
        message_id = data.get("id")
        room_id = data.get("roomId")

        if not message_id or not room_id:
            return JSONResponse({"status": "ignored - missing message id or room id"})

        try:
            message = get_webex_message(message_id)
        except Exception as exc:
            return JSONResponse({"status": f"failed to get message: {exc}"}, status_code=500)

        text = (message.get("text") or "").strip().lower()

        # Only trigger on exact phrase requested by user
        if text == "bot opprotunities":
            try:
                send_webex_message(
                    room_id=room_id,
                    text="Choose an opportunity action below.",
                    card=main_menu_card(),
                )
                return JSONResponse({"status": "main menu sent"})
            except Exception as exc:
                return JSONResponse({"status": f"failed to send menu: {exc}"}, status_code=500)

        return JSONResponse({"status": "ignored - text did not match trigger"})

    # --------------------------------------------------
    # Handle card submissions
    # --------------------------------------------------
    if resource == "attachmentActions" and event == "created":
        action_id = data.get("id")

        if not action_id:
            return JSONResponse({"status": "ignored - missing action id"})

        try:
            action_data = get_attachment_action(action_id)
        except Exception as exc:
            return JSONResponse({"status": f"failed to get attachment action: {exc}"}, status_code=500)

        inputs = action_data.get("inputs", {}) or {}
        room_id = action_data.get("roomId")
        action = inputs.get("action")

        if not room_id:
            return JSONResponse({"status": "ignored - missing room id"})

        # Show forms
        if action == "show_create_form":
            send_webex_message(room_id, text="Create opportunity form:", card=create_form_card())
            return JSONResponse({"status": "create form sent"})

        if action == "show_update_form":
            send_webex_message(room_id, text="Update opportunity form:", card=update_form_card())
            return JSONResponse({"status": "update form sent"})

        if action == "show_delete_form":
            send_webex_message(room_id, text="Delete opportunity form:", card=delete_form_card())
            return JSONResponse({"status": "delete form sent"})

        # Submit create
        if action == "submit_create":
            payload = build_create_payload(inputs)

            try:
                response = create_opportunity(payload)
            except Exception as exc:
                send_webex_message(room_id, text=f"Create request failed: {exc}")
                return JSONResponse({"status": f"create exception: {exc}"}, status_code=500)

            if response.ok:
                send_webex_message(
                    room_id,
                    text=f"Opportunity created successfully.\n{short_response_text(response)}",
                )
            else:
                send_webex_message(
                    room_id,
                    text=f"Create failed.\n{short_response_text(response)}",
                )

            return JSONResponse({"status": "create handled"})

        # Submit update
        if action == "submit_update":
            opportunity_id = clean_value(inputs.get("opportunityId"))
            if not opportunity_id:
                send_webex_message(room_id, text="Update failed: Opportunity ID is required.")
                return JSONResponse({"status": "missing opportunity id for update"}, status_code=400)

            payload = build_update_payload(inputs)

            try:
                response = update_opportunity(opportunity_id, payload)
            except Exception as exc:
                send_webex_message(room_id, text=f"Update request failed: {exc}")
                return JSONResponse({"status": f"update exception: {exc}"}, status_code=500)

            if response.ok:
                send_webex_message(
                    room_id,
                    text=f"Opportunity {opportunity_id} updated successfully.\n{short_response_text(response)}",
                )
            else:
                send_webex_message(
                    room_id,
                    text=f"Update failed.\n{short_response_text(response)}",
                )

            return JSONResponse({"status": "update handled"})

        # Submit delete
        if action == "submit_delete":
            opportunity_id = clean_value(inputs.get("opportunityId"))
            if not opportunity_id:
                send_webex_message(room_id, text="Delete failed: Opportunity ID is required.")
                return JSONResponse({"status": "missing opportunity id for delete"}, status_code=400)

            try:
                response = delete_opportunity(opportunity_id)
            except Exception as exc:
                send_webex_message(room_id, text=f"Delete request failed: {exc}")
                return JSONResponse({"status": f"delete exception: {exc}"}, status_code=500)

            if response.ok:
                send_webex_message(
                    room_id,
                    text=f"Opportunity {opportunity_id} deleted successfully.\n{short_response_text(response)}",
                )
            else:
                send_webex_message(
                    room_id,
                    text=f"Delete failed.\n{short_response_text(response)}",
                )

            return JSONResponse({"status": "delete handled"})

        return JSONResponse({"status": f"unknown action: {action}"})

    return JSONResponse({"status": "ignored - unsupported event"})