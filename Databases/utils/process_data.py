from utils.common import get_data, check_valid_url
from chess.pgn import *
from utils.sql import get_ids

api_url  = 'https://api.chess.com/pub/'

def process_tournament_data(data):
    name = data.get('name') or "NULL"
    url = data.get('url') or "NULL"
    settings = data.get('settings') or "NULL"
    time_control = settings.get('time_control') or "NULL"
    time_class = settings.get('time_class') or "NULL"
    t_type = settings.get('type') or "NULL"
    is_rated = settings.get('is_rated') or "NULL"
    is_official = settings.get('is_official') or "False"

    return url, name, time_control, time_class, t_type, is_rated, is_official

def process_player_data(data):
    player_id = data.get('player_id') or "NULL"
    username = data.get('username') or "NULL"
    name = data.get('name') or "NULL"
    title = data.get('title') or "NULL"
    country_url = data.get('country') or "NULL"
    country = "NULL"
    if country_url != "NULL":
        country_data = get_data(country_url)
        country = country_data.get('name') or "NULL"
    fide = data.get('fide') or "NULL"

    url = api_url + f'player/{username}/stats'
    stats_data = get_data(url)
    cur_daily = stats_data.get('chess_daily') or "NULL"
    if cur_daily != "NULL":
        cur_daily = cur_daily.get('last') or "NULL"
        if cur_daily != "NULL":
            cur_daily = cur_daily.get('rating') or "NULL"
    cur_rapid = stats_data.get('chess_rapid') or "NULL"
    if cur_rapid != "NULL":
        cur_rapid = cur_rapid.get('last') or "NULL"
        if cur_rapid != "NULL":
            cur_rapid = cur_rapid.get('rating') or "NULL"
    cur_bullet = stats_data.get('chess_bullet') or "NULL"
    if cur_bullet != "NULL":
        cur_bullet = cur_bullet.get('last') or "NULL"
        if cur_bullet != "NULL":
            cur_bullet = cur_bullet.get('rating') or "NULL"
    cur_blitz = stats_data.get('chess_blitz') or "NULL"
    if cur_blitz != "NULL":
        cur_blitz = cur_blitz.get('last') or "NULL"
        if cur_blitz != "NULL":
            cur_blitz = cur_blitz.get('rating') or "NULL"

    return player_id, username, name, title, country, fide, cur_daily, cur_rapid, cur_blitz, cur_bullet

def process_club_data(data, club_url):
    # Getting club info
    club_id = data.get('club_id') or "NULL"
    name = data.get('name') or "NULL"
    country_url = data.get('country') or "NULL"
    country = ""
    if country_url != "NULL":
        country_data = get_data(country_url)
        country = country_data.get('name') or "NULL"
    # club_url = data.get('@id') or "NULL"

    return club_id, name, country, club_url

def process_game_data(game):
    white = game.headers.get('White').lower()
    black = game.headers.get('Black').lower()
    time_control = game.headers.get('TimeControl').lower()
    date = game.headers.get('Date').lower()
    time = game.headers.get('EndTime').lower()
    result = game.headers.get('Result').lower()
    
    # Get games table data

    ## Player ids
    white_id, black_id = get_ids(white, black)
    ## Time class
    time_without_increment = time_control.split('+')[0]
    time_class = 'daily'
    if '/' not in time_without_increment:
        if int(time_without_increment) < 180: # less than 3 minutes
            time_class = 'bullet'
        elif int(time_without_increment) < 600: # less than 5 minutes
            time_class = 'blitz'
        elif int(time_without_increment) > 60*60: # more than 60 minutes
            time_class = 'standard'
        else:
            time_class = 'rapid'
    ## Result
    if result == '0-1':
        result = 'B'
    elif result == '1-0':
        result = 'W'
    else:
        result = 'D'

    ## Date-Time
    date = date.replace('.', '-')
    time = time.split(' ')[0]
    date_time = date + ' ' + time

    return ('NULL', white_id, black_id, date_time, time_class, time_control, result)