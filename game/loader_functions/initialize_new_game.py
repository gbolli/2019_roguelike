import tcod as libtcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment
from components.equippable import Equippable
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder
from equipment_slots import EquipmentSlots


def load_customfont():
    # the index of the first custom tile in the file
    a = 256

    # the 'y' is the row index, here we load the sixth row in the font file.   Future: increase the '6' to load any new rows from the file.
    for y in range(5, 6):
        libtcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32


def get_constants():
    window_title = 'Roguelike Never Before!'

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0  # ibtcod.FOV_BASIC
    fov_light_walls = True
    fov_radius = 7

    colors = {
        'dark_wall': libtcod.Color(0, 0, 50),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(50, 50, 100),  # (130, 110, 50),
        'light_ground': libtcod.Color(75, 75, 175)
    }

    # Tiles
    wall_tile = 256
    floor_tile = 257
    player_tile = 258
    orc_tile = 259
    troll_tile = 260
    scroll_tile = 261
    potion_tile = 262
    sword_tile = 263
    shield_tile = 264
    stairsdown_tile = 265
    dagger_tile = 266

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'colors': colors,
        'wall_tile': wall_tile,
        'floor_tile': floor_tile,
        'player_tile': player_tile,
        'orc_tile': orc_tile,
        'troll_tile': troll_tile,
        'scroll_tile': scroll_tile,
        'potion_tile': potion_tile,
        'sword_tile': sword_tile,
        'shield_tile': shield_tile,
        'stairsdown_tile': stairsdown_tile,
        'dagger_tile': dagger_tile
    }

    return constants


def get_game_variables(constants):

    load_customfont()

    fighter_component = Fighter(hp=50, defense=1, power=4)
    inventory_component = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()

    player = Entity(0,
                    0,
                    constants['player_tile'],
                    libtcod.white,
                    'Player',
                    blocks=True,
                    render_order=RenderOrder.ACTOR,
                    fighter=fighter_component,
                    inventory=inventory_component,
                    level=level_component,
                    equipment=equipment_component)
    entities = [player]

    # give the player a starting weapon
    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=1)
    dagger = Entity(0,
                    0,
                    constants['dagger_tile'],
                    libtcod.sky,
                    'Dagger',
                    equippable=equippable_component)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'],
                      constants['room_max_size'], constants['map_width'],
                      constants['map_height'], player, entities, constants)

    message_log = MessageLog(constants['message_x'],
                             constants['message_width'],
                             constants['message_height'])

    game_state = GameStates.PLAYER_TURN

    return player, entities, game_map, message_log, game_state
