import pygame
import sys
import string
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

#Build World
def build_world() -> Tuple[Dict[str, Room], Dict[str, Item]]:
    letters = list(string.ascii_uppercase[:25])   # 5×5 grid
    rows, cols = 5, 5

    bones = {"B","E","I","M","O","Q","V","Y"}
    meat  = {"K","L","R"}
    lions = {"C","G","J","T","W"}
    walls = {"H","N","U","X"}

    rooms: Dict[str, Room] = {}
    items: Dict[str, Item] = {
        "bone": Item(name="Bone", description="A dog bone."),
        "meat": Item(name="Meat", description="A piece of meat."),
        "lion": Item(name="Lion", description="A fierce lion."),
        "wall": Item(name="Wall", description="A solid brick wall.")
    }

    for index, letter in enumerate(letters):
        row = index // cols
        col = index % cols
        exits: Dict[str, str] = {}
        if row > 0:
            exits["north"] = letters[index - cols]
        if row < rows - 1:
            exits["south"] = letters[index + cols]
        if col > 0:
            exits["west"] = letters[index - 1]
        if col < cols - 1:
            exits["east"] = letters[index + 1]

        room_items: Set[str] = set()
        if letter in bones:
            room_items.add("bone")
        elif letter in meat:
            room_items.add("meat")
        elif letter in lions:
            room_items.add("lion")
        elif letter in walls:
            room_items.add("wall")

        rooms[letter] = Room(
            name=f"Room {letter}",
            description=f"You are in room {letter}.",
            exits=exits,                    # actually use the exits
            items=room_items
        )

    return rooms, items

pygame.init()
screen = pygame.display.set_mode((625, 650))
pygame.display.set_caption("Dog Hunting Game")
clock = pygame.time.Clock()
rooms, items = build_world()
current_room = rooms["A"]
font = pygame.font.Font(None, 36)
inventory: Set[str] = set()

# Draw the 5×5 grid
def draw_grid(surface: pygame.Surface,
              rooms: Dict[str, Room],
              current: Room) -> None:
    rows, cols = 5, 5
    tile_size = 100          
    margin = 50               

    # sort the keys so they appear in A‑Z order
    for idx, letter in enumerate(sorted(rooms.keys())):
        row = idx // cols
        col = idx % cols
        x = margin + col * tile_size
        y = margin + row * tile_size
        rect = pygame.Rect(x, y, tile_size, tile_size)

        colour = (0, 255, 0) if rooms[letter] is current else (255, 255, 255)
        pygame.draw.rect(surface, colour, rect, 2)

        txt = font.render(letter, True, (255, 255, 255))
        surface.blit(txt,
                     (x + tile_size/2 - txt.get_width()/2,
                      y + tile_size/2 - txt.get_height()/2))

# main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # … handle movement, picking up items, etc. …

    screen.fill((0, 0, 0))        # clear
    draw_grid(screen, rooms, current_room)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()