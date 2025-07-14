# backend/app.py
import sys
import asyncio
from flask import Flask, request, jsonify
from browser_control import BrowserController
from email_generator import generate_email
# for asyncio on Windows
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = Flask(__name__)

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()

    controller = BrowserController(
        email=data["email"],
        password=data["password"]
    )

    async def run_send():
        return await controller.send_email(
            to=data["to"],
            subject=data["subject"],
            body=data["body"]
        )

    try:
        # run async Playwright inside sync Flask route
        result = asyncio.run(run_send())
        return jsonify(result)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/generate-email", methods=["POST"])
def generate():
    data = request.get_json()
    try:
        content = generate_email(
            to=data["to"],
            subject=data["subject"],
            context=data["context"],
            tone=data.get("tone", "professional"),
            sender_name=data.get("sender_name", ""),
            recipient_name=data.get("recipient_name", "")
        )
        return jsonify({"status": "success", "email": content})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
