from dataclasses import dataclass


@dataclass
class CharacterPayload:
    id: int
    user_id: int
    rotmg_class: str
    keywords: set
    points: int
    is_active: bool


@dataclass
class ContestPayload:
    id: int
    contest_type_name: str
    start_time: float
    end_time: float
    post_id: int
    is_active: bool


@dataclass
class ContestantPayload:
    user_id: int
    is_banned: bool
