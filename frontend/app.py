import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/ask"


st.set_page_config(
    page_title="Enterprise Maintenance AI Assistant",
    page_icon="🏭",
)

st.title("🏭 Enterprise Maintenance AI Assistant")

st.write(
    "Ask a maintenance question. The assistant answers using approved internal documents."
)

user_question = st.text_area(
    "Maintenance question",
    placeholder="Example: What should I do if the pump is overheating?",
)

if st.button("Ask Assistant"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching documents and generating answer..."):
            response = requests.post(
                API_URL,
                json={"question": user_question},
                timeout=60,
            )

        if response.status_code != 200:
            st.error("API error. Check FastAPI terminal.")
        else:
            result = response.json()

            st.subheader("Answer")
            st.write(result["answer"])

            st.subheader("Sources")
            for source in result["sources"]:
                st.write(f"- {source}")