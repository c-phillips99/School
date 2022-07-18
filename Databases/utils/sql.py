import mysql.connector
from utils.common import open_database

def setup_db():
    conn = mysql.connector.connect (
        host = "localhost",
        user = "cole",
        password = "password",
    )
    cur = conn.cursor()
    cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'Chess';")
    result = cur.fetchone()

    if result == None:
        print("Creating database")
        with open('../setup_db.sql') as sql_file:
            full_sql = sql_file.read()
            sql_commands = full_sql.split(';') 
            for sql_command in sql_commands:
                cur.execute(sql_command)
            cur.close()
            conn.close()


def get_players_clubs_sql(player_id, club_id):
    sql = """INSERT INTO PlayersClubs VALUES ({player_id}, {club_id})""".format (
        player_id = f"'{player_id}'" if player_id != "NULL" else player_id,
        club_id = f"'{club_id}'" if club_id != "NULL" else club_id,
    )
    return sql

def get_tournament_sql(table_data):
    url, name, time_control, time_class, t_type, is_rated, is_official = table_data
    new_name = name.replace("'", "''")
    sql = """INSERT INTO Tournaments VALUES ({url}, {name}, {time_control}, {time_class}, {t_type}, {is_rated}, {is_official})""".format (
                        url = f"'{url}'" if url != "NULL" else url,
                        name = f"'{new_name}'" if new_name != "NULL" else new_name,
                        time_control = f"'{time_control}'" if time_control != "NULL" else time_control,
                        time_class = f"'{time_class}'" if time_class != "NULL" else time_class,
                        t_type = f"'{t_type}'" if t_type != "NULL" else t_type,
                        is_rated = is_rated,
                        is_official = is_official)
    return sql

def get_player_sql(table_data):
    player_id, username, name, title, country, fide, cur_daily, cur_rapid, cur_blitz, cur_bullet = table_data
    new_username = username.replace("'", "''")
    new_name = name.replace("'", "''")
    sql = """INSERT INTO Players VALUES ({player_id}, {username}, {name}, {title}, {country}, {fide}, {daily}, {rapid}, {blitz}, {bullet})""".format (
                        player_id = f"'{player_id}'" if player_id != "NULL" else player_id,
                        username = f"'{new_username}'" if new_username != "NULL" else new_username,
                        name = f"'{new_name}'" if new_name != "NULL" else new_name,
                        title = f"'{title}'" if title != "NULL" else title,
                        country = f"'{country}'" if country != "NULL" else country,
                        fide = int(fide) if fide != "NULL" else fide,
                        daily = int(cur_daily) if cur_daily != "NULL" else cur_daily,
                        rapid = int(cur_rapid) if cur_rapid != "NULL" else cur_rapid,
                        blitz = int(cur_blitz) if cur_blitz != "NULL" else cur_blitz,
                        bullet = int(cur_bullet) if cur_bullet != "NULL" else cur_bullet)
    return sql

def get_club_sql (table_data):
    club_id, name, country, club_url = table_data
    new_name = name.replace("'", "''")
    sql = """INSERT INTO Clubs VALUES ({club_id}, {name}, {country}, {club_url})""".format (
                        club_id = f"'{club_id}'" if club_id != "NULL" else club_id,
                        name = f"'{new_name}'" if new_name != "NULL" else new_name,
                        country = f"'{country}'" if country != "NULL" else country,
                        club_url = f"'{club_url}'" if club_url != "NULL" else club_url)
    return sql

def get_games_sql (table_data):
    game_id, white_id, black_id, date_time, time_class, time_control, result = table_data
    sql = """INSERT INTO Games VALUES ({game_id}, {white_id}, {black_id}, {date_time}, {time_class}, {time_control}, {result})""".format (
                        game_id = game_id,
                        white_id = f"'{white_id}'" if white_id != "NULL" else white_id,
                        black_id = f"'{black_id}'" if black_id != "NULL" else black_id,
                        date_time = f"'{date_time}'" if date_time != "NULL" else date_time,
                        time_class = f"'{time_class}'" if time_class != "NULL" else time_class,
                        time_control = f"'{time_control}'" if time_control != "NULL" else time_control,
                        result = f"'{result}'" if result != "NULL" else result)
    return sql

def get_turn_sql (game_id, turn):
    turn_num, white_move, black_move = turn
    black_move = "NULL" if black_move == '' else black_move
    sql = """INSERT INTO GameTurns VALUES ({game_id}, {turn_num}, {white_move}, {black_move})""".format (
                        game_id = game_id,
                        turn_num = f"'{turn_num}'" if turn_num != "NULL" else turn_num,
                        white_move = f"'{white_move}'" if white_move != "NULL" else white_move,
                        black_move = f"'{black_move}'" if black_move != "NULL" else black_move)
    return sql

def get_tournament_games_sql (game_id, tournament_id):
    sql = """INSERT INTO TournamentGames VALUES ({game_id}, {tournament_id})""".format (
        game_id = f"'{game_id}'" if game_id != "NULL" else game_id,
        tournament_id = f"'{tournament_id}'" if tournament_id != "NULL" else tournament_id
    )
    return sql

def tournament_exists(url):
    conn = open_database()
    cur = conn.cursor()

    result = False
    cur.execute("SELECT 1 FROM Tournaments WHERE EXISTS (SELECT URLId FROM Tournaments WHERE URLId = {id})".format(id=f"'{url}'"))
    cursor_response = cur.fetchone()
    if cursor_response != None:
        result = True
    conn.close()

    return result

