import tcod as libtcod

from entity import Entity
from input_handlers import handle_keys
from render_functions import render_all, clear_all


def main():
    # variables
    screen_width = 80
    screen_height = 50

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

    con = libtcod.console_new(screen_width, screen_height, )

    # variables for key and mouse inputs
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # game loop
    while not libtcod.console_is_window_closed():

        # capture new events / user input
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # draw all entities
        render_all(con, entities, screen_width, screen_height)

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
            player.move(dx, dy)

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
    main()
