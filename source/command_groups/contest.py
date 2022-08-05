from discord import app_commands

class Contest(app_commands.Group):
    pass

def setup(tree: app_commands.CommandTree) -> None:
    tree.add_command(Contest())
