import streamlit as st
import random
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sports Rotator Pro", page_icon="🎾", layout="wide")

def load_players():
    players = []
    if os.path.exists("players.txt"):
        with open("players.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "," in line:
                    name, score = line.strip().split(",")
                    players.append({"name": name.strip(), "score": int(score.strip())})
    return sorted(players, key=lambda x: x['name'])

def generate_rotation(selected_players):
    played_together = set()
    all_rounds_data = []
    
    for round_num in range(1, 4):
        success = False
        temp_pairs = []
        
        # Try to assemble a round (up to 300 attempts)
        for _ in range(300):
            pool = selected_players[:]
            random.shuffle(pool)
            round_pairs = []
            temp_history = played_together.copy()
            possible = True
            
            while len(pool) >= 2:
                p1 = pool.pop(0)
                found = False
                for i in range(len(pool)):
                    pair = tuple(sorted([p1['name'], pool[i]['name']]))
                    if pair not in temp_history:
                        p2 = pool.pop(i)
                        round_pairs.append((p1, p2))
                        temp_history.add(pair)
                        found = True
                        break
                if not found:
                    possible = False
                    break
            
            if possible and len(pool) < 2:
                played_together = temp_history
                temp_pairs = round_pairs
                success = True
                break
        
        all_rounds_data.append((round_num, temp_pairs))
    return all_rounds_data

# --- INTERFACE ---
st.title("🏆 Sports Community Rotator")

players_data = load_players()
names = [p['name'] for p in players_data]

st.sidebar.header("Settings")
selected_names = st.sidebar.multiselect("Select players for today:", names)

# Improved counter
count = len(selected_names)
if count == 12:
    st.sidebar.success(f"✅ Perfect: {count} players selected")
elif count > 0 and count % 4 == 0:
    st.sidebar.info(f"✅ Ready: {count} players ({count // 4} courts)")
else:
    st.sidebar.warning(f"⚠️ Selected: {count}. Need a multiple of 4 (8, 12, 16...)")

# Generate button
if st.sidebar.button("Generate Rotation", disabled=(count < 2)):
    if count % 2 != 0:
        st.error("Error: The number of players must be even!")
    else:
        active_players = [p for p in players_data if p['name'] in selected_names]
        results = generate_rotation(active_players)
        
        for r_num, pairs in results:
            st.markdown(f"## 📍 ROUND {r_num}")
            # Sort pairs by skill for balanced matches
            pairs.sort(key=lambda x: x[0]['score'] + x[1]['score'], reverse=True)
            
            # Dynamic court generation
            num_courts = len(pairs) // 2
            if num_courts > 0:
                cols = st.columns(num_courts)
                for court_idx in range(num_courts):
                    with cols[court_idx]:
                        st.subheader(f"🏟️ COURT {court_idx + 1}")
                        t1, t2 = pairs[court_idx * 2], pairs[court_idx * 2 + 1]
                        
                        score1 = t1[0]['score'] + t1[1]['score']
                        score2 = t2[0]['score'] + t2[1]['score']
                        
                        st.info(f"**Team A** (Power: {score1})\n\n{t1[0]['name']} + {t1[1]['name']}")
                        st.write("🆚")
                        st.warning(f"**Team B** (Power: {score2})\n\n{t2[0]['name']} + {t2[1]['name']}")
            else:
                # For 1 pair only (2 vs 2)
                st.info(f"🤝 Training Match: {pairs[0][0]['name']} + {pairs[0][1]['name']}")
            st.divider()