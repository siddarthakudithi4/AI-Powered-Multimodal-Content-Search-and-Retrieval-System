import streamlit as st
import pymongo
from datetime import datetime
import time
import os
import urllib.parse

# --- Load credentials from environment variables ---
MONGO_USER = "user1"
MONGO_PASSWORD = "siddartha@660"

# --- Validate credentials ---
if not MONGO_USER or not MONGO_PASSWORD:
    st.error("❌ MongoDB credentials not found.")
    st.stop()

# --- Escape special characters in credentials ---
escaped_user = urllib.parse.quote_plus(MONGO_USER)
escaped_pass = urllib.parse.quote_plus(MONGO_PASSWORD)

# --- MongoDB Connection ---
MONGO_URI = f"mongodb+srv://{escaped_user}:{escaped_pass}@cluster0.s0d01at.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URI)
db = client["messenger"]
users_collection = db["users"]
messages_collection = db["messages"]

# --- Helper Functions ---
def register_user(username, password, security_answer):
    if users_collection.find_one({"username": username}):
        return False
    users_collection.insert_one({
        "username": username,
        "password": password,
        "security_answer": security_answer
    })
    return True

def login_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    return user is not None

def reset_password(username, security_answer, new_password):
    user = users_collection.find_one({"username": username, "security_answer": security_answer})
    if user:
        users_collection.update_one(
            {"username": username},
            {"$set": {"password": new_password}}
        )
        return True
    return False

def send_message(sender, room, message, file_data=None, file_name=None):
    messages_collection.insert_one({
        "sender": sender,
        "room": room,
        "message": message,
        "timestamp": datetime.now(),
        "file_data": file_data,
        "file_name": file_name
    })

def get_messages(room):
    return list(messages_collection.find({"room": room}).sort("timestamp", pymongo.ASCENDING))

def delete_message(message_id):
    messages_collection.delete_one({"_id": message_id})

def edit_message(message_id, new_content):
    messages_collection.update_one({"_id": message_id}, {"$set": {"message": new_content}})

# --- Session State Setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = datetime.now()

# --- Sidebar Authentication ---
st.sidebar.title("Messenger App")
auth_option = st.sidebar.selectbox("Choose an option", ["Login", "Register", "Reset Password"])

if auth_option == "Register":
    st.sidebar.subheader("Register New User")
    new_username = st.sidebar.text_input("Username")
    new_password = st.sidebar.text_input("Password", type="password")
    security_answer = st.sidebar.text_input("Security Answer")
    if st.sidebar.button("Register"):
        if register_user(new_username, new_password, security_answer):
            st.sidebar.success("Registered Successfully! Please Login.")
        else:
            st.sidebar.error("Username already exists.")

elif auth_option == "Login":
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.sidebar.success(f"Logged in as {username}!")
        else:
            st.sidebar.error("Invalid Username or Password.")

elif auth_option == "Reset Password":
    st.sidebar.subheader("Reset Password")
    reset_username = st.sidebar.text_input("Username (Reset)")
    reset_answer = st.sidebar.text_input("Security Answer")
    new_password = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Reset Password"):
        if reset_password(reset_username, reset_answer, new_password):
            st.sidebar.success("Password reset successfully! Now login.")
        else:
            st.sidebar.error("Incorrect security answer or username.")

# --- Main App (After Login) ---
if st.session_state.logged_in:
    st.title(f"👋 Welcome, {st.session_state.username}!")

    # Room Selection
    room = st.selectbox("Select a Chat Room", ["general", "sports", "tech", "music"])

    # Message Input
    message = st.text_input("Type your message here...")
    uploaded_file = st.file_uploader("Upload a file (optional)", type=["png", "jpg", "jpeg", "pdf", "docx"])

    if st.button("Send"):
        file_data = None
        file_name = None
        if uploaded_file:
            file_data = uploaded_file.read()
            file_name = uploaded_file.name
        send_message(st.session_state.username, room, message, file_data, file_name)
        st.session_state.last_message_time = datetime.now()
        st.success("✅ Message Sent!")

    # Chat Room Display
    st.subheader(f"💬 Chat Room: {room}")

    messages = get_messages(room)
    for msg in messages:
        col1, col2 = st.columns([8, 2])
        with col1:
            st.markdown(f"**{msg['sender']}**: {msg['message']}")
            st.caption(msg["timestamp"].strftime("%Y-%m-%d %H:%M:%S"))
            if msg.get("file_name"):
                st.download_button(
                    label=f"📥 Download {msg['file_name']}",
                    data=msg["file_data"],
                    file_name=msg["file_name"],
                    key=str(msg["_id"]) + "_download"
                )
        if msg["sender"] == st.session_state.username:
            with col2:
                if st.button("Edit", key=str(msg["_id"]) + "_edit"):
                    new_content = st.text_input("Edit your message", value=msg["message"], key=str(msg["_id"]) + "_input")
                    if st.button("Save", key=str(msg["_id"]) + "_save"):
                        edit_message(msg["_id"], new_content)
                        st.rerun()
                if st.button("Delete", key=str(msg["_id"]) + "_delete"):
                    delete_message(msg["_id"])
                    st.rerun()

    # Push Notification (Toast)
    if messages:
        latest_msg_time = messages[-1]["timestamp"]
        if latest_msg_time > st.session_state.last_message_time:
            st.toast(f"🔔 New message from {messages[-1]['sender']} in {room}!")
            st.session_state.last_message_time = latest_msg_time

    # --- Auto-refresh every 2 seconds for real-time updates ---
    time.sleep(2)
    st.rerun()
