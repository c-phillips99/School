import requests
import json
import mysql.connector
import os
import pandas as pd
from tabulate import tabulate
from utils.process_data import *
from utils.sql import *
from utils.common import *
from utils.pgn_parser import add_games_to_db
from utils.export import export_db_xml

## TODO: Make a web scraper that fetches pgn

# Variables
api_url = 'https://api.chess.com/pub/'

def add_player_to_db(username):
    # Add Player to DB
    player_url = api_url + f"player/{username}"
    player_data = get_data(player_url)
    table_data = process_player_data(player_data)
    sql = get_player_sql(table_data)
    res = execute_sql(sql)

    # Add the Player's clubs to DB
    player_id = player_data.get('player_id')
    add_player_clubs_to_db(player_id, player_url)

def add_player_clubs_to_db(player_id, player_url):
    clubs_url = player_url + "/clubs"
    clubs_data = get_data(clubs_url)
    clubs = clubs_data.get('clubs')
    counter = 1

    for club in clubs:
        print(f"Adding club {counter} of {len(clubs)}")
        # Get the club's url
        club_home_url = club.get('@id')
        club_api_tag = "club/" + club_home_url.split('/')[-1]
        club_url = api_url + club_api_tag

        # Get club data and process
        club_data = get_data(club_url)
        table_data = process_club_data(club_data, club_home_url)
        sql = get_club_sql(table_data)
        res = no_errors = execute_sql(sql)

        # Add to PlayersClubs table
        club_id, _, _, _ = table_data
        pc_sql = get_players_clubs_sql(player_id, club_id)
        res = execute_sql(pc_sql)
        counter += 1
    
