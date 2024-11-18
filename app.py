import streamlit as st
import pandas as pd
import sqlite3
import json
import os

# Load credentials from credentials.json
def load_credentials():
    with open("credentials.json", "r") as file:
        return json.load(file)

credentials = load_credentials()

# Initialize SQLite database connection
conn = sqlite3.connect('repair_blog_db.db')
c = conn.cursor()

# Create tables for repair requests, training requests, blogs, and feedback
c.execute('''CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT, 
    name TEXT, 
    employee_no TEXT, 
    station TEXT, 
    department TEXT, 
    material_name TEXT, 
    material_code TEXT, 
    quantity INTEGER, 
    defect_description TEXT, 
    priority TEXT, 
    status TEXT DEFAULT 'Pending'
)''')

c.execute('''CREATE TABLE IF NOT EXISTS training_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT, 
    name TEXT, 
    employee_no TEXT, 
    station TEXT, 
    designation TEXT, 
    training_slot TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS blogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT, 
    title TEXT, 
    content TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT, 
    request_id INTEGER, 
    feedback TEXT, 
    rating INTEGER
)''')

conn.commit()

# Helper functions for database operations
def add_request(username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority):
    c.execute(
        "INSERT INTO requests (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority)
    )
    conn.commit()

def get_requests(username=None):
    if username:
        c.execute("SELECT rowid, * FROM requests WHERE username = ?", (username,))
    else:
        c.execute("SELECT rowid, * FROM requests")
    return c.fetchall()

def add_training_request(username, name, employee_no, station, designation, training_slot):
    c.execute(
        "INSERT INTO training_requests (username, name, employee_no, station, designation, training_slot) VALUES (?, ?, ?, ?, ?, ?)",
        (username, name, employee_no, station, designation, training_slot)
    )
    conn.commit()

def add_blog(author, title, content):
    c.execute("INSERT INTO blogs (author, title, content) VALUES (?, ?, ?)", (author, title, content))
    conn.commit()

def get_blogs():
    c.execute("SELECT * FROM blogs")
    return c.fetchall()

def add_feedback(username, request_id, feedback, rating):
    c.execute(
        "INSERT INTO feedback (username, request_id, feedback, rating) VALUES (?, ?, ?, ?)", 
        (username, request_id, feedback, rating)
    )
    conn.commit()

# Display logos and heading
def display_logo_and_heading():
    ntpc_logo_path = "ntpc_logo.png"
    elab_logo_path = "centralized_elab_logo.png"

    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if os.path.exists(ntpc_logo_path):
            st.image(ntpc_logo_path, use_column_width=False, width=150)
    with col2:
        st.markdown("<h1 style='text-align: center;'>NTPC Electronics Repair Lab</h1>", unsafe_allow_html=True)
    with col3:
        if os.path.exists(elab_logo_path):
            st.image(elab_logo_path, use_column_width=False, width=150)

# Login functionality
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = next((u for u in credentials["users"] if u["username"] == username and u["password"] == password), None)
        if user:
            st.session_state.auth_state = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Invalid login credentials")

# Repair Request Form
def repair_request_form():
    st.header("Submit Repair Request")
    name = st.text_input("Name")
    employee_no = st.text_input("Employee No.")
    station = st.text_input("Station")
    department = st.text_input("Department")
    material_name = st.text_input("Material Name")
    material_code = st.text_input("Material Code")
    quantity = st.number_input("Quantity", min_value=1)
    defect_description = st.text_area("Defect Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

    if st.button("Submit"):
        add_request(st.session_state['username'], name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority)
        st.success("Repair request submitted successfully")

# Training Request Form
def training_request_form():
    st.header("Submit Training Request")
    name = st.text_input("Name")
    employee_no = st.text_input("Employee No.")
    station = st.text_input("Station")
    designation = st.text_input("Designation")
    training_slot = st.date_input("Available Training Slot")

    if st.button("Submit Training Request"):
        add_training_request(st.session_state['username'], name, employee_no, station, designation, training_slot)
        st.success("Training request submitted successfully")

# View Repair Status and Provide Feedback
def view_repair_status_and_feedback():
    st.header("View Repair Status and Provide Feedback")
    requests = get_requests(st.session_state['username'])

    if requests:
        for req in requests:
            st.markdown(f"**Request ID:** {req[0]}")
            st.markdown(f"**Material:** {req[6]}")
            st.markdown(f"**Quantity:** {req[7]}")
            st.markdown(f"**Defect Description:** {req[9]}")
            st.markdown(f"**Priority:** {req[10]}")
            st.markdown(f"**Status:** {req[11]}")

            if req[11] == "Completed":
                st.markdown("### Provide Feedback")
                feedback = st.text_area(f"Feedback for Request ID {req[0]}", key=f"feedback_{req[0]}")
                rating = st.slider(f"Rating for Request ID {req[0]} (1-5)", min_value=1, max_value=5, step=1, key=f"rating_{req[0]}")
                if st.button(f"Submit Feedback for Request ID {req[0]}", key=f"submit_feedback_{req[0]}"):
                    add_feedback(st.session_state['username'], req[0], feedback, rating)
                    st.success(f"Feedback submitted for Request ID {req[0]}")
            st.markdown("---")
    else:
        st.info("No repair requests found.")

# Main Application
def main():
    if "auth_state" not in st.session_state:
        st.session_state.auth_state = False

    display_logo_and_heading()

    if not st.session_state.auth_state:
        login()
    else:
        if st.session_state['role'] == 'User':
            option = st.sidebar.radio("Navigation", ["Repair Request", "Training Request", "View Repair Status"])
            if option == "Repair Request":
                repair_request_form()
            elif option == "Training Request":
                training_request_form()
            elif option == "View Repair Status":
                view_repair_status_and_feedback()
        elif st.session_state['role'] == 'Admin':
            st.header("Admin Dashboard")
            admin_update_request_status()

if __name__ == "__main__":
    main()
