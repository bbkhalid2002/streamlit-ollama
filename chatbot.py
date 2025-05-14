import streamlit as st
from litellm import completion

# URL of your local Ollama server
OLLAMA_API_BASE = "http://localhost:11434"

st.set_page_config(page_title="Ollama Chatbot", layout="centered")

# --- Sidebar controls ---
default_prompt = "You are a helpful assistant."
system_prompt = st.sidebar.text_area(
    "System Prompt",
    value=st.session_state.get("system_prompt", default_prompt),
    key="system_prompt",
    height=150
)

# Instruction checkboxes
reply_code_only = st.sidebar.checkbox("Reply in code only")
explain_code     = st.sidebar.checkbox("Explain the code")
suggest_opt      = st.sidebar.checkbox("Suggest optimization")
be_concise      = st.sidebar.checkbox("Be concise")

# Clear chat history button
if st.sidebar.button("Clear chat"):
    # Reset to only the current system prompt
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# --- Initialize / sync chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
else:
    # Keep the system prompt message in sync
    if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
        st.session_state.messages[0]["content"] = system_prompt
    else:
        st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})

# --- Main chat UI ---
st.title("💬 Chat with Ollama")

# Render past messages (skip the system prompt)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new user input
if user_input := st.chat_input("Say something…"):
    # Build the final prompt with checkbox instructions
    final_prompt = user_input
    if reply_code_only:
        final_prompt += "\nReply in code only."
    if explain_code:
        final_prompt += "\nExplain the code."
    if suggest_opt:
        final_prompt += "\nSuggest optimization."
    if be_concise:
        final_prompt += "\nBe concise."


    # 1. Save & display the user's message
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # 2. Stream the assistant’s reply
    with st.chat_message("assistant"):
        full_reply = ""
        placeholder = st.empty()
        with st.spinner("Thinking…"):
            for chunk in completion(
                model="ollama_chat/gemma3:1b",
                messages=st.session_state.messages,
                api_base=OLLAMA_API_BASE,
                stream=True
            ):
                delta = chunk["choices"][0]["delta"].get("content") or ""
                full_reply += delta
                placeholder.markdown(full_reply)

    # 3. Save the assistant’s reply
    st.session_state.messages.append({"role": "assistant", "content": full_reply})
