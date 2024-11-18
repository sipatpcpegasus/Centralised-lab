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

# Create tables for repair requests, blogs, and training requests
c.execute('''CREATE TABLE IF NOT EXISTS requests (
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
    status TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS blogs (
    author TEXT, 
    title TEXT, 
    content TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS training_requests (
    username TEXT, 
    name TEXT, 
    employee_no TEXT, 
    station TEXT, 
    designation TEXT, 
    available_slots TEXT, 
    status TEXT
)''')
conn.commit()

# Helper functions for database operations
def add_request(username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority):
    c.execute(
        "INSERT INTO requests (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority, 'Pending')
    )
    conn.commit()

def add_training_request(username, name, employee_no, station, designation, available_slots):
    c.execute(
        "INSERT INTO training_requests (username, name, employee_no, station, designation, available_slots, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
        (username, name, employee_no, station, designation, available_slots, 'Pending')
    )
    conn.commit()

def update_request_status(request_id, new_status):
    c.execute("UPDATE requests SET status = ? WHERE rowid = ?", (new_status, request_id))
    conn.commit()

def get_requests():
    c.execute("SELECT rowid, * FROM requests")
    return c.fetchall()

def get_user_requests(username):
    c.execute("SELECT rowid, * FROM requests WHERE username = ?", (username,))
    return c.fetchall()

def get_blogs():
    c.execute("SELECT * FROM blogs")
    return c.fetchall()

def add_blog(author, title, content):
    c.execute("INSERT INTO blogs (author, title, content) VALUES (?, ?, ?)", (author, title, content))
    conn.commit()

def get_training_requests():
    c.execute("SELECT rowid, * FROM training_requests")
    return c.fetchall()

def display_logo_and_heading():
    # Paths to logos
    ntpc_logo_path = "ntpc_logo.png"  
    elab_logo_path = "centralized_elab_logo.png"  

    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        if os.path.exists(ntpc_logo_path):
            st.image(ntpc_logo_path, use_column_width=False, width=150)
        else:
            st.warning("NTPC logo not found!")

    with col2:
        st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 200px;">
                <h1 style="text-align: center; font-size: 40px; color: #333;">NTPC Electronics Repair Lab</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        if os.path.exists(elab_logo_path):
            st.image(elab_logo_path, use_column_width=False, width=280)
        else:
            st.warning("Centralized E-Lab logo not found!")

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

# Main app
def main():
    if "auth_state" not in st.session_state:
        st.session_state.auth_state = False

    display_logo_and_heading()

    if not st.session_state.auth_state:
        login()
    else:
        if st.session_state['role'] == 'User':
            st.title(f"Welcome, {st.session_state['username']}")
            option = st.selectbox("Choose an option", ["Submit Repair Request", "Submit Training Request", "View Repair Status", "Provide Feedback", "View Blogs", "Post Blog"])

            if option == "Submit Repair Request":
                st.header("Repair Request Form")
                name = st.text_input("Name")
                employee_no = st.text_input("Employee No.")
                station = st.text_input("Station")
                department = st.text_input("Department")
                material_name = st.text_input("Material Name")
                material_code = st.text_input("Material Code")
                quantity = st.number_input("Quantity", min_value=1)
                defect_description = st.text_area("Defect Description")
                priority = st.selectbox("Priority", ["Low", "Medium", "High"])

                if st.button("Submit Request"):
                    add_request(st.session_state['username'], name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority)
                    st.success("Repair request submitted successfully")

            elif option == "Submit Training Request":
                st.header("Training Request Form")
                name = st.text_input("Name")
                employee_no = st.text_input("Employee No.")
                station = st.text_input("Station")
                designation = st.text_input("Designation")
                available_slots = st.text_area("Available Training Slots (Date and Time)")

                if st.button("Submit Training Request"):
                    add_training_request(st.session_state['username'], name, employee_no, station, designation, available_slots)
                    st.success("Training request submitted successfully")

            elif option == "View Repair Status":
                st.header("Repair Status")
                requests = get_user_requests(st.session_state['username'])
                for req in requests:
                    st.write(f"Request ID: {req[0]}")
                    st.write(f"Material: {req[6]} | Status: {req[11]}")
                    st.write("---")

            elif option == "Provide Feedback":
                st.header("Provide Feedback")
                st.text_area("Feedback")
                if st.button("Submit Feedback"):
                    st.success("Feedback submitted successfully!")

        elif st.session_state['role'] == 'Admin':
            st.title(f"Welcome Admin, {st.session_state['username']}")
            st.header("Manage Repair Requests")
            requests = get_requests()
            for req in requests:
                st.write(f"Request ID: {req[0]} | Priority: {req[10]}")
                if st.button("Mark as Completed", key=req[0]):
                    update_request_status(req[0], "Completed")
                    st.success("Status updated successfully")

if __name__ == "__main__":
    main()
