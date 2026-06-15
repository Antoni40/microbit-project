records = [9999]

radio.set_group(1)
is_game_active = False
start_time = 0
role = ""
host_time = 0
player_time = 0

def start_round():
    global is_game_active, start_time, role

    if role == "PLAYER":
        return

    basic.clear_screen()

    for i in range(3, 0, -1):
        radio.send_number(i)
        basic.show_number(i)
        basic.pause(300)

    basic.clear_screen()

    random_time_show = randint(500, 3000)
    basic.pause(random_time_show)

    radio.send_string("START")
    basic.show_leds("""
    # # # # #
    # # # # #
    # # # # #
    # # # # #
    # # # # #
    """)
    
    start_time = input.running_time()
    is_game_active = True

def record_reaction_time():
    global is_game_active, start_time, host_time

    if not is_game_active:
        return
        
    end_time = input.running_time()
    reaction = (end_time - start_time)

    basic.clear_screen()

    is_game_active = False
    if role == "HOST":
        host_time = reaction
    else:
        radio.send_string("T: " + str(reaction))
    
def show_best_times():
    basic.clear_screen()

    if len(records) == 0 or records[0] == 9999:
        basic.show_string("NO RECORDS")
        return

    records_string = ""

    for i in range(len(records)):
        records_string += str(i + 1) + ". " + str(records[i]) + "ms "
    
    basic.show_string(records_string)
    basic.pause(1000)
    basic.show_string("A START")

def add_best_time(result):
    records.append(result)
    
    if records[0] == 9999:
        records.reverse()
        records.pop()

    sort_best_times()

def sort_best_times():
    for i in range(len(records)):
        for j in range(len(records) - 1 - i):
            if records[j] > records[j+1]:
                temp = records[j]
                records[j] = records[j + 1]
                records[j + 1] = temp
    
    while len(records) > 3:
        records.pop()

def handle_radio_message(receivedString):
    global role, is_game_active, start_time, host_time, player_time
    basic.clear_screen()

    if receivedString[0] == "R":
        if receivedString == "R: PLAYER":
            role = "PLAYER"
        else:
            role = "HOST"
        return

    if receivedString == "START":
        basic.show_leds("""
            # # # # #
            # # # # #
            # # # # #
            # # # # #
            # # # # #
            """)

        start_time = input.running_time()
        is_game_active = True
        return
    
    if receivedString[0] == "T" and role == "HOST":
        player_time = int(receivedString[3:])
        basic.show_string("H: " + str(host_time) + "ms ")
        basic.show_string("P:" + str(player_time) + "ms ")
        add_best_time(host_time)
        add_best_time(player_time)
        
        if host_time != 0:
            if host_time < player_time:
                basic.show_string("WIN")
            elif host_time > player_time:
                basic.show_string("LOSE")
            else:
                basic.show_string("DRAW")

        basic.show_string("A START")
        return
radio.on_received_string(handle_radio_message)

def handle_countdown_number(receivedNumber):
    basic.show_number(receivedNumber)
    basic.pause(300)
    basic.clear_screen()
            
radio.on_received_number(handle_countdown_number)

def handle_button_a():
    global role
    if role == "":
        role = "HOST"
        radio.send_string("R: PLAYER")
        basic.show_string("A START")
    elif role == "HOST":
        start_round()

input.on_button_pressed(Button.A, handle_button_a)

def handle_button_b():
    global role
    if role == "":
        role = "PLAYER"
        radio.send_string("R: HOST")
        basic.show_string("A START")
    elif is_game_active:
            record_reaction_time()

input.on_button_pressed(Button.B, handle_button_b)


def handle_buttons_ab():
    global is_game_active, start_time
    if role == "HOST":
        basic.clear_screen()
        if is_game_active == True:
            is_game_active = False
            start_time = 0
        show_best_times()
        
input.on_button_pressed(Button.AB, handle_buttons_ab)

radio.send_string("CONFIG")

if role == "":
    basic.show_string("A - HOST B - PLAYER")