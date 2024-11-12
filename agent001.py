import streamlit as st
import requests

ollama_url = "http://172.16.206.31:11434"  # Ollama API endpoint

# Initialize chat sessions in session state
if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = {}
if "current_session" not in st.session_state:
    st.session_state["current_session"] = None

# Function to read file content
def read_file(uploaded_file):
    if uploaded_file is not None:
        return uploaded_file.read().decode("utf-8")
    return None

# Send input (text or file content) to Ollama and get the response
def get_ollama_response(input_text: str) -> str:
    payload = {
        "model": "llama3.2",
        "prompt": input_text,
        "stream": False,
    }
    response = requests.post(f"{ollama_url}/api/generate", json=payload)
    return response.json().get("response", "")

# Sidebar for managing chat sessions
with st.sidebar:
    st.title("Chat Sessions")
    new_chat = st.button("Start New Chat")
    
    if new_chat:
        session_id = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[session_id] = []
        st.session_state.current_session = session_id
    
    # Display previous chat sessions
    session_list = list(st.session_state.chat_sessions.keys())
    if session_list:
        st.session_state.current_session = st.selectbox("Select Chat", session_list, index=session_list.index(st.session_state.current_session))

# Apply CSS for styling (with improved colors and black font for agent response)
st.markdown(
    """
    <style>
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f0f0f5;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
    }
    .user-msg {
        background-color: #d1e7ff;
        color: black;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid #a4c6ff;
    }
    .agent-msg {
        background-color: #e8e8e8;
        color: black;  /* Set font color to black */
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid #d1d1d1;
    }
    .chat-input-container {
        display: flex;
        align-items: center;
        position: relative;
        width: 100%;
        margin-top: 20px;
    }
    .chat-input {
        width: 80%;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    .chat-send-btn {
        width: 15%;
        margin-left: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 10px;
        cursor: pointer;
    }
    .chat-send-btn:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main layout
if st.session_state.current_session:
    st.header(st.session_state.current_session)
    
    # Chat container for history and input
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        # Display chat history for the selected session
        chat_history = st.session_state.chat_sessions[st.session_state.current_session]
        for chat in chat_history:
            if "user" in chat:
                st.markdown(f'<div class="user-msg">{chat["user"]}</div>', unsafe_allow_html=True)
            elif "agent" in chat:
                st.markdown(f'<div class="agent-msg">{chat["agent"]}</div>', unsafe_allow_html=True)

        # Combined chat input and file upload
        with st.form(key="chat_input_form"):
            user_input = st.text_input("Type your message here...", key="user_input", label_visibility="collapsed")
            uploaded_file = st.file_uploader(" ", type=["csv", "log"], label_visibility="collapsed")
            submit_button = st.form_submit_button(label="Send")

            # Handle file uploads or text submission when the "Send" button is pressed
            input_text = None
            if uploaded_file:
                input_text = read_file(uploaded_file)
                # Add the prompt from the uploaded file as a message in the chat history
                st.session_state.chat_sessions[st.session_state.current_session].append({"user": f"File uploaded: {uploaded_file.name}"})
            elif submit_button and user_input:
                input_text = user_input
                # Add the user input as a message in the chat history
                st.session_state.chat_sessions[st.session_state.current_session].append({"user": user_input})

            # Only send to Ollama if there is input and "Send" was clicked
            if input_text and submit_button:
                response = get_ollama_response(input_text)
                # Add the agent response to the chat history
                st.session_state.chat_sessions[st.session_state.current_session].append({"agent": response})
                st.experimental_rerun()  # This will refresh the page to show the updated conversation

        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
else:
    st.write("Start a new chat or select an existing chat session from the sidebar.")
