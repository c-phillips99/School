from chess.pgn import *
from utils.sql import get_games_sql, get_turn_sql, get_tournament_games_sql, get_game_id, check_for_game
from utils.common import execute_sql
from utils.process_data import process_game_data

class StringExporterMod(StringExporterMixin, BaseVisitor[str]):
    def result(self) -> str:
        if self.current_line:
            return " ".join(itertools.chain(self.lines, [self.current_line.rstrip()])).rstrip()
        else:
            return " ".join(self.lines).rstrip()
    def __str__(self) -> str:
        return self.result()

def group_moves(pgn_list):
    turns = []
    list_len = len(pgn_list)
    if list_len % 3 == 0: # If black made the last move and the list doesn't have an extra move for white
        for index in range(0, list_len, 3): # Iterate throught the turns (each turn has 3 elements)
            turn = pgn_list[index].replace('.', '')
            white_move = pgn_list[index+1]
            black_move = pgn_list[index+2]
            turns.append((turn, white_move, black_move))
    else:
        last_turn = list_len // 3 * 3 # Last turn that there are two moves (one for white and one for black)
        for index in range(0, list_len, 3): # Iterate throught the turns (each turn has 3 elements)
            if index != last_turn:
                turn = pgn_list[index].replace('.', '')
                white_move = pgn_list[index+1]
                black_move = pgn_list[index+2]
                turns.append((turn, white_move, black_move))
            else:
                last_turn = pgn_list[index].replace('.', '')
                last_white_move = pgn_list[index+1]
                turns.append((last_turn, last_white_move, ''))
    return turns

def insert_turns(game_id, turns):
    for turn in turns:
        sql = get_turn_sql(game_id, turn)
        res = execute_sql(sql)

def add_games_to_db(file_location_raw, tournament_id):

    # Read pgn and get headers
    file_location = file_location_raw.replace('\\', '/')
    # file_location = "C:/Users/celld/School/Databases/Project/input_data/pgns/U1000_May3_2021-05-03-13-16.pgn"
    pgn = open(file_location)
    counter = 1
    while True:
        game = chess.pgn.read_game(pgn)
        if game == None:
            break
        else:
            # Insert into Games table
            table_data = process_game_data(game)
            game_exists = check_for_game(table_data)
            if not game_exists:
                sql = get_games_sql(table_data)
                res = execute_sql(sql)

                # Insert into Tournament Games table
                game_id = get_game_id()           
                tg_sql = get_tournament_games_sql(game_id, tournament_id)
                res = execute_sql(tg_sql)

                # Get data for Moves table and insert
                exporter = StringExporterMod(headers=False, variations=False, comments=False)
                pgn_string = game.accept(exporter)
                pgn_list = pgn_string.split()[:-1]
                turns = group_moves(pgn_list)
                insert_turns(game_id, turns)
                print(f"Games added: {counter}")
                counter += 1
            else:
                continue
