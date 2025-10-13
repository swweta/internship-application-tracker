import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date

st.set_page_config(page_title="Internship Tracker", page_icon="💼", layout="wide")
DATA_FILE = "applications.csv"

# --- Initialize storage ---
if "data" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.data = pd.read_csv(DATA_FILE)
    else:
        st.session_state.data = pd.DataFrame(columns=["Company", "Role", "Location", "Date", "Status", "Mode", "Link"])

# Title
st.title("Internship Application Tracker")
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
        st.session_state.data.to_csv(DATA_FILE, index=False)

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
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success(f"✅ Deleted row {row_to_delete}")
            st.rerun()
else:
    st.info("No applications yet. Add your first one above!")

# Filter Applications section removed as requested

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
        file_name="applications.csv",
        mime="text/csv",
    )