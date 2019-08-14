import tcod as libtcod

from components.fighter import Fighter
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import render_all, clear_all


def main():
    # variables
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0  # ibtcod.FOV_BASIC
    fov_light_walls = True
    fov_radius = 7

    max_monsters_per_room = 3

    colors = {
        'dark_wall': libtcod.Color(0, 0, 50),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(50, 50, 100),  # (130, 110, 50),
        'light_ground': libtcod.Color(75, 75, 175)
    }

    # create player
    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = Entity(0,
                    0,
                    '@',
                    libtcod.green,
                    'Player',
                    blocks=True,
                    fighter=fighter_component)
    entities = [player]

    # set graphics template (source, type, layout)
    libtcod.console_set_custom_font(
        'arial10x10.png',
        libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # create screen (width, height, title, fullscreen_boolean)
    libtcod.console_init_root(screen_width, screen_height,
                              'game name placeholder', False)

    # initialize console
    con = libtcod.console_new(screen_width, screen_height)

    # initialize game_map
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width,
                      map_height, player, entities, max_monsters_per_room)

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    # variables for key and mouse inputs
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # game loop
    game_state = GameStates.PLAYER_TURN

    while not libtcod.console_is_window_closed():

        # capture new events / user input
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # recompute field of view (fov) if player has moved
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius,
                          fov_light_walls, fov_algorithm)

        # draw all:  game map, entities, ...
        render_all(con, entities, game_map, fov_map, fov_recompute,
                   screen_width, screen_height, colors)

        fov_recompute = False

        libtcod.console_flush()

        # clear after drawing on screen
        clear_all(con, entities)

        # key pressed handling
        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            # check for blocked before moving
            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(
                    entities, destination_x, destination_y)
                if target:
                    # placeholder for player combat / interaction code
                    print('You kick the ' + target.name +
                          ' in the shin, much to its chagrin!')
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    entity.ai.take_turn(player, fov_map, game_map, entities)

            game_state = GameStates.PLAYER_TURN


if __name__ == '__main__':
    main()
