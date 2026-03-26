import pygame
import sys
import random
import string
import csv
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

# Game Data Structures
@dataclass
class Room:
    name: str
    description: str
    exits: Dict[str, 'str']  # direction -> Room
    items: Set[str] = field(default_factory=set)

@dataclass
class Item:
    name: str
    description: str

grid_layout = [
    ["A", "F", "K", "P", "U"],
    ["B", "G", "L", "Q", "V"],
    ["C", "H", "M", "R", "W"],
    ["D", "I", "N", "S", "X"],
    ["E", "J", "O", "T", "Y"]
    ]

def level1_item_placement():
    bones = {"B","E","I","M","O","Q","V","Y"}
    meat  = {"K","L","R"}
    lions = {"C","G","J","T","W"}
    walls = {"H","N","U"}
    return bones, meat, lions, walls

def level1_config():
    bones, meat, lions, walls = level1_item_placement()

    placement = {
        "bone": bones,
        "meat": meat,
        "lion": lions,
        "wall": walls
    }
    return placement


def get_random_empty_cell(grid_width, grid_height, occupied):
    while True:
        x = random.randint(0, grid_width - 1)
        y = random.randint(0, grid_height - 1)

        if (x, y) not in occupied:
            return (x, y)

def level2_item_placement():
    bones = {"B","E","I","M","Q","C","V","Y"}
    meat = {"K","F","Z"}
    lions = set()
    walls = {"H","N","U"}

    occupied = bones | meat | walls

    protected = {"A", "X", "T"}
    all_rooms = set(string.ascii_uppercase[:25]) - protected

    while len(lions) < 3:
        available = list(all_rooms - occupied)
        cell = random.choice(available)
        lions.add(cell)
        occupied.add(cell)
        print(cell)  # Debug: print the randomly placed lion cell

    return bones, meat, lions, walls

def level2_config():
    bones, meat, lions, walls = level2_item_placement()

    placement = {
        "bone": bones,
        "meat": meat,
        "lion": lions,
        "wall": walls
    }
    return placement

def level3_item_placement():
    bones = {"B","E","I","M","Q","C","V","Y"}
    meat = {"K","F","Z"}
    lions = set()
    walls = {"H","N","U"}

    occupied = bones | meat | walls

    protected = {"A", "X", "T"}

    neighbour = list(player.exits.values())  # Get neighboring rooms of the player
    random.shuffle(neighbour)  # Shuffle to randomize which neighbors get lions

    return bones, meat, lions, walls
def move_lions_to_neighbors():
    global rooms, player

    for room in rooms.values():
        room.items.discard("lion")  # Remove all lions first
    neighbors = list(player.exits.values())
    random.shuffle(neighbors)  # Shuffle to randomize lion placement

    valid_neighbors = [rn for rn in neighbors if "wall" not in rooms[rn].items]
    max_lions = max(0, len(valid_neighbors) - 2)  # Ensure at least one neighbor is free of lions
    placed = 0
    for room_name in valid_neighbors:
        if placed >= max_lions:
            break

        if "wall" in room.items:
            continue  # Skip walls
        
        rooms[room_name].items.add("lion")
        placed += 1
        
            

def level3_config():
    bones, meat, lions, walls = level3_item_placement()

    placement = {
        "bone": bones,
        "meat": meat,
        "lion": lions,
        "wall": walls
    }
    return placement

#Build World
def build_world(grid_layout, placement) -> Tuple[Dict[str, Room], Dict[str, Item], int]:
    rows, cols = 5, 5
    score = 0

    rooms: Dict[str, Room] = {}

    items: Dict[str, Item] = {
        "bone": Item(name="Bone", description="A dog bone."),
        "meat": Item(name="Meat", description="A piece of meat."),
        "lion": Item(name="Lion", description="A fierce lion."),
        "wall": Item(name="Wall", description="A solid brick wall.")
    }

    for row in range(rows):
        for col in range(cols):
            letter = grid_layout[row][col]
            exits = {}

            if row > 0:  # north
                exits["north"] = grid_layout[row-1][col]
            if row < rows - 1:  # south
                exits["south"] = grid_layout[row+1][col]
            if col > 0:  # west
                exits["west"] = grid_layout[row][col-1]
            if col < cols - 1:  # east
                exits["east"] = grid_layout[row][col+1]

            room_items: Set[str] = set()

            for item_name, locations in placement.items():
                if letter in locations:
                    room_items.add(item_name)

            rooms[letter] = Room(
                name=f"Room {letter}",
                description=f"You are in room {letter}.",
                exits=exits,                    # actually use the exits
                items=room_items
            )

    return rooms, items, score

pygame.init()
#Creating log file
player_id = str(uuid.uuid4())
csv_file = open('game_log.csv', 'a', newline='')
csv_writer = csv.writer(csv_file)
if csv_file.tell() == 0:  # Write header if file is new
    csv_writer.writerow(['timestamp', 'player_id', 'level', 'keyPressed', 'room', 'score', 'gameEvent'])

