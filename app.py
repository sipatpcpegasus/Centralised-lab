import streamlit as st
import pandas as pd
import sqlite3
import json
import os
import time

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

# Success stories data
success_stories = [
    {
        "title": "Success Story 1: ATT System Repair",
        "content": "NTPC's repair team restored the ATT system in Stage-1, saving 19 lakh and ensuring turbine protection system health monitoring. 19 faulty current sensing transducers were repaired in-house."
    },
    {
        "title": "Success Story 2: Ventilator Repair during COVID-19",
        "content": "During the COVID-19 pandemic, NTPC's repair lab restored two ventilators at NTPC and one at a district hospital. This effort supported critical healthcare needs and earned appreciation from the District Collector."
    },
    {
        "title": "Success Story 3: ABB IMASI23 Card Repair",
        "content": "NTPC repaired IMASI23 cards for the control system, saving 1.56 crore in replacement costs. With a 95% success rate, the lab ensures high system reliability and significant cost savings."
    }
]

# Display logos and heading
def display_logo_and_heading():
    ntpc_logo_path = "ntpc_logo.png"  
    elab_logo_path = "centralized_elab_logo.png"  

    col1, col2, col3 = st.columns([1, 5, 1])  # Columns for layout

    with col1:
        if os.path.exists(ntpc_logo_path):
            st.image(ntpc_logo_path, use_column_width=False, width=120)  # NTPC logo
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
            st.image(elab_logo_path, use_column_width=False, width=180)  # Smaller E-Lab logo
        else:
            st.warning("Centralized E-Lab logo not found!")

# Auto-scrolling success stories display using st.empty()
def display_success_stories():
    st.markdown("<h2 style='text-align: center;'>Success Stories</h2>", unsafe_allow_html=True)

    # Create an empty container for success stories that will be updated
    story_container = st.empty()

    # Loop through stories and update the container with a delay to simulate scrolling
    while True:
        for story in success_stories:
            story_container.markdown(
                f"""
                <h3>{story['title']}</h3>
                <p>{story['content']}</p>
                """,
                unsafe_allow_html=True
            )
            time.sleep(5)  # Delay for 5 seconds before showing the next story
            story_container.empty()  # Clear the container before showing the next one

# Main app page based on role
def main():
    if "auth_state" not in st.session_state:
        st.session_state.auth_state = False

    # Display logos and heading on every page
    display_logo_and_heading()

    # Display success stories in a scrolling section
    display_success_stories()

if __name__ == "__main__":
    main()
