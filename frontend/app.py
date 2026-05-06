import streamlit as st
import requests

# Configuration de la page
st.set_page_config(page_title="Travel Agent", page_icon="✈️")

st.title("✈️ Travel Agent")

# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique
for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.write(message)

# Input utilisateur (mode chat moderne)
user_input = st.chat_input("Ask about a destination, budget, weather, etc...")

if user_input:
    # Ajouter message user
    st.session_state.messages.append(("user", user_input))

    # Afficher message user immédiatement
    with st.chat_message("user"):
        st.write(user_input)

    # Appel API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://backend:8000/chat",
                    json={
                        "user_message": user_input,
                        "session_id": "test_session"
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    bot_message = response.json().get(
                        "bot_message",
                        "No response from the agent."
                    )
                else:
                    bot_message = "Error communicating with the API."

            except requests.exceptions.RequestException:
                bot_message = "Unable to reach the backend."

            # Afficher réponse
            st.write(bot_message)

    # Ajouter réponse à l'historique
    st.session_state.messages.append(("assistant", bot_message))