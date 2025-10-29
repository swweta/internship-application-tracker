import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date
import hashlib
import json

st.set_page_config(page_title="Internship Tracker", page_icon="💼", layout="wide")

# File paths
USERS_FILE = "users.json"
DATA_FOLDER = "user_data"

# Create data folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Initialize users file if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

# Helper Functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def get_user_data_file(username):
    """Get the data file path for a specific user"""
    return os.path.join(DATA_FOLDER, f"{username}_applications.csv")

def load_user_data(username):
    """Load data for a specific user"""
    file_path = get_user_data_file(username)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=["Company", "Role", "Location", "Date", "Status", "Mode", "Link"])

def save_user_data(username, data):
    """Save data for a specific user"""
    file_path = get_user_data_file(username)
    data.to_csv(file_path, index=False)

def signup_user(username, password, email):
    """Create a new user account"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists!"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters!"
    
    users[username] = {
        "password": hash_password(password),
        "email": email
    }
    save_users(users)
    return True, "Account created successfully!"

def login_user(username, password):
    """Authenticate user login"""
    users = load_users()
    
    if username not in users:
        return False, "Username not found!"
    
    if users[username]["password"] == hash_password(password):
        return True, "Login successful!"
    else:
        return False, "Incorrect password!"

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# Login/Signup Page
if not st.session_state.logged_in:
    st.title("🔐 Internship Application Tracker")
    st.markdown("**Secure your job search journey**")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary"):
            if login_username and login_password:
                success, message = login_user(login_username, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.data = load_user_data(login_username)
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all fields")
    
    with tab2:
        st.subheader("Create New Account")
        signup_username = st.text_input("Choose Username", key="signup_user")
        signup_email = st.text_input("Email Address", key="signup_email")
        signup_password = st.text_input("Choose Password (min 6 characters)", type="password", key="signup_pass")
        signup_password_confirm = st.text_input("Confirm Password", type="password", key="signup_pass_confirm")
        
        if st.button("Create Account", type="primary"):
            if signup_username and signup_email and signup_password and signup_password_confirm:
                if signup_password != signup_password_confirm:
                    st.error("Passwords don't match!")
                else:
                    success, message = signup_user(signup_username, signup_password, signup_email)
                    if success:
                        st.success(message)
                        st.info("Please login with your new account")
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields")
    st.stop()

# Load user's data
if "data" not in st.session_state or st.session_state.data is None:
    st.session_state.data = load_user_data(st.session_state.username)

# Header with logout button
col1, col2 = st.columns([4, 1])
with col1:
    st.title("Internship Application Tracker")
    st.markdown(f"Welcome back, **{st.session_state.username}**! 👋")
with col2:
    if st.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.data = None
        st.rerun()

st.markdown("Track your internship applications, filter them, and view simple analytics!")

# --- Input Form ---
with st.form("add_form"):
    company = st.text_input("Company Name")
    role = st.text_input("Role / Position")
    
    # All US states + Remote
    location_options = ["Remote", "Alabama", "Alaska", "Arizona", "Arkansas", "California", 
                       "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", 
                       "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", 
                       "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", 
                       "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", 
                       "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", 
                       "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", 
                       "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", 
                       "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
                       "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
    location = st.selectbox("Location", location_options)
    
    app_date = st.date_input("Application Date")
    
    # Searchable status dropdown
    status = st.selectbox(
        "Application Status", 
        ["Applied", "Interview", "Offer", "Rejected", "Pending"],
        help="Select or type to search"
    )
    
    mode = st.selectbox("Application Mode", ["Online", "Hybrid", "In-Person"])
    
    application_link = st.text_input("Application Link (URL)", placeholder="https://example.com/job-posting")
    
    submitted = st.form_submit_button("Add Application")

if submitted:
    # Validate all fields are filled
    if not company or not role or not location:
        st.error("⚠️ Please fill in all fields (Company, Role, and Location are required)")
    else:
        new_entry = {
            "Company": company, 
            "Role": role, 
            "Location": location, 
            "Date": app_date, 
            "Status": status, 
            "Mode": mode,
            "Link": application_link
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
        st.success("✅ Application Added!")
        save_user_data(st.session_state.username, st.session_state.data)

# --- View Table ---
st.subheader("📁 All Applications")
if not st.session_state.data.empty:
    # Add row numbers and delete button
    display_data = st.session_state.data.copy()
    display_data.insert(0, 'Number', range(1, len(display_data) + 1))
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**Delete Row**")
        row_to_delete = st.number_input("Enter row number to delete", min_value=1, max_value=len(st.session_state.data), step=1, key="delete_input")
        if st.button("🗑️ Delete", type="primary"):
            st.session_state.data = st.session_state.data.drop(st.session_state.data.index[row_to_delete - 1]).reset_index(drop=True)
            save_user_data(st.session_state.username, st.session_state.data)
            st.success(f"✅ Deleted row {row_to_delete}")
            st.rerun()
else:
    st.info("No applications yet. Add your first one above!")

# --- Visualization: Horizontal Bar Chart (Mode vs Applications) ---
st.subheader("📊 Mode vs Application Status")

if not st.session_state.data.empty:
    # Count applications by mode
    mode_counts = st.session_state.data["Mode"].value_counts()

    # --- Plot Horizontal Bar Chart ---
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Define colors for each mode
    colors_map = {
        "In-Person": "#FFA500",  # Orange
        "Hybrid": "#DC143C",      # Red
        "Online": "#1E90FF"       # Blue
    }
    colors = [colors_map.get(mode, "#808080") for mode in mode_counts.index]
    
    # Create horizontal bar chart
    bars = ax.barh(mode_counts.index, mode_counts.values, color=colors, height=0.25)

    # --- Styling ---
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlabel("No. of Applications", fontsize=11, fontweight="bold", color="#333333")
    ax.set_ylabel("")
    ax.set_title("Application Mode Distribution", fontsize=12, fontweight="bold", pad=15, color="#333333")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(2)
    ax.spines["bottom"].set_linewidth(2)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    
    # Add value labels at the end of bars
    for i, (mode, count) in enumerate(zip(mode_counts.index, mode_counts.values)):
        ax.text(count + 0.1, i, str(int(count)), va="center", fontsize=10, fontweight="bold", color="#333333")

    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("Add some internship data first to view this chart.")

# --- Download Data as CSV ---
if not st.session_state.data.empty:
    st.download_button(
        label="⬇️ Download Applications as CSV",
        data=st.session_state.data.to_csv(index=False).encode("utf-8"),
        file_name=f"{st.session_state.username}_applications.csv",
        mime="text/csv",
    )
