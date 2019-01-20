import fast_json


def keyboard_markup(options=None, header=None, n_col=2):
    if options:
        return build_menu(
            options,
            n_cols=n_col,
            footer_buttons=["Отмена"],
            header_buttons=header,
        )
    else:
        return remove_keyboard()


def remove_keyboard():
    return fast_json.dumps({"remove_keyboard": True})


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i : i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return fast_json.dumps({"keyboard": menu})
