import xml.etree.ElementTree as xtree
from utils.common import open_database

def export_db_xml(): 
    conn = open_database()
    cur = conn.cursor()
    filename = 'Chess.xml'
    root = xtree.Element("Chess")
    tables = ['Players', 'Clubs', 'Games', 'Tournaments', 'GameTurns', 'PlayersClubs', 'TournamentGames']  
    for table in tables:
        cur.execute(f'SELECT * FROM {table}')
        data = cur.fetchall()
        if table == 'Players':
            root.append(players_element(data))
        elif table == 'Clubs':
            root.append(clubs_element(data))
        elif table == "Games":
            root.append(games_element(data))
        elif table == 'Tournaments':
            root.append(tournaments_element(data))
        elif table == 'GameTurns':
            root.append(game_turns_element(data))
        elif table == 'PlayersClubs':
            root.append(players_clubs_element(data))
        else:
            root.append(tournament_games_element(data))
    tree = xtree.ElementTree(root)
    with open(filename, "wb") as xml_file:
        tree.write(xml_file)
    conn.close()

def players_element(players):
    element = xtree.Element("Players")
    for player in players:
        player_element = xtree.Element("Player")
        tag = xtree.SubElement(player_element, "PlayerId")
        tag.text = player[0] if player[0] != None else "NULL"
        tag = xtree.SubElement(player_element, "Username")
        tag.text = player[1] if player[1] != None else "NULL"
        tag = xtree.SubElement(player_element, "Name")
        tag.text = player[2] if player[2] != None else "NULL"
        tag = xtree.SubElement(player_element, "Title")
        tag.text = player[3] if player[3] != None else "NULL"
        tag = xtree.SubElement(player_element, "Country")
        tag.text = player[4] if player[4] != None else "NULL"
        tag = xtree.SubElement(player_element, "FIDE")
        tag.text = str(player[5]) if player[5] != None else "NULL"
        tag = xtree.SubElement(player_element, "DailyRating")
        tag.text = str(player[6]) if player[6] != None else "NULL"
        tag = xtree.SubElement(player_element, "RapidRating")
        tag.text = str(player[7]) if player[7] != None else "NULL"
        tag = xtree.SubElement(player_element, "BlitzRating")
        tag.text = str(player[8]) if player[8] != None else "NULL"
        tag = xtree.SubElement(player_element, "BulletRating")
        tag.text = str(player[9]) if player[9] != None else "NULL"

        element.append(player_element)

    return element

def clubs_element(clubs):
    element = xtree.Element("Clubs")
    for club in clubs:
        club_element = xtree.Element("Club")
        tag = xtree.SubElement(club_element, "ClubId")
        tag.text = club[0] if club[0] != None else "NULL"
        tag = xtree.SubElement(club_element, "Name")
        tag.text = club[1] if club[1] != None else "NULL"
        tag = xtree.SubElement(club_element, "Country")
        tag.text = club[2] if club[2] != None else "NULL"
        tag = xtree.SubElement(club_element, "URL")
        tag.text = club[3] if club[3] != None else "NULL"

        element.append(club_element)
    
    return element

def games_element(games):
    element = xtree.Element("Games")
    for game in games:
        game_element = xtree.Element("Game")
        tag = xtree.SubElement(game_element, "GameId")
        tag.text = str(game[0]) if game[0] != None else "NULL"
        tag = xtree.SubElement(game_element, "WhitePlayerId")
        tag.text = game[1] if game[1] != None else "NULL"
        tag = xtree.SubElement(game_element, "BlackPlayerId")
        tag.text = game[2] if game[2] != None else "NULL"
        tag = xtree.SubElement(game_element, "Date")
        tag.text = str(game[3]) if game[3] != None else "NULL"
        tag = xtree.SubElement(game_element, "TimeClass")
        tag.text = game[4] if game[4] != None else "NULL"
        tag = xtree.SubElement(game_element, "TimeControl")
        tag.text = game[5] if game[5] != None else "NULL"
        tag = xtree.SubElement(game_element, "Result")
        tag.text = game[6] if game[6] != None else "NULL"
        
        element.append(game_element)
    
    return element

def tournaments_element(tournaments):
    element = xtree.Element("Tournaments")
    for tournament in tournaments:
        tournament_element = xtree.Element("Tournament")
        tag = xtree.SubElement(tournament_element, "URLId")
        tag.text = tournament[0] if tournament[0] != None else "NULL"
        tag = xtree.SubElement(tournament_element, "Name")
        tag.text = tournament[1] if tournament[1] != None else "NULL"
        tag = xtree.SubElement(tournament_element, "TimeControl")
        tag.text = tournament[2] if tournament[2] != None else "NULL"
        tag = xtree.SubElement(tournament_element, "TimeClass")
        tag.text = tournament[3] if tournament[3] != None else "NULL"
        tag = xtree.SubElement(tournament_element, "IsRated")
        tag.text = str(tournament[4]) if tournament[4] != None else "NULL"
        tag = xtree.SubElement(tournament_element, "IsOfficial")
        tag.text = str(tournament[5]) if tournament[5] != None else "NULL"

        element.append(tournament_element)

    return element

def game_turns_element(game_turns):
    element = xtree.Element("GameTurns")
    for turn in game_turns:
        turn_element = xtree.Element("Turn")
        tag = xtree.SubElement(turn_element, "GameId")
        tag.text = str(turn[0]) if turn[0] != None else "NULL"
        tag = xtree.SubElement(turn_element, "Turn")
        tag.text = str(turn[1]) if turn[1] != None else "NULL"
        tag = xtree.SubElement(turn_element, "WhiteMove")
        tag.text = turn[2] if turn[2] != None else "NULL"
        tag = xtree.SubElement(turn_element, "BlackMove")
        tag.text = turn[3] if turn[3] != None else "NULL"
        
        element.append(turn_element)

    return element

def players_clubs_element(players_clubs):
    element = xtree.Element("PlayersClubs")
    for pc in players_clubs:
        pc_element = xtree.Element("PlayerClub")
        tag = xtree.SubElement(pc_element, "PlayerId")
        tag.text = pc[0] if pc[0] != None else "NULL"
        tag = xtree.SubElement(pc_element, "ClubId")
        tag.text = pc[1] if pc[1] != None else "NULL"
        
        element.append(pc_element)

    return element

def tournament_games_element(tournament_games):
    """
    `GameId` INT NOT NULL,
    `URLId` VARCHAR(150) NOT NULL,
    """
    element = xtree.Element("TournamentGames")
    for tg in tournament_games:
        tg_element = xtree.Element("TournamentGame")
        tag = xtree.SubElement(tg_element, "GameId")
        tag.text = str(tg[0]) if tg[0] != None else "NULL"
        tag = xtree.SubElement(tg_element, "URLId")
        tag.text = tg[1] if tg[1] != None else "NULL"
        
        element.append(tg_element)

    return element