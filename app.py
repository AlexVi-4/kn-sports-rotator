import streamlit as st
import random
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Padel Pro Manager", page_icon="🎾", layout="wide")

# Read passcodes securely from Streamlit Secrets / Environment Variables
ADMIN_PASSCODE = st.secrets.get("ADMIN_PASSCODE", "26022026")
USER_PASSCODE = st.secrets.get("USER_PASSCODE", "3698")

GSHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_players():
    return conn.read(spreadsheet=GSHEET_URL, worksheet="Players", ttl=0)

def get_all_rotations():
    return conn.read(spreadsheet=GSHEET_URL, worksheet="Rotations", ttl=0)

# --- AUTHORIZATION (Point 2 & 3) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'role' not in st.session_state:
    st.session_state.role = None

def login():
    if not st.session_state.authenticated:
        st.title("🔐 Padel Community Access")
        pwd = st.text_input("Enter Passcode:", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSCODE:
                st.session_state.authenticated = True
                st.session_state.role = 'admin'
                st.rerun()
            elif pwd == USER_PASSCODE:
                st.session_state.authenticated = True
                st.session_state.role = 'user'
                st.rerun()
            else:
                st.error("Invalid Passcode")
        return False
    return True

if login():
    players_df = get_players()
    all_rotations = get_all_rotations()
    
    st.title("🎾 Padel Match Day")
    selected_date = st.date_input("📅 Select Date", date.today())
    date_str = str(selected_date)

    daily_data = all_rotations[all_rotations['Date'] == date_str] if not all_rotations.empty else pd.DataFrame()

    # --- ADMIN SIDEBAR (Point 5 Layout Updates) ---
    if st.session_state.role == 'admin':
        st.sidebar.title("🛠️ Admin Control")
        
        all_names = players_df['Name'].tolist() if 'Name' in players_df.columns else []
        
        # 1. Player count BEFORE search bar
        selected_names = st.sidebar.session_state.get('selected_players_key', [])
        count = len(selected_names)
        st.sidebar.markdown(f"### Selected players: `{count}` / Total: `{len(all_names)}`")

        # 2. Generate button BEFORE search bar
        generate_btn = st.sidebar.button("🚀 Generate & Save Rotation", use_container_width=True)

        st.sidebar.divider()

        # 3. Searchable selection list filling down the sidebar
        selected_names = st.sidebar.multiselect(
            "Search and select players:",
            options=all_names,
            key='selected_players_key',
            help="Type player name to filter"
        )

        if generate_btn:
            if count >= 4 and count % 4 == 0:
                active_players = players_df[players_df['Name'].isin(selected_names)].to_dict('records')
                new_rows = []
                
                for r_num in range(1, 4):
                    random.shuffle(active_players)
                    for i in range(0, len(active_players), 4):
                        g = active_players[i:i+4]
                        new_rows.append({
                            "Date": date_str,
                            "Round": f"Round {r_num}",
                            "Court": f"Court {(i//4)+1}",
                            "Team A": f"{g[0]['Name']} & {g[1]['Name']}",
                            "Team B": f"{g[2]['Name']} & {g[3]['Name']}"
                        })
                
                new_df = pd.DataFrame(new_rows)
                updated_db = pd.concat([all_rotations, new_df], ignore_index=True) if not all_rotations.empty else new_df
                conn.update(spreadsheet=GSHEET_URL, worksheet="Rotations", data=updated_db)
                st.sidebar.success(f"Saved for {date_str}!")
                st.rerun()
            else:
                st.sidebar.error("Select a multiple of 4 players (8, 12, 16...).")

        if st.sidebar.checkbox("Show Power Levels (Admin Only)"):
            st.sidebar.dataframe(players_df)
            
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # --- MAIN CONTENT DISPLAY (Point 1 & 4 Table View) ---
    if not daily_data.empty:
        st.success(f"Schedule for {date_str}")
        for r_name in daily_data['Round'].unique():
            st.subheader(f"📍 {r_name}")
            table_to_show = daily_data[daily_data['Round'] == r_name]
            st.table(table_to_show[['Court', 'Team A', 'Team B']].set_index('Court'))
    else:
        st.warning(f"No rotation stored for {date_str}.")

    if st.session_state.role == 'user':
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()