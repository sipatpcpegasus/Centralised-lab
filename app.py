import streamlit as st
import pandas as pd
import sqlite3
import json

# Load credentials from credentials.json
def load_credentials():
    with open("credentials.json", "r") as file:
        return json.load(file)

credentials = load_credentials()

# Initialize SQLite database connection
conn = sqlite3.connect('repair_blog_db.db')
c = conn.cursor()

# Create tables for repair requests and blogs
c.execute('''CREATE TABLE IF NOT EXISTS requests (username TEXT, name TEXT, employee_no TEXT, station TEXT, department TEXT, material_name TEXT, material_code TEXT, quantity INTEGER, defect_description TEXT, priority TEXT, status TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS blogs (author TEXT, title TEXT, content TEXT)''')
conn.commit()

# Helper functions for database operations
def add_request(username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority):
    c.execute("INSERT INTO requests (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
              (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority, 'Pending'))
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

# Login functionality
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = next((u for u in credentials["users"] if u["username"] == username and u["password"] == password), None)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['role'] = user["role"]
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Invalid login credentials")

# Main app page based on role
def app():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        # Add custom CSS for positioning the logos and heading
        st.markdown("""
            <style>
            .logo-container-left {
                position: absolute;
                top: 10px;
                left: 10px;
                z-index: 9999;
            }
            .logo-container-right {
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 9999;
            }
            .heading {
                text-align: center;
                font-size: 30px;
                font-weight: bold;
                margin-top: 50px;
            }
            .login-heading {
                position: absolute;
                top: 30%;
                left: 50%;
                transform: translateX(-50%);
            }
            </style>
        """, unsafe_allow_html=True)

        # Add the logos and heading
        st.markdown('<div class="logo-container-left"><img src="ntpc_logo.png" width="100"></div>', unsafe_allow_html=True)
        st.markdown('<div class="logo-container-right"><img src="centralized_elab_logo.png" width="100"></div>', unsafe_allow_html=True)

        if not st.session_state['logged_in']:
            st.markdown('<div class="login-heading"><h1>NTPC Electronics Repair Lab</h1></div>', unsafe_allow_html=True)

        if st.session_state['role'] == 'User':
            st.title(f"Welcome, {st.session_state['username']}")
            option = st.selectbox("Choose an option", ["Submit Repair Request", "View Blogs", "Post Blog"])

            if option == "Submit Repair Request":
                # Repair Request Form
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
                st.subheader(f"Issue: {req[1]} (Status: {req[3]})")
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
    else:
        login()

if __name__ == "__main__":
    app()
