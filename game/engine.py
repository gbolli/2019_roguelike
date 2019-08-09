import tcod as libtcod
from input_handlers import handle_keys


def main():
    # variables
    screen_width = 80
    screen_height = 50

    player_x = int(screen_width / 2)
    player_y = int(screen_height / 2)

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

        # color for character (console, color)
        libtcod.console_set_default_foreground(con, libtcod.green)

        # starting point setup (console, x, y, character, background)
        libtcod.console_put_char(
            con, player_x, player_y, '@', libtcod.BKGND_NONE)

        libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

        libtcod.console_flush()

        libtcod.console_put_char(
            con, player_x, player_y, ' ', libtcod.BKGND_NONE)

        # key pressed handling
        action = handle_keys(key)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move:
            dx, dy = move
            player_x += dx
            player_y += dy

        if exit:
            return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())


if __name__ == '__main__':
    main()
