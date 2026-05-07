# this file keeps the dataclass models used to describe the main app data
# these models make user, activity, race and plan data easier to pass around

# import dataclass for simple data objects and optional for fields that can be empty
from dataclasses import dataclass
from typing import Optional


# this class stores the main details for a registered user
@dataclass
class User:
    id: str
    name: str
    email: str
    password: str


# this class stores one workout activity logged by a user
@dataclass
class Activity:
    id: str
    user_id: str
    type: str
    date: str
    duration: int
    distance: Optional[str]
    notes: Optional[str]
    route_data: Optional[str]
    plan_id: Optional[str]


# this class stores one race event saved by a user
@dataclass
class Race:
    id: int
    user_id: str
    name: str
    race_type: str
    location: str
    date: str
    finish_time: Optional[str]
    is_pb: int
    status: str


# this class stores one structured training plan created by a user
@dataclass
class Plan:
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


# done comments for data/models.py
# summary of comments:
# - explains that this file holds dataclass models
# - shows the user model fields
# - shows the activity model fields
# - shows the race model fields
# - shows the plan model fields
