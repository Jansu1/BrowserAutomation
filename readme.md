# 🤖 Smart Email Agent – AI-Powered Browser Automation

A conversational AI assistant that understands user intent, gathers email details, generates email drafts, and uses browser automation to send emails with screenshots.

---


**Components:**

1. **Frontend (Streamlit UI)**
   - Chat interface for user-AI conversation
   - Screenshot viewer (carousel) for visual feedback

2. **Flask Backend**
   - Handles incoming messages from frontend
   - Coordinates between:
     - `nlp_agent.py`: Intent detection, slot filling, and dialogue management
     - `email_generator.py`: Generates well-formatted emails
     - `browser_control.py`: Uses Playwright to automate Gmail login, fill, and send email

---

## 🔍 Component Breakdown

### 🧠 NLP Agent (`nlp_agent.py`)
- Uses Gemini 2.5 Pro (Google AI)
- Identifies intent (e.g., `send_email`)
- Performs slot filling (e.g., `to`, `from`, `subject`, `body`, `date`, `duration`)
- Asks smart follow-up questions for missing info

### ✍️ Email Generator (`email_generator.py`)
- Generates human-like email drafts using LLM based on collected slots
- Ensures clarity, tone, and professionalism

### 🌐 Browser Controller (`browser_control.py`)
- Headless browser automation using Playwright
- Logs into Gmail, fills email fields, and clicks send
- Takes screenshots after each action and saves them

### 🖥️ Streamlit Frontend
- Two-panel layout:
  - **Left**: Conversation chat flow
  - **Right**: Screenshot carousel viewer
- Detects when email is sent and dynamically displays screenshots

---

## 🧪 Technology Stack

| Layer          | Technology         | Reason                                                                 |
|----------------|--------------------|------------------------------------------------------------------------|
| Frontend       | Streamlit          | Simple UI, perfect for rapid prototyping & interactive chat            |
| Backend        | Flask              | Lightweight, easy to integrate with agents and REST endpoints          |
| Browser        | Playwright         | Reliable automation with screenshot support                            |
| NLP/LLM        | Gemini 2.5 Pro     | Accurate intent classification, slot filling, and follow-up generation |
| State Handling | `st.session_state` | Tracks conversation and screenshot history in Streamlit                |

---

## ⚙️ Setup & Running

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/ai-browser-agent.git
cd ai-browser-agent
```

### 2. Create Python Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
playwright install
```

### 4. Run the Flask Backend
```bash
cd backend
python app.py
python nlp_agent.py # Run command in Another terminal
```

### 5. Run the Streamlit Frontend
```bash
cd ../frontend/
streamlit run main.py
```