screen = pygame.display.set_mode((625, 650))
pygame.display.set_caption("Dog Hunting Game")
clock = pygame.time.Clock()
placement = level1_config()
rooms, items, score = build_world(grid_layout, placement)
player= rooms["A"]

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
inventory: Set[str] = set()
messages = []

user_text = ""

current_level = 1

# Logging function
def log_event(level, room, key, event, score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    csv_writer.writerow([timestamp, player_id, level, key, room, score, event])
    csv_file.flush()  # Ensure data is written to file immediately

# Draw the 5×5 grid
def draw_grid(surface: pygame.Surface,
              rooms: Dict[str, Room],
              current: Room) -> None:
    rows, cols = 5, 5
    tile_size = 70
    margin = 20

    for row in range(rows):
        for col in range(cols):
            letter = grid_layout[row][col]
            x = margin + col * tile_size
            y = margin + row * tile_size
            rect = pygame.Rect(x, y, tile_size, tile_size)

            colour = (0, 255, 0) if rooms[letter] is current else (255, 255, 255)
            pygame.draw.rect(surface, colour, rect, 2)

            txt = font.render(letter, True, (255, 255, 255))
            surface.blit(txt,
                         (x + tile_size/2 - txt.get_width()/2,
                          y + tile_size/2 - txt.get_height()/2))

#Movement and interactions
def move_player(direction):
    global score, player, rooms, items, current_level

    # Map shortcuts to full exit names
    shortcuts = {
        "n": "north", "up": "north",
        "s": "south", "down": "south",
        "e": "east", "right": "east",
        "w": "west", "left": "west"
    }

    direction = direction.lower().strip()
    # Convert shortcut to full direction if needed
    if direction in shortcuts:
        direction = shortcuts[direction]

    level_name = f"Level {current_level}"
    current_room = player.name[-1]

    if direction not in player.exits:
        messages.append("You can't go that way!")
        return

    next_room_name = player.exits[direction]
    next_room = rooms[next_room_name]

    if "wall" in next_room.items:
        messages.append("A wall blocks your way!")
        log_event(level_name, current_room, direction, "hit_wall", score)
        return

    player = next_room
    current_room = player.name[-1]

    if "bone" in player.items:
        score += 2
        messages.append("Found a bone! (+2)")
        player.items.remove("bone")
        log_event(level_name, current_room, direction, "Bone Collected", score)

    elif "meat" in player.items:
        score += 5
        messages.append("Found meat! (+5)")
        player.items.remove("meat")
        log_event(level_name, current_room, direction, "Meat Collected", score)


    elif "lion" in player.items:
        messages.append("A lion attacks! GAME OVER")
        log_event(level_name, current_room, direction, "Attacked by Lion", score)
        score = 0
        return "lose"
    else:
        messages.append("Empty Room")
        log_event(level_name, current_room, direction, "Moved to Empty Room", score)

    if player == rooms["Y"]:
        messages.append("You found the exit! Congratulations!")
        return "win"
    
    # After handling bone/meat/lion
    if bones_remaining(rooms) == 0:
        messages.append("All bones collected! Level Complete! Press N for next level.")
        return "level_complete"
    
    if current_level == 3:
        move_lions_to_neighbors()  # Move lions after player moves in level 3

# Draw user input box
def draw_input(surface, user_text):
    input_box = pygame.Rect(20, 540, 580, 40)  # below messages
    pygame.draw.rect(surface, (255,255,255), input_box, 2)
    txt = font.render("> " + user_text, True, (0,255,0))
    surface.blit(txt, (input_box.x + 10, input_box.y + 10))
# Draw the last 3 messages on screen
def draw_messages(surface, messages):
    """Draw the last 5 messages on screen."""
    y_start = 380  # start below the grid
    for msg in messages[-3:]:
        txt = font.render(msg, True, (255, 255, 0))
        surface.blit(txt, (30, y_start))
        y_start += 22

# Draw score and bones remaining
def draw_score(surface, score, rooms):
    txt = font.render(f"Score: {score}", True, (255, 255, 0))  # yellow
    surface.blit(txt, (500, 35))  # top right

    remaining = bones_remaining(rooms)
    txtbones = small_font.render(f"Bones Remaining: {remaining}", True, (255, 255, 255))
    surface.blit(txtbones, (450, 50))  # top left

# Draw current level
def draw_level(surface, level):
    txt = font.render(f"Level {level}", True, (255, 255, 0))
    surface.blit(txt, (500, 10))  # top left

# Command handling
def handle_command(command):
    command = command.lower().strip()
    move_player(command)

# Utility function to count remaining bones
def bones_remaining(rooms: Dict[str, Room]) -> int:
    """Count how many bones are still in the rooms."""
    return sum(1 for room in rooms.values() if "bone" in room.items)


# main loop

game_state = "playing"  # can be "playing", "win", "lose"

#Level 1 - Static placement of lions, bones, and meat
def level1():
    global player, rooms, items, score, messages, user_text, game_state

    placement = level1_config()
    rooms, items, score = build_world(grid_layout, placement)
    player = rooms["A"]
    messages = []
    exits = ", ".join(player.exits.keys())
    messages.append(f"You can go: {exits}")
    user_text = ""
    game_state = "playing"

    global current_level
    current_level = 1
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # Restart game
                if game_state == "lose" and event.key == pygame.K_r:
                    level1()
                    return
                
                # Next level
                if game_state == "level_complete" or game_state == "win" and event.key == pygame.K_q:
                    level2()
                    return

                if game_state == "playing":
                    if event.key == pygame.K_RETURN:
                        result = move_player(user_text)
                        exits = ", ".join(player.exits.keys())
                        messages.append(f"You can go: {exits}")
                        user_text = ""

                        if result == "lose":
                            messages.append("Game Over! Press R to restart.")
                            game_state = "lose"

                        elif result == "win":
                            messages.append("You Win! Press Q to go to the next level.")
                            game_state = "win"

                        elif result == "level_complete":
                            game_state = "level_complete"

                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]

                    else:
                        user_text += event.unicode

        screen.fill((0,0,0))
        draw_grid(screen, rooms, player)
        draw_messages(screen, messages)
        draw_input(screen, user_text)
        draw_score(screen, score, rooms)
        draw_level(screen, 1)
        pygame.display.flip()
        clock.tick(30)