if __name__ == "__main__":
    os.system ("cls")
    #TODO: Make user sign in on startup
    setup_db()

    # Initial mode selection
    mode = set_mode()
    first_time = True

    while True:     
        if mode == 'Tournament':
            os.system ("cls")
            print("Mode: Add Tournament\n\n")
            print("Please enter the url of the tournament you would like to enter (no support of arena tournaments at the moment). \nEnter a blank line to return to the main menu.\n")
            home_url = input("Tournament URL: ")
            if home_url == '':
                os.system ("cls")
                mode = set_mode()
                continue
            # Check if tournament already exists
            result = tournament_exists(home_url)
            if result == True:
                print("Tournament already exists.")
                os.system ("cls")
                mode = set_mode()
                continue
            else:
                print("Collecting data...")
                # Check if valid url
                is_valid = check_valid_url(home_url)
                no_errors = True
                if is_valid:
                    tag = "tournament/" + home_url.split('/')[-1]
                    url = api_url + tag
                    is_valid = check_valid_url(url)
                    if is_valid:
                        # Add tournament to database
                        data = get_data(url)
                        table_data = process_tournament_data(data)
                        sql = get_tournament_sql(table_data)
                        res = execute_sql(sql)
                        no_errors = res if no_errors == True else False

                        # Collect players in tournament
                        players = data.get('players')
                        if players != None:
                            counter = 1
                            for player in players:
                                print(f"Adding player {counter} of {len(players)}")
                                username = player.get('username')
                                if username != None:
                                    add_player_to_db(username)
                                else:
                                    print("Players could not be added.")
                                    continue
                                counter += 1
                        else:
                            print("Players could not be added.")
                            continue

                        # Collect games from tournament
                        print("Please specify the location of the tournament pgn (found at the tournament url). \nEnter a blank line to return to the main menu.\n")
                        file_location = input("File Path: ")
                        if file_location == '':
                            os.system ("cls")
                            mode = set_mode()
                            continue
                        try:
                            add_games_to_db(file_location, home_url)
                        except Exception as e:
                            print(f"The following error occured: {e}") 
                        print("\nAll games added! \nPress Enter to return the main menu.")
                        input("")
                        os.system ("cls")
                        mode = set_mode()
                    else:
                        print("Invalid URL.")
                        continue
                else:
                    print("Invalid URL.")
                    continue

        # Only works with players in the db right now. Will expand this.
        elif mode == 'Games':
            os.system ("cls")
            print("Mode: Add Games\n\n")
            print("Please specify the location of the tournament pgn (found at the tournament url). Enter a blank line to return to the main menu.")
            file_location = input("File Path: ")
            if file_location == '':
                os.system ("cls")
                mode = set_mode()
                continue
            print("\n\nDo these games belong to a tournament? Enter a blank line to return to the main menu.")
            tournament = input("Y/N: ").lower()
            if tournament == '':
                os.system ("cls")
                mode = set_mode()
                continue
            elif tournament == 'y':
                print("\n\nPlease enter the url of the tournament you would like to enter. \nEnter a blank line to return to the main menu.")
                home_url = input("Tournament URL: ")
                if home_url == '':
                    os.system ("cls")
                    mode = set_mode()
                    continue
                # Check if tournament already exists
                result = tournament_exists(home_url)
                if result == True: # tournament exists in db
                    try:
                        add_games_to_db(file_location, home_url)
                    except Exception as e:
                        print(f"The following error occured: {e}")
                    print("\nAll games added! \nPress Enter to return the main menu.")
                    input("")
                    os.system ("cls") 
                    mode = set_mode()
                    continue
                else:
                    print("Tournament not found.")
                    print("Collecting data...")
                    # Check if valid url
                    is_valid = check_valid_url(home_url)
                    no_errors = True
                    if is_valid:
                        tag = "tournament/" + home_url.split('/')[-1]
                        url = api_url + tag
                        is_valid = check_valid_url(url)
                        if is_valid:
                            # Add tournament to database
                            data = get_data(url)
                            table_data = process_tournament_data(data)
                            sql = get_tournament_sql(table_data)
                            res = execute_sql(sql)
                            no_errors = res if no_errors == True else False

                            # Collect players in tournament
                            players = data.get('players')
                            if players != None:
                                counter = 1
                                for player in players:
                                    print(f"Adding player {counter} of {len(players)}")
                                    username = player.get('username')
                                    if username != None:
                                        add_player_to_db(username)
                                    else:
                                        print("Players could not be added.")
                                        continue
                                    counter += 1
                            else:
                                print("Players could not be added.")
                                continue
                            try:
                                add_games_to_db(file_location, home_url)
                            except Exception as e:
                                print(f"The following error occured: {e}")
                            mode = setmode()
                            continue
            elif tournament == 'n':
                try:
                    add_games_to_db(file_location, home_url)
                except Exception as e:
                    print(f"The following error occured: {e}")
                os.system ("cls") 
                mode = set_mode()
                continue

        elif mode == 'Tournament Games': #TODO: export the pgn
            if first_time == True:
                os.system ("cls")
                print("Mode: View Tournament Games\n\n")
                print("Please provide the url of the tournament games you would like to view.\nType 'Help' to view the available tournaments.\nEnter a blank line to return to the main menu.\n")
            url = input("Tournament URL: ")
            if url == '':
                os.system ("cls")
                mode = set_mode()
                continue
            elif url.lower() == 'help':
                first_time = False
                urls = get_tournament_urls()
                print("\nAvailable tournaments:\n")
                for link in urls:
                    print(link[0])
                print()
            else:
                os.system("cls")
                print("Mode: View Tournament Games\n\n")
                print(f"Tournament: {url}\n")
                games = get_tournament_games(url)
                counter = 1
                game_strings = []
                for game in games:
                    result = game[3]
                    if result == 'W':
                        result = "1-0"
                    elif result == 'B':
                        result = "0-1"
                    else:
                        result = "1/2-1/2"
                    game_string = f"Game {counter}: {game[1]} vs {game[2]} {result}"
                    game_strings.append(game_string)
                    print(game_string)
                    counter += 1
                print()
                print("Select the number for the game you would like to inspect.")
                print("Or press Enter to continue to the main menu.\n")
                user_input = input("Selection: ")
                if user_input == '':
                    os.system("cls")
                    mode = set_mode()
                    continue
                else:
                    os.system("cls")
                    index = int(user_input) - 1
                    print(game_strings[index] + "\n\n")
                    print("Game PGN: \n")
                    game_id = games[index][0]
                    pgn_string = get_pgn(game_id)
                    print(pgn_string)
                    print("\n\nPress Enter to continue to the main menu.\n")
                    input("")
                    os.system("cls")
                    mode = set_mode()
                first_time = True

        elif mode == 'Leaderboard':
            os.system("cls")
            create_views()
            print("Mode: View Leaderboards\n\n")
            print("Select a Leaderboard you would like to view. \nPress Enter to return to the main menu.\n")
            print("1. Daily Leaderboard \n2. Rapid Leaderboard \n3. Blitz Leaderboard \n4. Bullet Leaderboard \n")
            user_input = input("Selection: ")
            if user_input == '':
                os.system("cls")
                mode = set_mode()
                continue
            elif user_input == '1':
                os.system("cls")
                print("Daily Leaderboard\n\n")
                leaderboard = get_daily_leaderboard()
                players = []
                rating = []
                ranks = []
                rank = 1
                for player in leaderboard:
                    players.append(player[0])
                    rating.append(player[1])
                    ranks.append(rank)
                    rank += 1
                df = ({'Rank': ranks, 'Username': players, 'Rating': rating})
                print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
                print("\n\nPress Enter to return to the main menu.")
                input("")
                os.system("cls")
                mode = set_mode()
                continue
            elif user_input == '2':
                os.system("cls")
                print("Rapid Leaderboard\n\n")
                leaderboard = get_rapid_leaderboard()
                players = []
                rating = []
                ranks = []
                rank = 1
                for player in leaderboard:
                    players.append(player[0])
                    rating.append(player[1])
                    ranks.append(rank)
                    rank += 1
                df = ({'Rank': ranks, 'Username': players, 'Rating': rating})
                print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
                print("\n\nPress Enter to return to the main menu.")
                input("")
                os.system("cls")
                mode = set_mode()
                continue
            elif user_input == '3':
                os.system("cls")
                print("Bullet Leaderboard\n\n")
                leaderboard = get_blitz_leaderboard()
                players = []
                rating = []
                ranks = []
                rank = 1
                for player in leaderboard:
                    players.append(player[0])
                    rating.append(player[1])
                    ranks.append(rank)
                    rank += 1
                df = ({'Rank': ranks, 'Username': players, 'Rating': rating})
                print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
                print("\n\nPress Enter to return to the main menu.")
                input("")
                os.system("cls")
                mode = set_mode()
                continue
            elif user_input == '4':
                os.system("cls")
                print("Blitz Leaderboard\n\n")
                leaderboard = get_bullet_leaderboard()
                players = []
                rating = []
                ranks = []
                rank = 1
                for player in leaderboard:
                    players.append(player[0])
                    rating.append(player[1])
                    ranks.append(rank)
                    rank += 1
                df = ({'Rank': ranks, 'Username': players, 'Rating': rating})
                print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
                print("\n\nPress Enter to return to the main menu.")
                input("")
                os.system("cls")
                mode = set_mode()
                continue
            else:
                continue

        elif mode == 'Update Player':
            os.system("cls")
            print("Mode: Update Player Rank\n\n")
            print("Enter the username of the player you would like to update.\n")
            username = input("Username: ").lower()
            print("\n\nSelect the rank you would like to update.")
            print("1. Daily \n2. Rapid \n3. Blitz \n4. Bullet \n")
            user_input = input("Selection: ")
            rank_type = 'BulletRating'
            if user_input == '1':
                rank_type = 'DailyRating'
            elif user_input =='2':
                rank_type = 'RapidRating'
            elif user_input == '3':
                rank_type = 'BlitzRating'
            print ("\n\nEnter the rank you would like to set this player's rank to.\n")
            rank = int(input("Rank: "))
            update_player(username, rank_type, rank)
            print("\nPlayer updated! \nPress Enter to return to the main menu.")
            input("")
            os.system("cls")
            mode = set_mode()
            continue

        elif mode == 'Export':
            os.system("cls")
            print("Mode: Export Database\n\n")
            print("Exporting data to XML File...")
            export_db_xml()
            print("Database exported to Chess.xml.")
            print("Press Enter to continue to the main menu.")
            input()
            os.system ("cls")
            mode = set_mode()
            continue

        elif mode == 'Exit':
            os.system("cls")
            break

