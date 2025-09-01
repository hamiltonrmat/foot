import streamlit as st
import pandas as pd

# --- Configuration et Données Initiales ---

st.set_page_config(page_title="Générateur d'Équipes de Futsal", layout="wide")

# Dictionnaire pour mapper les codes aux positions complètes
POSITION_MAP = {'A': 'Attaquant', 'D': 'Défenseur', 'P': 'Polyvalent'}
# Dictionnaire inversé pour l'affichage
POSITION_MAP_INV = {v: k for k, v in POSITION_MAP.items()}

# Liste des joueurs réguliers
REGULAR_PLAYERS = [
    {'nom': 'Hamilton', 'note': 5, 'position': POSITION_MAP['P']},
    {'nom': 'Ariel', 'note': 5, 'position': POSITION_MAP['P']},
    {'nom': 'Olivier', 'note': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Raoul', 'note': 1, 'position': POSITION_MAP['A']},
    {'nom': 'Marcouille', 'note': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Marco', 'note': 4, 'position': POSITION_MAP['A']},
    {'nom': 'Daniel', 'note': 4, 'position': POSITION_MAP['D']},
    {'nom': 'Tijani', 'note': 4, 'position': POSITION_MAP['P']},
    {'nom': 'Hamid', 'note': 4, 'position': POSITION_MAP['A']},
    {'nom': 'Lucas', 'note': 5, 'position': POSITION_MAP['P']},
    {'nom': 'Corentin', 'note': 4, 'position': POSITION_MAP['P']},
    {'nom': 'Jean-Luc', 'note': 4, 'position': POSITION_MAP['D']},
    {'nom': 'Thomas', 'note': 3, 'position': POSITION_MAP['P']},
    {'nom': 'Gabriel', 'note': 2, 'position': POSITION_MAP['D']},
    {'nom': 'Antoine', 'note': 3, 'position': POSITION_MAP['P']},
    {'nom': 'Emile', 'note': 2, 'position': POSITION_MAP['P']},
    {'nom': 'Arnaud', 'note': 4, 'position': POSITION_MAP['P']},
]

# Initialisation du session_state pour les joueurs invités
if 'guest_players' not in st.session_state:
    st.session_state.guest_players = []

# --- Fonctions de l'Algorithme (inchangées) ---

def calculate_team_stats(team):
    if not team: return 0
    return sum(player['note'] for player in team)

def create_balanced_teams(players, num_teams, players_per_team):
    teams = [[] for _ in range(num_teams)]
    
    attackers = sorted([p for p in players if p['position'] == 'Attaquant'], key=lambda x: x['note'], reverse=True)
    defenders = sorted([p for p in players if p['position'] == 'Défenseur'], key=lambda x: x['note'], reverse=True)
    versatile = sorted([p for p in players if p['position'] == 'Polyvalent'], key=lambda x: x['note'], reverse=True)
    
    # Distribution pour contraintes de position
    for i in range(num_teams):
        if attackers: teams[i].append(attackers.pop(0))
        elif versatile: teams[i].append(versatile.pop(0))
        else:
            st.error("Pas assez d'attaquants ou de joueurs polyvalents pour former les équipes.")
            return None
            
        if defenders: teams[i].append(defenders.pop(0))
        elif versatile: teams[i].append(versatile.pop(0))
        else:
            st.error("Pas assez de défenseurs ou de joueurs polyvalents pour former les équipes.")
            return None

    # Distribution des joueurs restants pour équilibrer
    remaining_players = sorted(attackers + defenders + versatile, key=lambda x: x['note'], reverse=True)
    
    for player in remaining_players:
        team_notes = [calculate_team_stats(t) for t in teams]
        available_teams = []
        for i, team in enumerate(teams):
            if len(team) < players_per_team:
                available_teams.append((team_notes[i], i))
        
        if not available_teams: break
            
        available_teams.sort()
        target_team_index = available_teams[0][1]
        teams[target_team_index].append(player)
        
    return teams


# --- Interface Streamlit ---

st.title("⚽ Générateur d'Équipes de Futsal")

# --- BARRE LATÉRALE DE CONFIGURATION ---
st.sidebar.header("⚙️ Paramètres de Match")
num_teams = st.sidebar.selectbox("Nombre d'équipes", options=[2, 3], index=0)
players_per_team = st.sidebar.selectbox("Nombre de joueurs par équipe", options=[4, 5, 6], index=1)
total_players_needed = num_teams * players_per_team
st.sidebar.info(f"**Objectif : {total_players_needed} joueurs**")

# --- SÉLECTION DES JOUEURS ---
st.header("👤 Sélection des Joueurs Présents")

# 1. Joueurs Réguliers
st.subheader("Réguliers")
selected_regulars = []
cols = st.columns(3) # Affichage sur 3 colonnes pour la compacité
for i, player in enumerate(REGULAR_PLAYERS):
    with cols[i % 3]:
        is_present = st.checkbox(
            f"{player['nom']} (Note: {player['note']}, Pos: {POSITION_MAP_INV[player['position']]})", 
            key=f"player_{i}"
        )
        if is_present:
            selected_regulars.append(player)

st.markdown("---")

# 2. Joueurs Invités
st.subheader("Invités")
with st.form("guest_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    guest_name = col1.text_input("Nom de l'invité")
    guest_note = col2.number_input("Note", min_value=1, max_value=5, step=1, value=3)
    guest_pos_short = col3.selectbox("Position", options=list(POSITION_MAP.keys()))
    
    if st.form_submit_button("Ajouter l'invité"):
        if guest_name:
            st.session_state.guest_players.append({
                'nom': guest_name,
                'note': guest_note,
                'position': POSITION_MAP[guest_pos_short]
            })
            st.rerun()

# Afficher les invités ajoutés et permettre leur suppression
if st.session_state.guest_players:
    st.write("Liste des invités :")
    for i, player in enumerate(st.session_state.guest_players):
        col1, col2 = st.columns([4, 1])
        col1.write(f"- {player['nom']} (Note: {player['note']}, Pos: {POSITION_MAP_INV[player['position']]})")
        # Le bouton de suppression utilise l'index pour retirer l'élément de la liste
        if col2.button("❌", key=f"del_{i}"):
            st.session_state.guest_players.pop(i)
            st.rerun() # On utilise la nouvelle syntaxe pour forcer le rafraîchissement
            
st.markdown("---")

# --- COMPTEUR ET BOUTON DE GÉNÉRATION ---
total_players_selected = len(selected_regulars) + len(st.session_state.guest_players)

# Affichage du compteur avec un code couleur
if total_players_selected == total_players_needed:
    st.sidebar.success(f"**{total_players_selected} / {total_players_needed} joueurs sélectionnés** 👍")
else:
    st.sidebar.warning(f"**{total_players_selected} / {total_players_needed} joueurs sélectionnés**")


if st.button("🚀 Générer les équipes", type="primary", use_container_width=True):
    all_players = selected_regulars + st.session_state.guest_players
    
    if len(all_players) != total_players_needed:
        st.error(f"Le nombre de joueurs sélectionnés ({len(all_players)}) ne correspond pas au nombre requis ({total_players_needed}).")
    else:
        with st.spinner("Création des équipes en cours..."):
            teams = create_balanced_teams(all_players, num_teams, players_per_team)
        
        if teams:
            st.success("Les équipes ont été générées avec succès !")
            st.header("Équipes Formées")
            
            cols = st.columns(num_teams)
            team_notes = []

            for i, team in enumerate(teams):
                with cols[i]:
                    total_note = calculate_team_stats(team)
                    team_notes.append(total_note)
                    st.subheader(f"Équipe {i + 1} (Note: {total_note})")
                    
                    # Préparation pour un affichage propre
                    display_team = []
                    for p in team:
                        display_team.append({
                            'Nom': p['nom'],
                            'Note': p['note'],
                            'Pos': POSITION_MAP_INV[p['position']]
                        })
                    
                    df_team = pd.DataFrame(display_team)
                    st.dataframe(df_team, hide_index=True)
            
            # Résumé de l'équilibrage
            st.header("📊 Résumé de l'Équilibrage")
            if team_notes:
                min_note, max_note = min(team_notes), max(team_notes)
                st.metric(
                    label="Écart de note (max - min)",
                    value=f"{max_note - min_note}",
                    help="Plus ce chiffre est proche de 0, plus l'équilibre est parfait."
                )