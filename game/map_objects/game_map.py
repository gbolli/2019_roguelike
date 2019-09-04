import tcod as libtcod
from random import randint

from components.ai import BasicMonster
from equipment_slots import EquipmentSlots  # corrected from components.equipement
from components.equippable import Equippable
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from entity import Entity
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from render_functions import RenderOrder
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from game_messages import Message
from random_utils import random_choice_from_dict, from_dungeon_level


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)]
                 for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width,
                 map_height, player, entities, constants):

        # Create rooms and passages
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)
            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)
            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # "paint" it to the map's tiles
                self.create_room(new_room)
                # center coordinates of new room
                (new_x, new_y) = new_room.center()

                # find center of final room to place stairs
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # first room where player starts
                    player.x = new_x
                    player.y = new_y
                else:
                    # connect to previous room with a tunnel (based on center)

                    # pull center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin
                    if randint(0, 1) == 1:
                        # horizontal then vertical
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # vertical then horizontal
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                # add entities to the map
                self.place_entities(new_room, entities, constants)

                # append new room to list
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x,
                             center_of_last_room_y,
                             constants['stairsdown_tile'],
                             libtcod.white,
                             'Stairs',
                             render_order=RenderOrder.STAIRS,
                             stairs=stairs_component)
        entities.append(down_stairs)

    def create_room(self, room):
        # got through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities, constants):

        # get a random number of monsters
        number_of_monsters = from_dungeon_level([[2, 1], [3, 4], [4, 6]],
                                                self.dungeon_level)
        number_of_items = from_dungeon_level(
            [[randint(0, 1), 1], [randint(1, 2), 2]], self.dungeon_level)

        monster_chances = {
            'orc':
            80,
            'troll':
            from_dungeon_level([[15, 2], [30, 3], [60, 4]], self.dungeon_level)
        }
        item_chances = {
            'healing_potion':
            25,
            'sword':
            from_dungeon_level([[1, 1], [3, 2], [10, 3]], self.dungeon_level),
            'shield':
            from_dungeon_level([[1, 1], [3, 2], [10, 3]], self.dungeon_level),
            'lightning_scroll':
            from_dungeon_level([[5, 3], [10, 4]], self.dungeon_level),
            'fireball_scroll':
            from_dungeon_level([[10, 4]], self.dungeon_level),
            'confusion_scroll':
            from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        for i in range(number_of_monsters):
            # choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([
                    entity
                    for entity in entities if entity.x == x and entity.y == y
            ]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'orc':
                    fighter_component = Fighter(hp=randint(8, 10),
                                                defense=0,
                                                power=3,
                                                xp=35)
                    ai_component = BasicMonster()

                    monster = Entity(x,
                                     y,
                                     constants['orc_tile'],
                                     libtcod.lightest_green,
                                     'Orc',
                                     blocks=True,
                                     render_order=RenderOrder.ACTOR,
                                     fighter=fighter_component,
                                     ai=ai_component)
                else:
                    fighter_component = Fighter(hp=randint(18, 22),
                                                defense=1,
                                                power=6,
                                                xp=100)
                    ai_component = BasicMonster()

                    monster = Entity(x,
                                     y,
                                     constants['troll_tile'],
                                     libtcod.white,
                                     'Troll',
                                     blocks=True,
                                     render_order=RenderOrder.ACTOR,
                                     fighter=fighter_component,
                                     ai=ai_component)

                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([
                    entity
                    for entity in entities if entity.x == x and entity.y == y
            ]):
                item_choice = random_choice_from_dict(item_chances)

                if item_choice == 'healing_potion':
                    item_component = Item(use_function=heal,
                                          amount=randint(8, 11))
                    item = Entity(x,
                                  y,
                                  constants['potion_tile'],
                                  libtcod.violet,
                                  'Healing Potion',
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)

                elif item_choice == 'sword':
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND,
                                                      power_bonus=3)
                    item = Entity(x,
                                  y,
                                  constants['sword_tile'],
                                  libtcod.sky,
                                  'Sword',
                                  render_order=RenderOrder.ITEM,
                                  equippable=equippable_component)

                elif item_choice == 'shield':
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND,
                                                      defense_bonus=1)
                    item = Entity(x,
                                  y,
                                  constants['shield_tile'],
                                  libtcod.darker_orange,
                                  'Shield',
                                  render_order=RenderOrder.ITEM,
                                  equippable=equippable_component)

                elif item_choice == 'fireball_scroll':
                    item_component = Item(
                        use_function=cast_fireball,
                        targeting=True,
                        targeting_message=Message(
                            'Left click a target tile for the fireball, or right click to cancel.',
                            libtcod.light_cyan),
                        damage=randint(12, 15),
                        radius=3)
                    item = Entity(x,
                                  y,
                                  constants['scroll_tile'],
                                  libtcod.light_red,
                                  'Fireball Scroll',
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)

                elif item_choice == 'confusion_scroll':
                    item_component = Item(
                        use_function=cast_confuse,
                        targeting=True,
                        targeting_message=Message(
                            'Left click an enemy to confuse it, or right click to cancel.',
                            libtcod.light_cyan))
                    item = Entity(x,
                                  y,
                                  constants['scroll_tile'],
                                  libtcod.yellow,
                                  'Confusion Scroll',
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)

                else:
                    item_component = Item(use_function=cast_lightning,
                                          damage=randint(18, 30),
                                          maximum_range=5)
                    item = Entity(x,
                                  y,
                                  constants['scroll_tile'],
                                  libtcod.azure,
                                  'Lightning Scroll',
                                  render_order=RenderOrder.ITEM,
                                  item=item_component)

                entities.append(item)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(constants['max_rooms'], constants['room_min_size'],
                      constants['room_max_size'], constants['map_width'],
                      constants['map_height'], player, entities, constants)

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(
            Message('You take a moment to rest, and recover your strenth.',
                    libtcod.light_violet))

        return entities