def get_ids(white, black):
    # Get games table data
    conn = open_database()
    cur = conn.cursor()

    # Player ids
    cur.execute(f"SELECT PlayerId FROM Players WHERE Username = '{white}'")
    white_id = cur.fetchone()[0]
    cur.execute(f"SELECT PlayerId FROM Players WHERE Username = '{black}'")
    black_id = cur.fetchone()[0]

    conn.close()

    return white_id, black_id

def get_game_id():
    conn = open_database()
    cur = conn.cursor()
    cur.execute(f"SELECT MAX(GameId) FROM Games")
    game_id = cur.fetchone()[0]
    conn.close()
    return game_id

def get_tournament_games(url):
    conn = open_database()
    cur = conn.cursor()
    cur.execute(f"""SELECT Games.GameId, white.Username AS White, black.Username AS Black, Result
                FROM Games, Players white, Players black, TournamentGames 
                WHERE WhitePlayerId = white.PlayerId AND BlackPlayerId = black.PlayerId 
                AND TournamentGames.GameId = Games.GameId 
                AND TournamentGames.URLId = '{url}' 
                ORDER BY Games.GameId;""")
    games = cur.fetchall()
    conn.close()
    return games

def get_tournament_urls():
    conn = open_database()
    cur = conn.cursor()
    cur.execute(f"""SELECT URLId FROM Tournaments""")
    tournaments = cur.fetchall()
    conn.close()
    return tournaments

def get_pgn(game_id):
    conn = open_database()
    cur = conn.cursor()
    cur.execute(f"""SELECT Turn, WhiteMove, BlackMove FROM GameTurns WHERE GameId = '{game_id}' ORDER BY Turn""")
    turns = cur.fetchall()
    cur.execute(f"""SELECT Result FROM Games WHERE GameId = '{game_id}'""")
    result = cur.fetchone()[0]
    conn.close()
    if result == 'W':
        result = "1-0"
    elif result == 'B':
        result = "0-1"
    else:
        result = "1/2-1/2"

    parsed_turns = []
    for turn in turns:
        if turn[2] != None:
            pgn_turn = f"{turn[0]}. {turn[1]} {turn[2]}"
            parsed_turns.append(pgn_turn)
        else:
            pgn_turn = f"{turn[0]}. {turn[1]}"
            parsed_turns.append(pgn_turn)

    pgn_string = ' '.join(parsed_turns)
    pgn_string += f" {result}"

    return pgn_string

def create_views():
    conn = open_database()
    cur = conn.cursor()
    # Daily
    cur.execute("""SELECT 'view exists' FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = N'DailyLeaderboard';""")
    exists = cur.fetchone()
    if exists == None:
        cur.execute("""CREATE VIEW DailyLeaderboard AS (SELECT Username, DailyRating FROM Players WHERE DailyRating != 'NULL' ORDER BY DailyRating DESC LIMIT 10);""")
    # Rapid
    cur.execute("""SELECT 'view exists' FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = N'RapidLeaderboard';""")
    exists = cur.fetchone()
    if exists == None:
        cur.execute("""CREATE VIEW RapidLeaderboard AS (SELECT Username, RapidRating FROM Players WHERE RapidRating != 'NULL' ORDER BY RapidRating DESC LIMIT 10);""")
    # Blitz
    cur.execute("""SELECT 'view exists' FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = N'BlitzLeaderboard';""")
    exists = cur.fetchone()
    if exists == None:
        cur.execute("""CREATE VIEW BlitzLeaderboard AS (SELECT Username, BlitzRating FROM Players WHERE BlitzRating != 'NULL' ORDER BY BlitzRating DESC LIMIT 10);""")
    # Bullet
    cur.execute("""SELECT 'view exists' FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_NAME = N'BulletLeaderboard';""")
    exists = cur.fetchone()
    if exists == None:
        cur.execute("""CREATE VIEW BulletLeaderboard AS (SELECT Username, BulletRating FROM Players WHERE BulletRating != 'NULL' ORDER BY BulletRating DESC LIMIT 10);""")
    cur.close()
    conn.close()

def get_daily_leaderboard():
    conn = open_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM DailyLeaderboard")
    leaderboard = cur.fetchall()
    conn.close()
    return leaderboard

def get_rapid_leaderboard():
    conn = open_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM RapidLeaderboard")
    leaderboard = cur.fetchall()
    conn.close()
    return leaderboard

def get_blitz_leaderboard():
    conn = open_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM BlitzLeaderboard")
    leaderboard = cur.fetchall()
    conn.close()
    return leaderboard

def get_bullet_leaderboard():
    conn = open_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM BulletLeaderboard")
    leaderboard = cur.fetchall()
    conn.close()
    return leaderboard

def check_for_game(table_data):
    _, white_id, black_id, date_time, time_class, time_control, result = table_data
    conn = open_database()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT 'game exists' FROM Games WHERE WhitePlayerId = '{white_id}'
        AND BlackPlayerId = '{black_id}'
        AND Date = '{date_time}';
        """
    )
    result = cur.fetchone()
    conn.close()
    if result == None:
        return False
    else:
        return True

def update_player(username, rank_type, rank):
    try:
        conn = open_database()
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE Players
            SET {rank_type} = '{rank}'
            WHERE Username = '{username}';
            """
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"There as an error: {e}")
        conn.rollback()
        cur.close()
        conn.close()
