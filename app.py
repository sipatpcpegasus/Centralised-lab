import streamlit as st
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

# Create tables
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

# Helper functions
def add_request(username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority):
    c.execute(
        "INSERT INTO requests (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        (username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority)
    )
    conn.commit()

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

def get_requests(username=None):
    if username:
        c.execute("SELECT * FROM requests WHERE username = ?", (username,))
    else:
        c.execute("SELECT * FROM requests")
    return c.fetchall()

def get_training_requests(username=None):
    if username:
        c.execute("SELECT * FROM training_requests WHERE username = ?", (username,))
    else:
        c.execute("SELECT * FROM training_requests")
    return c.fetchall()

def add_feedback(username, request_id, feedback, rating):
    c.execute(
        "INSERT INTO feedback (username, request_id, feedback, rating) VALUES (?, ?, ?, ?)", 
        (username, request_id, feedback, rating)
    )
    conn.commit()

def get_feedback():
    c.execute("SELECT * FROM feedback")
    return c.fetchall()

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

# Blogs and success stories on the login page
def show_blogs_on_login():
    st.markdown("<h2 style='text-align: center;'>Blogs and Success Stories</h2>", unsafe_allow_html=True)
    blogs = get_blogs()

    if blogs:
        for blog in blogs:
            st.markdown(f"<h4 style='text-align: center;'>{blog[2]}</h4>", unsafe_allow_html=True)  # Blog Title
            st.markdown(f"<p style='text-align: center; color: gray;'>By: {blog[1]}</p>", unsafe_allow_html=True)  # Author
            st.text_area("", value=blog[3], height=100, max_chars=200, key=f"blog_{blog[0]}", disabled=True)
            st.markdown("---")
    else:
        st.info("No blogs available. Start by posting the first blog!")

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

    # Display blogs and success stories
    show_blogs_on_login()

# Repair and Training Request Forms
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

    if st.button("Submit Repair Request"):
        add_request(st.session_state.username, name, employee_no, station, department, material_name, material_code, quantity, defect_description, priority)
        st.success("Repair Request Submitted!")

def training_request_form():
    st.header("Submit Training Request")
    name = st.text_input("Name")
    employee_no = st.text_input("Employee No.")
    station = st.text_input("Station")
    designation = st.text_input("Designation")
    training_slot = st.text_input("Available Training Slot (Date/Time)")

    if st.button("Submit Training Request"):
        add_training_request(st.session_state.username, name, employee_no, station, designation, training_slot)
        st.success("Training Request Submitted!")

# Main Application
def main():
    if "auth_state" not in st.session_state:
        st.session_state.auth_state = False

    display_logo_and_heading()

    if not st.session_state.auth_state:
        login()
    else:
        st.sidebar.title("Navigation")
        option = st.sidebar.radio("Choose an option", ["Repair Requests", "Training Requests", "Blogs"])

        if option == "Repair Requests":
            repair_request_form()
        elif option == "Training Requests":
            training_request_form()
        elif option == "Blogs":
            blog_option = st.radio("Choose an option", ["View Blogs", "Post Blog"])
            if blog_option == "View Blogs":
                view_blogs()
            elif blog_option == "Post Blog":
                submit_blog()

# Run the app
if __name__ == "__main__":
    main()
