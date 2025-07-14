from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json
import requests
import google.generativeai as genai


genai.configure(api_key="GEMINI_API_KEY")  # Replace with your actual key
model = genai.GenerativeModel("gemini-2.5-pro")

# Flask App Init
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication


def safe_extract_json(text):
    try:
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print("JSON extraction error:", e)
    print("Failed to extract JSON from:", text)
    return None

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# NLP Agent Class
class NLPAgent:
    def __init__(self):
        self.session = {
            "intent": "",
            "from": "",
            "password": "",
            "to": "",
            "subject": "",
            "context": "",
            "tone": "professional",
            "start_date": "",
            "end_date": "",
            "sender_name": "",
            "recipient_name": ""
        }

    def process_input(self, user_input):
        if self.session["intent"] == "send_email" and not self.all_required_filled():
            return self.handle_missing_slot(user_input)
        prompt = f"""
Classify the user's intent from: "send_email", "chat", or "unknown".
Input: \"\"\"{user_input}\"\"\"
Return JSON only: {{"intent": "<send_email/chat/unknown>"}}
No preamble.
"""
        try:
            response = model.generate_content(prompt).text
            parsed = safe_extract_json(response)
        except Exception as e:
            return f" Failed to detect intent: {e}"

        if not parsed or "intent" not in parsed:
            return "Sorry, I couldn't understand your request."

        self.session["intent"] = parsed["intent"]

        if parsed["intent"] == "send_email":
            return self.extract_slots(user_input)
        elif parsed["intent"] == "chat":
            return self.chat_response(user_input)
        else:
            return "I'm here to help with emails or general questions. How can I assist you today?"

    def extract_slots(self, user_input):
        prompt = f"""
Extract the following fields from this user's request if available.
Input: \"\"\"{user_input}\"\"\"

Return JSON:
{{
  "from": "",
  "password": "",
  "to": "",
  "subject": "",
  "context": "",
  "tone": "professional",
  "start_date": "",
  "end_date": "",
  "sender_name": "",
  "recipient_name": ""
}}
Leave fields empty if not mentioned. No preamble.
"""
        try:
            response = model.generate_content(prompt).text
            slots = safe_extract_json(response)
        except Exception as e:
            return f"Failed to extract slots: {e}"

        if not slots:
            return "Couldn’t extract email details. Can you rephrase?"

        for key, val in slots.items():
            if val and not self.session[key]:
                self.session[key] = val

        return self.next_email_step()

    def handle_missing_slot(self, user_input):
        slot_prompts = {
            "from": "What's your Gmail address?",
            "password": "And your Gmail password? (Only use test accounts!)",
            "to": "Who should the email be sent to? (Please give their Gmail address)",
            "subject": "What's the subject of the email?",
            "context": "What should the email say?",
            "sender_name": "What's your name?",
            "recipient_name": "What's the recipient's name?",
            "start_date": "When do you plan to take the leave?",
            "end_date": "When will you be returning?"
        }

        for slot, prompt in slot_prompts.items():
            if not self.session[slot]:
                if slot in ["from", "to"] and is_valid_email(user_input.strip()):
                    self.session[slot] = user_input.strip()
                    return self.next_email_step()
                elif slot == "password":
                    self.session[slot] = user_input.strip()
                    return self.next_email_step()

                extraction_prompt = f"""
Extract only the value for "{slot}" from the user input below. Do NOT infer other fields.
User input: \"\"\"{user_input}\"\"\"
Return JSON: {{"{slot}": "<value>"}}
No preamble.
"""
                try:
                    response = model.generate_content(extraction_prompt).text
                    parsed = safe_extract_json(response)
                except Exception as e:
                    return f" Failed extracting {slot}: {e}"

                if parsed and parsed.get(slot):
                    self.session[slot] = parsed[slot]
                    return self.next_email_step()
                else:
                    return prompt

        return self.next_email_step()

    def next_email_step(self):
        required_slots = ["from", "password", "to", "subject", "context", "sender_name", "recipient_name"]
        prompts = {
            "from": "What's your Gmail address?",
            "password": "And your Gmail password? (Only use test accounts!)",
            "to": "Who should the email be sent to? (Please give their Gmail address)",
            "subject": "What's the subject of the email?",
            "context": "What should the email say?",
            "sender_name": "What's your name?",
            "recipient_name": "What's the recipient's name?"
        }

        for slot in required_slots:
            if not self.session[slot]:
                return prompts[slot]

        return self.generate_and_send()

    def generate_and_send(self):
        try:
            gen_response = requests.post(
                "http://localhost:5000/generate-email",
                json={
                    "to": self.session["to"],
                    "subject": self.session["subject"],
                    "context": self.session["context"],
                    "tone": self.session.get("tone", "professional"),
                    "sender_name": self.session.get("sender_name", ""),
                    "recipient_name": self.session.get("recipient_name", "")
                }
            )
            gen_response.raise_for_status()
            email_content = gen_response.json()["email"]
        except Exception as e:
            return f"📨 Email generation failed: {e}"

        try:
            send_response = requests.post(
                "http://localhost:5000/send-email",
                json={
                    "email": self.session["from"],
                    "password": self.session["password"],
                    "to": self.session["to"],
                    "subject": self.session["subject"],
                    "body": email_content
                }
            )
            send_response.raise_for_status()
            return send_response.json().get("message", "Email sent successfully!")
        except Exception as e:
            return f"Email sending failed: {e}"

    def all_required_filled(self):
        keys = ["from", "password", "to", "subject", "context", "sender_name", "recipient_name"]
        return all(self.session.get(k) for k in keys)

    def chat_response(self, user_input):
        prompt = f"""
You're a friendly chatbot. Respond helpfully to:
\"\"\"{user_input}\"\"\"
No preamble. Friendly tone.
"""
        try:
            response = model.generate_content(prompt).text
            return response.strip()
        except Exception as e:
            return f"Chat failed: {e}"



agent = NLPAgent()

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"response": "No input received."}), 400

    result = agent.process_input(user_input)
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
