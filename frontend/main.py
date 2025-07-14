import streamlit as st
import requests
import os
from PIL import Image

st.set_page_config(layout="wide")
st.title("Browser Automation Chatbot")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "screenshots" not in st.session_state:
    st.session_state.screenshots = []

# Layout: 2 columns
col1, col2 = st.columns([2, 1])

#Left Side: Chat Interface
with col1:
    st.subheader("💬 Conversation")
    user_input = st.chat_input("Say something...")

    if user_input:
        st.session_state.messages.append(("You", user_input))
        response = requests.post("http://localhost:5001/process", json={"message": user_input})
        bot_reply = response.json()["response"]
        st.session_state.messages.append(("AI", bot_reply))

    # Display chat messages in reverse order (latest at bottom)
    for role, msg in st.session_state.messages[::-1]:
        st.chat_message(role).markdown(msg)

#Right Side: Screenshot Viewer
with col2:
    show_screens = any("Email sent" in msg for _, msg in st.session_state.messages)

    if show_screens:
        st.subheader(" Screenshots")

        screenshot_dir = "../screenshots"
        if os.path.exists(screenshot_dir):
            images = sorted([
                f for f in os.listdir(screenshot_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ])
            st.session_state.screenshots = images

        if st.session_state.screenshots:
            index = st.slider("Slide", 0, len(st.session_state.screenshots) - 1, 0)
            img_path = os.path.join(screenshot_dir, st.session_state.screenshots[index])
            image = Image.open(img_path)
            st.image(image, caption=f"Screenshot {index + 1}", use_container_width=True)
        else:
            st.info("No screenshots found yet.")
