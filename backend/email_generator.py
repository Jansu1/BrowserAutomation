# backend/email_generator.py
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")  # Replace with your actual key

model = genai.GenerativeModel("gemini-2.5-pro")

def generate_email(to: str, subject: str, context: str, tone="professional", sender_name="", recipient_name=""):
    prompt = f"""
    Write a {tone} email to {recipient_name or to} regarding "{subject}".
    The email is from {sender_name}.
    Context: {context}

    Format:
    - Start with: "Dear {recipient_name},"
    - End with: "Best regards, {sender_name}"

    Only return the body of the email (subject is already set). Keep it concise.
    """
    response = model.generate_content(prompt)
    print(f"Generated email content: {response.text}")
    return response.text

