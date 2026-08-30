import streamlit as st
import requests

st.title("SQL Analyst Agent")
st.caption("Ask questions about the ride-hailing dataset in plain English.")

question = st.text_input("Your question:")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        res = requests.post("http://localhost:8000/query", json={"question": question})

    st.write(f"Status code: {res.status_code}")

    if res.status_code == 200:
        data = res.json()
        st.subheader("Generated SQL")
        st.code(data["generated_sql_query"], language="sql")
        st.subheader("Answer")
        st.write(data["final_answer"])
    else:
        st.error(f"Request failed:\n\n{res.text}")