# Start Screen
def start_screen():
    screen.fill((0,0,0))
    title = font.render("Dog Hunting Game", True, (255, 255, 0))
    instructions = font.render("Collect bones and meat, avoid lions!", True, (255, 255, 255))
    start_msg = small_font.render("Press Enter to Start", True, (255, 255, 255))
    screen.blit(title, (150, 200))
    screen.blit(instructions, (50, 300))
    screen.blit(start_msg, (200, 400))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
                level1()

#Level 2 - Lions are randomly placed in different rooms at the start of the level
def level2():
    global player, rooms, items, score, messages, user_text, game_state

    placement = level2_config()
    rooms, items, score = build_world(grid_layout, placement)
    player = rooms["A"]
    messages = []
    exits = ", ".join(player.exits.keys())
    messages.append("Welcome to Level 2! Watch out, the lions have moved!")
    messages.append(f"You can go: {exits}")
    user_text = ""
    game_state = "playing"

    global current_level
    current_level = 2
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # Restart game
                if game_state in ("lose", "win") and event.key == pygame.K_r:
                    level2()
                    return
                
                #Next Level
                if game_state == "level_complete" or game_state == "win" and event.key == pygame.K_q:
                    level3()
                    return

                if game_state == "playing":
                    if event.key == pygame.K_RETURN:
                        result = move_player(user_text)
                        exits = ", ".join(player.exits.keys())
                        messages.append(f"You can go: {exits}")
                        user_text = ""

                        if result == "lose":
                            messages.append("Game Over! Press R to restart.")
                            game_state = "lose"

                        elif result == "win":
                            messages.append("You Win! Press Q to go to the next level.")
                            game_state = "win"

                        elif result == "level_complete":
                            game_state = "level_complete"

                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]

                    else:
                        user_text += event.unicode

        screen.fill((0,0,0))
        draw_grid(screen, rooms, player)
        draw_messages(screen, messages)
        draw_input(screen, user_text)
        draw_score(screen, score, rooms)
        draw_level(screen, 2)
        pygame.display.flip()
        clock.tick(30)

#Level 3 - Lions move to neighboring rooms after each player move
def level3():
    global player, rooms, items, score, messages, user_text, game_state, move_lions_to_neighbors

    placement = level3_config()
    rooms, items, score = build_world(grid_layout, placement)
    player = rooms["A"]
    messages = []
    exits = ", ".join(player.exits.keys())
    messages.append("Watch out, the lions have moved to neighboring rooms!")
    messages.append(f"You can go: {exits}")
    user_text = ""
    game_state = "playing"

    global current_level
    current_level = 3
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                # Restart game
                if game_state in ("lose", "win") and event.key == pygame.K_r:
                    level3()
                    return

                if game_state == "playing":
                    if event.key == pygame.K_RETURN:
                        result = move_player(user_text)
                        move_lions_to_neighbors()  # Move lions after player moves
                        exits = ", ".join(player.exits.keys())
                        messages.append(f"You can go: {exits}")
                        user_text = ""

                        if result == "lose":
                            messages.append("Game Over! Press R to restart.")
                            game_state = "lose"

                        elif result == "win":
                            messages.append("You Win! Press Q to go to the next level.")
                            game_state = "win"

                        elif result == "level_complete":
                            game_state = "level_complete"

                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]

                    else:
                        user_text += event.unicode

        screen.fill((0,0,0))
        draw_grid(screen, rooms, player)
        draw_messages(screen, messages)
        draw_input(screen, user_text)
        draw_score(screen, score, rooms)
        draw_level(screen, 3)
        pygame.display.flip()
        clock.tick(30)

start_screen() # Start the game with the start screen
csv_file.close() # Closes CSV File
pygame.quit()
sys.exit()
