from enum import Enum

class ROTMG_Class(Enum):
    rogue = ()
    archer = ()
    wizard = ()
    priest = ()
    warrior = ()
    knight = ()
    paladin = ()
    assassin = ()
    necromancer = ()
    huntress = ()
    mystic = ()
    trickster = ()
    sorcerer = ()
    ninja = ()
    samurai = ()
    bard = ()

    def __str__(self) -> str:
        return str(self.name)