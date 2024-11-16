import streamlit as st
import pandas as pd
import sqlite3

# Initialize SQLite database connection
conn = sqlite3.connect('repair_blog_db.db')
c = conn.cursor()

# Create tables for users, repair requests, and blogs
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS requests (username TEXT, issue TEXT, details TEXT, status TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS blogs (author TEXT, title TEXT, content TEXT)''')
conn.commit()

# Helper functions for database operations
def create_user(username, password, role):
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()

def check_user(username, password):
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()

def add_request(username, issue, details):
    c.execute("INSERT INTO requests (username, issue, details, status) VALUES (?, ?, ?, ?)", (username, issue, details, 'Pending'))
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
    role = st.sidebar.radio("Role", ("User", "Admin"))

    if st.sidebar.button("Login"):
        user = check_user(username, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['role'] = role
            st.sidebar.success(f"Logged in as {username}")
        else:
            st.sidebar.error("Invalid login credentials")

# Main app page based on role
def app():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if st.session_state['logged_in']:
        if st.session_state['role'] == 'User':
            st.title(f"Welcome, {st.session_state['username']}")
            option = st.selectbox("Choose an option", ["Submit Repair Request", "View Blogs", "Post Blog"])

            if option == "Submit Repair Request":
                issue = st.text_input("Issue Title")
                details = st.text_area("Issue Details")
                if st.button("Submit"):
                    add_request(st.session_state['username'], issue, details)
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
                st.write(req[2])
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
