import streamlit as st
import requests

st.set_page_config(page_title="Onboarding Buddy", page_icon="🤖")

st.title("Onboarding Buddy")
st.caption("AI assistant for company policies")

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Employee Info")

    # Add role selection in the sidebar
    role = st.selectbox(
        "Role",
        ["intern", "full_time"]
    )

    # Fetch list from backend based on selected role
    try:
        r = requests.get(
            "http://localhost:8000/list_by_role",  # Backend endpoint
            params={"role": role},  # Send the selected role as a parameter
            timeout=10
        )
        r.raise_for_status()  # Check if request is successful
        items = r.json().get("items", [])
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        items = []

    # Handle case when no users are found for the selected role
    if not items:
        st.warning("No users found for this role.")
        user_id = None
    else:
        # Show user selection dropdown
        selected = st.selectbox(
            "Select Person",
            items,
            format_func=lambda x: f"{x['id']} - {x['name']}"
        )
        user_id = selected["id"]  # Store the selected user's ID

    # Checkbox to show debug information
    show_debug = st.checkbox("Show retrieved context (debug)")

# -----------------------------
# Main Area
# -----------------------------
st.divider()

question = st.text_area("Ask your question")

if st.button("Ask"):
    # Check if question is empty or user is not selected
    if not question.strip():
        st.warning("Please enter a question.")
    elif not user_id:
        st.warning("Please select a user.")
    else:
        with st.spinner("Thinking..."):
            try:
                # Send the request to the backend with role and user information
                r = requests.post(
                    "http://localhost:8000/chat",  # Backend API
                    json={
                        "user_id": user_id,  # User's ID
                        "question": question,  # The question being asked
                        "role": role,  # Send the user's role
                        "debug": show_debug  # Include debug flag
                    },
                    timeout=120
                )

                if r.status_code != 200:
                    st.error(r.text)  # Show error if backend request fails
                else:
                    data = r.json()

                    # Display the answer from the backend
                    st.subheader("Answer")
                    st.write(data.get("answer", "No answer returned."))

                    # Show debug context if enabled
                    if show_debug:
                        st.subheader("Context")
                        for c in data.get("context", []):
                            st.code(c)

            except Exception as e:
                st.error(f"Request failed: {e}")
