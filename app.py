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

# Create tables for repair requests and blogs
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
conn.commit()

# Helper functions for database operations
def add_request(username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority):
    c.execute(
        "INSERT INTO requests (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority, 'Pending')
    )
    conn.commit()

def get_requests():
    c.execute("SELECT * FROM requests")
    return c.fetchall()

def add_blog(author, title, content):
    c.execute("INSERT INTO blogs (author, title, content) VALUES (?, ?, ?)", (author, title, content))
    conn.commit()

def get_blogs():
    c.execute("SELECT * FROM blogs")
    return c.fetchall()

# Display logos and heading
def display_logo_and_heading():
    logo_path = "ntpc_logo.png"  # Path to NTPC logo
    big_image_path = "centralized_elab_logo.png"  # Path to centralized lab logo

    col1, col2 = st.columns([1, 6])  # Layout proportions
    with col1:
        if os.path.exists(logo_path):
            st.image(logo_path, use_column_width=True)
        else:
            st.warning("NTPC logo not found!")

    with col2:
        if os.path.exists(big_image_path):
            st.image(big_image_path, use_column_width=True)
        else:
            st.warning("Centralized E-Lab logo not found!")

    st.markdown("<h1 style='text-align: center;'>NTPC Electronics Repair Lab</h1>", unsafe_allow_html=True)

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

# Main app page based on role
def main():
    if "auth_state" not in st.session_state:
        st.session_state.auth_state = False

    # Display logos and heading on every page
    display_logo_and_heading()

    if not st.session_state.auth_state:
        login()
    else:
        if st.session_state['role'] == 'User':
            st.title(f"Welcome, {st.session_state['username']}")
            option = st.selectbox("Choose an option", ["Submit Repair Request", "View Blogs", "Post Blog"])

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

                if st.button("Submit"):
                    add_request(st.session_state['username'], name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority)
                    st.success("Request submitted successfully")

            elif option == "View Blogs":
                st.header("Blogs")
                blogs = get_blogs()
                for blog in blogs:
                    st.subheader(blog[1])
                    st.write(f"By: {blog[0]}")
                    st.write(blog[2])
                    st.write("---")

            elif option == "Post Blog":
                st.header("Post a Blog")
                title = st.text_input("Blog Title")
                content = st.text_area("Blog Content")
                if st.button("Post"):
                    add_blog(st.session_state['username'], title, content)
                    st.success("Blog posted successfully")

        elif st.session_state['role'] == 'Admin':
            st.title(f"Welcome Admin, {st.session_state['username']}")
            st.header("View Repair Requests")
            requests = get_requests()
            for req in requests:
                st.subheader(f"Issue: {req[1]} (Status: {req[10]})")
                st.write(f"Submitted by: {req[0]}")
                st.write(f"Material: {req[5]} - Code: {req[6]}")
                st.write(f"Quantity: {req[7]} | Priority: {req[9]}")
                st.write(req[8])  # Defect Description
                st.write("---")
            
            st.header("Manage Blogs")
            option = st.selectbox("Manage", ["View Blogs", "Post Blog"])
            
            if option == "View Blogs":
                blogs = get_blogs()
                for blog in blogs:
                    st.subheader(blog[1])
                    st.write(f"By: {blog[0]}")
                    st.write(blog[2])
                    st.write("---")
            
            elif option == "Post Blog":
                title = st.text_input("Blog Title")
                content = st.text_area("Blog Content")
                if st.button("Post"):
                    add_blog(st.session_state['username'], title, content)
                    st.success("Blog posted successfully")

if __name__ == "__main__":
    main()
