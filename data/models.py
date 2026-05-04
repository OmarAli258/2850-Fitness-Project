from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """Represents a registered user in the FitTrack application.

    Schema:
        id (str): UUID primary key
        name (str): Display name
        email (str): Unique email address, used for login
        password (str): Hashed password
    """
    id: str
    name: str
    email: str
    password: str


@dataclass
class Activity:
    """Represents a logged workout activity.

    Schema:
        id (str): UUID primary key
        user_id (str): Foreign key to users(id)
        type (str): Exercise type (Running, Walking, Cycling, Swimming, Gym, Weights)
        date (str): Date of the activity in YYYY-MM-DD format
        duration (int): Duration in minutes
        distance (str|None): Distance string (e.g. "5.2 km") or None
        notes (str|None): Optional notes about the activity
        route_data (str|None): JSON-encoded GPS route coordinates or None
        plan_id (str|None): Foreign key to plans(id) if linked to a training plan
    """
    id: str
    user_id: str
    type: str
    date: str
    duration: int
    distance: Optional[str]
    notes: Optional[str]
    route_data: Optional[str]
    plan_id: Optional[str]


@dataclass
class Race:
    """Represents a race event tracked by the user.

    Schema:
        id (int): Auto-incrementing primary key
        user_id (str): Foreign key to users(id)
        name (str): Race name
        race_type (str): Sport/type of race
        location (str): Where the race took place
        date (str): Race date in YYYY-MM-DD format
        finish_time (str|None): Recorded finish time or None if not completed
        is_pb (int): 1 if this is a personal best for the race type, 0 otherwise
        status (str): "upcoming" or "past"
    """
    id: int
    user_id: str
    name: str
    race_type: str
    location: str
    date: str
    finish_time: Optional[str]
    is_pb: int
    status: str


@dataclass
class Plan:
    """Represents a structured exercise/training plan.

    Schema:
        id (str): UUID primary key
        user_id (str): Foreign key to users(id)
        name (str): Custom plan name (e.g. "Marathon Training")
        exercise_type (str): Associated exercise type
        frequency (str): How often (e.g. "daily", "3x per week", "weekly")
        target_duration (int|None): Target minutes per session or None
        target_distance (str|None): Target distance string or None
        notes (str|None): Optional notes or goals
        created_at (str): Timestamp of plan creation (YYYY-MM-DD HH:MM:SS)
        status (str): "active", "paused", or "completed"
    """
    id: str
    user_id: str
    name: str
    exercise_type: str
    frequency: str
    target_duration: Optional[int]
    target_distance: Optional[str]
    notes: Optional[str]
    created_at: str
    status: str