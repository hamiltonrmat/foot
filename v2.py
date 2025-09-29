import streamlit as st
import pandas as pd

# --- Configuration et Données Initiales ---

st.set_page_config(page_title="Futsal Langevin", layout="wide")

# Dictionnaire pour mapper les codes aux positions complètes
POSITION_MAP = {'A': 'Attaquant', 'D': 'Défenseur', 'P': 'Polyvalent'}
# Dictionnaire inversé pour l'affichage
POSITION_MAP_INV = {v: k for k, v in POSITION_MAP.items()}

# Liste des joueurs réguliers avec notes détaillées
REGULAR_PLAYERS = [
    {'nom': 'Antoine', 'attaque': 2, 'defense': 3, 'endurance': 4, 'position': POSITION_MAP['P']},
    {'nom': 'Arnaud', 'attaque': 3, 'defense': 3, 'endurance': 4, 'position': POSITION_MAP['A']},
    {'nom': 'Ariel', 'attaque': 5, 'defense': 5, 'endurance': 5, 'position': POSITION_MAP['P']},
    {'nom': 'Corentin', 'attaque': 5, 'defense': 4, 'endurance': 5, 'position': POSITION_MAP['P']},
    {'nom': 'Daniel', 'attaque': 2, 'defense': 5, 'endurance': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Emile', 'attaque': 2, 'defense': 3, 'endurance': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Gabriel', 'attaque': 1, 'defense': 4, 'endurance': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Hamid', 'attaque': 5, 'defense': 2, 'endurance': 3, 'position': POSITION_MAP['A']},
    {'nom': 'Hamilton', 'attaque': 5, 'defense': 4, 'endurance': 4, 'position': POSITION_MAP['P']},
    {'nom': 'Jean-Luc', 'attaque': 1, 'defense': 4, 'endurance': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Lucas', 'attaque': 5, 'defense': 5, 'endurance': 5, 'position': POSITION_MAP['P']},
    {'nom': 'Marcouille', 'attaque': 2, 'defense': 4, 'endurance': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Marco IT', 'attaque': 4, 'defense': 2, 'endurance': 3, 'position': POSITION_MAP['A']},
    {'nom': 'Olivier', 'attaque': 2, 'defense': 5, 'endurance': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Raoul', 'attaque': 1, 'defense': 2, 'endurance': 3, 'position': POSITION_MAP['A']},
    {'nom': 'Romain', 'attaque': 2, 'defense': 4, 'endurance': 3, 'position': POSITION_MAP['D']},
    {'nom': 'Tijani', 'attaque': 4, 'defense': 3, 'endurance': 3, 'position': POSITION_MAP['P']},
    {'nom': 'Thomas', 'attaque': 3, 'defense': 3, 'endurance': 3, 'position': POSITION_MAP['P']},
    {'nom': 'Etudiant1', 'attaque': 3, 'defense': 3, 'endurance': 3, 'position': POSITION_MAP['P']},
    {'nom': 'Etudiant2', 'attaque': 3, 'defense': 3, 'endurance': 3, 'position': POSITION_MAP['P']},
    {'nom': 'Etudiant3', 'attaque': 3, 'defense': 3, 'endurance': 3, 'position': POSITION_MAP['P']}
]

# Initialisation du session_state pour les joueurs invités
if 'guest_players' not in st.session_state:
    st.session_state.guest_players = []

# --- Fonctions de l'Algorithme ---

def calculate_team_stats(team):
    """Calcule les statistiques totales d'une équipe"""
    if not team:
        return {'total': 0, 'attaque': 0, 'defense': 0, 'endurance': 0}
    
    stats = {
        'attaque': sum(player['attaque'] for player in team),
        'defense': sum(player['defense'] for player in team),
        'endurance': sum(player['endurance'] for player in team)
    }
    stats['total'] = stats['attaque'] + stats['defense'] + stats['endurance']
    return stats

def get_player_total(player):
    """Calcule la note totale d'un joueur"""
    return player['attaque'] + player['defense'] + player['endurance']

def create_balanced_teams(players, num_teams, players_per_team):
    teams = [[] for _ in range(num_teams)]
    
    # Séparation par position et tri par note totale
    attackers = sorted([p for p in players if p['position'] == 'Attaquant'], 
                      key=get_player_total, reverse=True)
    defenders = sorted([p for p in players if p['position'] == 'Défenseur'], 
                      key=get_player_total, reverse=True)
    versatile = sorted([p for p in players if p['position'] == 'Polyvalent'], 
                      key=get_player_total, reverse=True)
    
    # Distribution pour contraintes de position (1 attaquant et 1 défenseur minimum par équipe)
    for i in range(num_teams):
        if attackers:
            teams[i].append(attackers.pop(0))
        elif versatile:
            teams[i].append(versatile.pop(0))
        else:
            st.error("Pas assez d'attaquants ou de joueurs polyvalents pour former les équipes.")
            return None
            
        if defenders:
            teams[i].append(defenders.pop(0))
        elif versatile:
            teams[i].append(versatile.pop(0))
        else:
            st.error("Pas assez de défenseurs ou de joueurs polyvalents pour former les équipes.")
            return None

    # Distribution des joueurs restants pour équilibrer
    remaining_players = sorted(attackers + defenders + versatile, 
                              key=get_player_total, reverse=True)
    
    for player in remaining_players:
        team_stats = [calculate_team_stats(t) for t in teams]
        available_teams = []
        
        for i, team in enumerate(teams):
            if len(team) < players_per_team:
                available_teams.append((team_stats[i]['total'], i))
        
        if not available_teams:
            break
            
        available_teams.sort()
        target_team_index = available_teams[0][1]
        teams[target_team_index].append(player)
        
    return teams


# --- Interface Streamlit ---

st.title("⚽ Futsal Langevin")

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
cols = st.columns(3)
for i, player in enumerate(REGULAR_PLAYERS):
    with cols[i % 3]:
        total = get_player_total(player)
        is_present = st.checkbox(
            f"{player['nom']} (Total: {total}, Pos: {POSITION_MAP_INV[player['position']]})", 
            key=f"player_{i}",
            help=f"Attaque: {player['attaque']}, Défense: {player['defense']}, Endurance: {player['endurance']}"
        )
        if is_present:
            selected_regulars.append(player)

st.markdown("---")
st.markdown("⚠️ Attention: le nombre de joueurs doit être égal à: (nb. d'équipes) x (nb. de joueurs p/ équipe)")

# 2. Joueurs Invités
st.subheader("Invités")
with st.form("guest_form", clear_on_submit=True):
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    guest_name = col1.text_input("Nom de l'invité")
    guest_attaque = col2.number_input("Attaque", min_value=1, max_value=5, step=1, value=3)
    guest_defense = col3.number_input("Défense", min_value=1, max_value=5, step=1, value=3)
    guest_endurance = col4.number_input("Endurance", min_value=1, max_value=5, step=1, value=3)
    guest_pos_short = col5.selectbox("Pos", options=list(POSITION_MAP.keys()))
    
    if st.form_submit_button("Ajouter l'invité"):
        if guest_name:
            st.session_state.guest_players.append({
                'nom': guest_name,
                'attaque': guest_attaque,
                'defense': guest_defense,
                'endurance': guest_endurance,
                'position': POSITION_MAP[guest_pos_short]
            })
            st.rerun()

# Afficher les invités ajoutés et permettre leur suppression
if st.session_state.guest_players:
    st.write("Liste des invités :")
    for i, player in enumerate(st.session_state.guest_players):
        col1, col2 = st.columns([4, 1])
        total = get_player_total(player)
        col1.write(f"- {player['nom']} (ATT: {player['attaque']}, DEF: {player['defense']}, END: {player['endurance']}, Total: {total}, Pos: {POSITION_MAP_INV[player['position']]})")
        if col2.button("❌", key=f"del_{i}"):
            st.session_state.guest_players.pop(i)
            st.rerun()
            
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
            all_team_stats = []

            for i, team in enumerate(teams):
                with cols[i]:
                    stats = calculate_team_stats(team)
                    all_team_stats.append(stats)
                    
                    st.subheader(f"Équipe {i + 1}")
                    st.metric(label="Note Totale", value=stats['total'])
                    
                    # Affichage des stats par catégorie
                    subcols = st.columns(3)
                    subcols[0].metric("⚔️ Attaque", stats['attaque'])
                    subcols[1].metric("🛡️ Défense", stats['defense'])
                    subcols[2].metric("⚡ Endurance", stats['endurance'])
                    
                    st.markdown("---")
                    
                    # Préparation pour un affichage propre
                    display_team = []
                    for p in team:
                        display_team.append({
                            'Nom': p['nom'],
                            'ATT': p['attaque'],
                            'DEF': p['defense'],
                            'END': p['endurance'],
                            'Total': get_player_total(p),
                            'Pos': POSITION_MAP_INV[p['position']]
                        })
                    
                    df_team = pd.DataFrame(display_team)
                    st.dataframe(df_team, hide_index=True, use_container_width=True)
            
            # Résumé de l'équilibrage
            st.header("📊 Résumé de l'Équilibrage")
            
            # Calcul des écarts
            totals = [s['total'] for s in all_team_stats]
            attaques = [s['attaque'] for s in all_team_stats]
            defenses = [s['defense'] for s in all_team_stats]
            endurances = [s['endurance'] for s in all_team_stats]
            
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric(
                label="Écart Total",
                value=f"{max(totals) - min(totals)}",
                help="Différence entre l'équipe la plus forte et la plus faible"
            )
            col2.metric(
                label="Écart Attaque",
                value=f"{max(attaques) - min(attaques)}"
            )
            col3.metric(
                label="Écart Défense",
                value=f"{max(defenses) - min(defenses)}"
            )
            col4.metric(
                label="Écart Endurance",
                value=f"{max(endurances) - min(endurances)}"
            )
