import tcod as libtcod

from entity import Entity
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import render_all, clear_all


def main():
    # variables
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150)
    }

    player = Entity(int(screen_width / 2),
                    int(screen_height / 2), '@', libtcod.green)
    npc = Entity(int(screen_width / 2 - 5),
                 int(screen_height / 2), '@', libtcod.yellow)
    entities = [npc, player]

    # set graphics template (source, type, layout)
    libtcod.console_set_custom_font(
        'arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # create screen (width, height, title, fullscreen_boolean)
    libtcod.console_init_root(
        screen_width, screen_height, 'game name placeholder', False)

    # initialize console
    con = libtcod.console_new(screen_width, screen_height)

    # initialize game_map
    game_map = GameMap(map_width, map_height)

    # variables for key and mouse inputs
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # game loop
    while not libtcod.console_is_window_closed():

        # capture new events / user input
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # draw all:  game map, entities, ...
        render_all(con, entities, game_map,
                   screen_width, screen_height, colors)

        libtcod.console_flush()

        # clear after drawing on screen
        clear_all(con, entities)

        # key pressed handling
        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            # check for blocked before moving
            if not game_map.is_blocked(player.x + dx, player.y + dy):
                player.move(dx, dy)

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
    main()
