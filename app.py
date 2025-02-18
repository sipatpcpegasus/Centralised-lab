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
def add_blog(author, title, content):
    c.execute("INSERT INTO blogs (author, title, content) VALUES (?, ?, ?)", (author, title, content))
    conn.commit()

def get_blogs():
    c.execute("SELECT author, title, content FROM blogs ORDER BY rowid DESC")
    return c.fetchall()

# Post Blog Section
def post_blog():
    st.header("Post a Blog")
    title = st.text_input("Blog Title")
    content = st.text_area("Blog Content")
    if st.button("Post"):
        if title and content:
            add_blog(st.session_state['username'], title, content)
            st.success("Blog posted successfully")
            st.experimental_rerun()  # Force rerun to show new post immediately
        else:
            st.error("Title and Content cannot be empty")

# View Blogs Section
def view_blogs():
    st.header("Blogs and Success Stories")
    blogs = get_blogs()
    if not blogs:
        st.info("No blogs posted yet.")
    for blog in blogs:
        st.subheader(blog[1])  # Blog title
        st.write(f"**By:** {blog[0]}")  # Author
        st.text_area("", value=blog[2], height=100, disabled=True)
        st.markdown("---")

# Main Execution
if __name__ == "__main__":
    if 'auth_state' not in st.session_state:
        st.session_state['auth_state'] = False

    if not st.session_state['auth_state']:
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user = next((u for u in credentials["users"] if u["username"] == username and u["password"] == password), None)
            if user:
                st.session_state['auth_state'] = True
                st.session_state['username'] = username
                st.session_state['role'] = user['role']
                st.sidebar.success(f"Logged in as {username}")
            else:
                st.sidebar.error("Invalid login credentials")
        view_blogs()
    else:
        if st.session_state['role'] == 'User':
            option = st.selectbox("Choose an option", ["View Blogs", "Post Blog"])
            if option == "View Blogs":
                view_blogs()
            elif option == "Post Blog":
                post_blog()
        elif st.session_state['role'] == 'Admin':
            option = st.selectbox("Choose an option", ["View Blogs", "Post Blog"])
            if option == "View Blogs":
                view_blogs()
            elif option == "Post Blog":
                post_blog()
