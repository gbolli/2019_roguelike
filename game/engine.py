import tcod as libtcod

from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import MessageLog, Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse
from map_objects.game_map import GameMap
from render_functions import render_all, clear_all, RenderOrder
from loader_functions.initialize_new_game import get_constants


def main():
    # variables
    constants = get_constants()

    # screen_width = 80
    # screen_height = 50

    # bar_width = 20
    # panel_height = 7
    # panel_y = screen_height - panel_height

    # message_x = bar_width + 2
    # message_width = screen_width - bar_width - 2
    # message_height = panel_height - 1

    # map_width = 80
    # map_height = 43

    # room_max_size = 10
    # room_min_size = 6
    # max_rooms = 30

    # fov_algorithm = 0  # ibtcod.FOV_BASIC
    # fov_light_walls = True
    # fov_radius = 7

    # max_monsters_per_room = 3
    # max_items_per_room = 2

    # colors = {
    #     'dark_wall': libtcod.Color(0, 0, 50),
    #     'dark_ground': libtcod.Color(50, 50, 150),
    #     'light_wall': libtcod.Color(50, 50, 100),  # (130, 110, 50),
    #     'light_ground': libtcod.Color(75, 75, 175)
    # }

    # create player
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_component = Inventory(26)
    player = Entity(0,
                    0,
                    '@',
                    libtcod.green,
                    'Player',
                    blocks=True,
                    render_order=RenderOrder.ACTOR,
                    fighter=fighter_component,
                    inventory=inventory_component)
    entities = [player]

    # set graphics template (source, type, layout)
    libtcod.console_set_custom_font(
        'arial10x10.png',
        libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # create screen (width, height, title, fullscreen_boolean)
    libtcod.console_init_root(constants['screen_width'],
                              constants['screen_height'],
                              constants['window_title'], False)

    # initialize console
    con = libtcod.console_new(constants['screen_width'],
                              constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'],
                                constants['panel_height'])

    # initialize game_map
    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'],
                      constants['room_max_size'], constants['map_width'],
                      constants['map_height'], player, entities,
                      constants['max_monsters_per_room'],
                      constants['max_items_per_room'])

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    message_log = MessageLog(constants['message_x'],
                             constants['message_width'],
                             constants['message_height'])

    # variables for key and mouse inputs
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # game loop
    game_state = GameStates.PLAYER_TURN
    previous_game_state = game_state

    targeting_item = None

    while not libtcod.console_is_window_closed():

        # capture new events / user input
        libtcod.sys_check_for_event(
            libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        # recompute field of view (fov) if player has moved
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'],
                          constants['fov_light_walls'],
                          constants['fov_algorithm'])

        # draw all:  game map, entities, ...
        render_all(con, panel, entities, player, game_map, fov_map,
                   fov_recompute, message_log, constants['screen_width'],
                   constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], mouse,
                   constants['colors'], game_state)

        fov_recompute = False

        libtcod.console_flush()

        # clear after drawing on screen
        clear_all(con, entities)

        # key pressed handling
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            # check for blocked before moving
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(
                    entities, destination_x, destination_y)
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break

            else:
                message_log.add_message(
                    Message('There is nothing here to pick up.',
                            libtcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(
                    player.inventory.use(item,
                                         entities=entities,
                                         fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item,
                                                        entities=entities,
                                                        fov_map=fov_map,
                                                        target_x=target_x,
                                                        target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(
                        player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYER_TURN


if __name__ == '__main__':
    main()
