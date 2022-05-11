from vk_base.Config import search_commands, commands, json_commands


def command_handler(*args):
    def decorator(fn):
        for i in args:
            commands[i.lower()] = fn
    return decorator


def search_command_handler(*args):
    def decorator(fn):
        for i in args:
            search_commands[i[0].lower()] = [fn, i[1]]
    return decorator


def json_command_handler(*args):
    def decorator(fn):
        for i in args:
            commands[i.lower()] = fn
            json_commands[i] = fn

    return decorator


def get_dicts():
    return commands, json_commands, search_commands