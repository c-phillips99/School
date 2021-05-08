import requests
import json
import mysql.connector

modes = {'1': 'Tournament', '2': 'Games', '3': 'Tournament Games', '4': 'Leaderboard', '5': 'Update Player', '6': 'Export', '7': 'Exit'}

def open_database():
    conn = mysql.connector.connect (
        host = "localhost",
        user = "cole",
        password = "password",
        database = "Chess"
    )
    return conn

def set_mode():
    changed = False
    first_time = True
    new_mode = '0'
    while changed == False:
        if first_time:
            print("Please choose one of the following: \n")
        print("\n1. Enter Data From Tournament \n2. Enter Games As PGN \n3. View Tournament Games \n4. View Leaderboard \n5. Update Player Rating \n6. Export Database \n7. Exit Program")
        new_mode = input("\nSelection: ")
        if new_mode in modes.keys():
            changed = True
        else:
            print("Invalid input.")
            first_time = False
    return modes[new_mode]

def get_data(url):
    try:
        response = requests.get(url)
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"The following error occured: {e}")
        return {}

def check_valid_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            print(response.status_code)
            return False
    except Exception as e:
        print(f"The following error occured: {e}")
        return False

def execute_sql(sql):
    try:
        conn = open_database()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        # print(sql)
        # print ("Success! Data was stored.")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        if e.errno == 1062:
            # print ("Data already exists.")
            # print(e)
            return True
        else:   
            print (f"There was an error: {e} \nDatabase was rolled back.")
            print(sql)
            return False