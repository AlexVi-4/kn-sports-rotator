import streamlit as st
import random
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION ---
st.set_page_config(page_title="Padel Pro Manager", page_icon="🎾", layout="wide")

ADMIN_PASSWORD = "26022026"
USER_PASSWORD = "3698"
# Твоя ссылка на таблицу
GSHEET_URL = "https://docs.google.com/spreadsheets/d/15lGz2FjSIsA1vA8XshEAtu2Xo0VzX_z0-GzFhYvX-2o/edit?usp=sharing"

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- HELPER FUNCTIONS ---
def get_players():
    # Читаем список игроков из Google Sheets
    return conn.read(spreadsheet=GSHEET_URL, worksheet="Players", ttl=0)

def get_all_rotations():
    # Читаем все сохраненные игры
    return conn.read(spreadsheet=GSHEET_URL, worksheet="Rotations", ttl=0)

def login():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Padel Community Access")
        pwd = st.text_input("Enter Passcode:", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.role = 'admin'
                st.rerun()
            elif pwd == USER_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.role = 'user'
                st.rerun()
            else:
                st.error("Invalid Passcode")
        return False
    return True

# --- MAIN APP ---
if login():
    # 1. Загружаем данные
    players_df = get_players()
    all_rotations = get_all_rotations()
    
    # 2. Выбор даты (Пункт 3)
    st.title("🎾 Padel Match Day")
    selected_date = st.date_input("📅 Select Date to View or Create Rotation", date.today())
    date_str = str(selected_date)

    # Фильтруем данные из базы на выбранную дату
    daily_data = all_rotations[all_rotations['Date'] == date_str]

    # --- SIDEBAR (ADMIN ONLY) ---
    if st.session_state.role == 'admin':
        st.sidebar.title("🛠️ Admin Control")
        
        # Пункт 4: Кнопка генерации и инфо ПЕРЕД списком
        st.sidebar.subheader("Action Center")
        
        # Список имен для мультиселекта
        all_names = players_df['Name'].tolist()
        selected_names = st.sidebar.multiselect(
            f"Select Players (Total in DB: {len(all_names)})",
            options=all_names,
            help="Type to search player name"
        )
        
        count = len(selected_names)
        st.sidebar.write(f"**Selected for today: {count}**")

        if st.sidebar.button("🚀 Generate & Save Rotation", use_container_width=True):
            if count >= 4 and count % 4 == 0:
                # Логика генерации (упрощенная для примера)
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
                            "Team A": f"{g[0]['name']} & {g[1]['name']}",
                            "Team B": f"{g[2]['name']} & {g[3]['name']}"
                        })
                
                # Сохранение в Google Sheets
                new_df = pd.DataFrame(new_rows)
                updated_db = pd.concat([all_rotations, new_df], ignore_index=True)
                conn.update(spreadsheet=GSHEET_URL, worksheet="Rotations", data=updated_db)
                st.sidebar.success(f"Saved to Google Sheets for {date_str}!")
                st.rerun()
            else:
                st.sidebar.error("Please select a multiple of 4 players.")

        if st.sidebar.checkbox("Show Power Levels (Admin Only)"):
            st.sidebar.dataframe(players_df)
            
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # --- MAIN DISPLAY ---
    if not daily_data.empty:
        st.success(f"Confirmed rotation for {date_str}")
        # Пункт 1: Компактный табличный вид
        for r_name in daily_data['Round'].unique():
            st.subheader(f"📍 {r_name}")
            table_to_show = daily_data[daily_data['Round'] == r_name]
            st.table(table_to_show[['Court', 'Team A', 'Team B']].set_index('Court'))
    else:
        st.warning(f"No rotation found for {date_str}. Please contact Administrator.")

    if st.session_state.role == 'user':
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()