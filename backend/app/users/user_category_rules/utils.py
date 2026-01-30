"""
Canonical user category rules for running activity type.

Mapping structure:
USER_CATEGORY_RULES: dict[int, dict] where key is category_id and
value is a dict with the fields required to insert into user_category_rules.
"""
from typing import Dict

# Default values to be used when creating user category rules for a user.
USER_CATEGORY_RULES: Dict[int, dict] = {
    1: {
        "activity_type_id": 1,
        "category_id": 1,
        "min_distance": 2000,
        "max_distance": 8000,
        "min_hr": 90,
        "max_hr": 120,
        "min_elevation_gain": 0,
        "max_elevation_gain": 150,
    },
    2: {
        "activity_type_id": 1,
        "category_id": 2,
        "min_distance": 3000,
        "max_distance": 15000,
        "min_hr": 110,
        "max_hr": 140,
        "min_elevation_gain": 0,
        "max_elevation_gain": 300,
    },
    3: {
        "activity_type_id": 1,
        "category_id": 3,
        "min_distance": 5000,
        "max_distance": 18000,
        "min_hr": 130,
        "max_hr": 155,
        "min_elevation_gain": 0,
        "max_elevation_gain": 500,
    },
    4: {
        "activity_type_id": 1,
        "category_id": 4,
        "min_distance": 5000,
        "max_distance": 20000,
        "min_hr": 150,
        "max_hr": 170,
        "min_elevation_gain": 0,
        "max_elevation_gain": 600,
    },
    5: {
        "activity_type_id": 1,
        "category_id": 5,
        "min_distance": 4000,
        "max_distance": 15000,
        "min_hr": 165,
        "max_hr": 180,
        "min_elevation_gain": 0,
        "max_elevation_gain": 700,
    },
    6: {
        "activity_type_id": 1,
        "category_id": 6,
        "min_distance": 2000,
        "max_distance": 10000,
        "min_hr": 175,
        "max_hr": 190,
        "min_elevation_gain": 0,
        "max_elevation_gain": 800,
    },
    7: {
        "activity_type_id": 1,
        "category_id": 7,
        "min_distance": 500,
        "max_distance": 6000,
        "min_hr": 180,
        "max_hr": 200,
        "min_elevation_gain": 0,
        "max_elevation_gain": 500,
    },
    8: {
        "activity_type_id": 1,
        "category_id": 8,
        "min_distance": 15000,
        "max_distance": 40000,
        "min_hr": 120,
        "max_hr": 155,
        "min_elevation_gain": 0,
        "max_elevation_gain": 1200,
    },
    9: {
        "activity_type_id": 1,
        "category_id": 9,
        "min_distance": 3000,
        "max_distance": 42000,
        "min_hr": 160,
        "max_hr": 200,
        "min_elevation_gain": 0,
        "max_elevation_gain": 2000,
    },
    10: {
        "activity_type_id": 1,
        "category_id": 10,
        "min_distance": 3000,
        "max_distance": 25000,
        "min_hr": 120,
        "max_hr": 190,
        "min_elevation_gain": 0,
        "max_elevation_gain": 1000,
    },
}
