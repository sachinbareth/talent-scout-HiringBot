import streamlit as st
from app.models.assistant import HiringAssistant

def initialize_session():
    if "assistant" not in st.session_state:
        st.session_state.assistant = HiringAssistant()
        # This will now work:
        greeting = st.session_state.assistant.generate_response("")  
        st.session_state.messages = [{"role": "assistant", "content": greeting}]

def display_chat():
    st.title("TalentScouT Hiring Assistant")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = st.session_state.assistant.generate_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

def main():
    initialize_session()
    display_chat()

if __name__ == "__main__":
    main()
