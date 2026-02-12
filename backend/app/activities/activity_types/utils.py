import json
from typing import Any, Dict, List, Optional

from activities.activity.constants import ACTIVITY_ID_TO_NAME
import activities.activity_categories.utils as activity_category_utils


def normal_to_snake_case(value: str) -> str:
    """
    Convert a human-friendly string to snake_case.

    Args:
        value: The input string.

    Returns:
        The snake_cased string.

    Raises:
        ValueError: If value is None.
    """
    if value is None:
        raise ValueError("value cannot be None")

    import re

    s = value.strip().lower()
    # Replace any sequence of non-alphanumeric characters with underscore
    s = re.sub(r"[^a-z0-9]+", "_", s)
    # Collapse multiple underscores into one
    s = re.sub(r"_+", "_", s)
    # Trim leading/trailing underscores
    s = s.strip("_")
    return s


# Static parameter mappings for AI insights per activity type (by normalized snake_case name).
# These mappings remain static, while the list of activity types is auto-derived from
# activities.activity.utils.ACTIVITY_ID_TO_NAME so future edits there reflect automatically here.
AI_INSIGHT_DEFAULT_PARAMS_BY_ACTIVITY: Dict[str, List[str]] = {
    # Running family
    "run": ["hr", "distance", "elevation_gain", "pace", "cadence"],
    "trail_run": ["hr", "distance", "elevation_gain", "pace", "cadence"],
    "virtual_run": ["hr", "distance", "elevation_gain", "pace", "cadence"],
    "track_run": ["hr", "distance", "elevation_gain", "pace", "cadence"],
    "treadmill": ["hr", "distance", "pace", "cadence"],

    # Cycling family
    "ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],
    "gravel_ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],
    "mtb_ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],
    "virtual_ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],
    "commuting_ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],
    "indoor_ride": ["power", "hr", "distance", "speed", "cadence"],
    "mixed_surface_ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],
    "e_bike_ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],
    "e_mountain_bike_ride": ["power", "hr", "distance", "elevation_gain", "speed", "cadence"],

    # Swimming family
    "lap_swimming": ["distance", "pace", "hr"],
    "open_water_swimming": ["distance", "pace", "hr"],

    # Walk / Hike
    "walk": ["hr", "distance", "elevation_gain", "pace"],
    "indoor_walking": ["hr", "distance", "pace"],
    "hike": ["hr", "distance", "elevation_gain", "pace"],

    # Rowing
    "rowing": ["power", "hr", "distance", "cadence", "pace"],

    # Gym / bodyweight
    "workout": ["hr", "distance"],
    "strength_training": ["hr"],
    "crossfit": ["hr"],
    "hiit": ["hr"],
    "cardio_training": ["hr", "distance", "pace"],
    "yoga": ["hr"],

    # Snow sports
    "alpine_ski": ["distance", "elevation_gain", "speed", "hr"],
    "nordic_ski": ["distance", "elevation_gain", "speed", "hr"],
    "snowboard": ["distance", "elevation_gain", "speed", "hr"],
    "snow_shoeing": ["distance", "elevation_gain", "hr"],

    # Skating
    "ice_skate": ["distance", "speed", "hr"],
    "inline_skating": ["distance", "speed", "hr"],

    # Water and board
    "windsurf": ["distance", "speed", "hr"],
    "sailing": ["distance", "speed", "hr"],
    "surf": ["distance", "speed", "hr"],
    "stand_up_paddling": ["distance", "speed", "hr"],
    "kayaking": ["distance", "speed", "hr"],

    # Field and racket
    "soccer": ["hr", "distance", "pace"],
    "tennis": ["hr"],
    "tabletennis": ["hr"],
    "badminton": ["hr"],
    "squash": ["hr"],
    "racquetball": ["hr"],
    "pickleball": ["hr"],

    # Transitions / misc
    "transition": [],
}


def get_parameters_for_activity(display_name: str) -> Optional[List[str]]:
    """
    Return the default parameter list for AI insights for a given activity display name.

    The lookup uses the normalized snake_case of the provided display name.
    Returns None when there is no static mapping for the activity.
    """
    key = normal_to_snake_case(display_name)
    return AI_INSIGHT_DEFAULT_PARAMS_BY_ACTIVITY.get(key)


# -----------------------------
# Category defaults per activity
# -----------------------------
# Build sensible single-value defaults per category for each activity.
# Units:
# - distance: meters
# - elevation_gain: meters
# - hr: beats per minute
# - power: watts
# - cadence: steps per minute (run) / rpm (ride) / spm (row)
# Only parameters present in AI_INSIGHT_DEFAULT_PARAMS_BY_ACTIVITY will be emitted for an activity.

# Canonical category names list (ordered by ID)
_CATEGORY_NAMES = [
    name for _id, (name, _disp) in sorted(activity_category_utils.CANONICAL_ACTIVITY_CATEGORIES.items())
]

# Grouping helpers
_RUN_GROUP = {
    "run",
    "trail_run",
    "virtual_run",
    "track_run",
    "treadmill",
}
_RIDE_GROUP = {
    "ride",
    "gravel_ride",
    "mtb_ride",
    "virtual_ride",
    "commuting_ride",
    "indoor_ride",
    "mixed_surface_ride",
    "e_bike_ride",
    "e_mountain_bike_ride",
}
_SWIM_GROUP = {"lap_swimming", "open_water_swimming"}
_WALK_GROUP = {"walk", "indoor_walking"}
_HIKE_GROUP = {"hike"}
_ROW_GROUP = {"rowing"}
_GYM_GROUP = {"workout", "strength_training", "crossfit", "hiit", "cardio_training", "yoga"}
_SNOW_GROUP = {"alpine_ski", "nordic_ski", "snowboard", "snow_shoeing"}
_SKATE_GROUP = {"ice_skate", "inline_skating"}
_WATER_GROUP = {"windsurf", "sailing", "surf", "stand_up_paddling", "kayaking"}
_FIELD_GROUP = {"soccer", "tennis", "tabletennis", "badminton", "squash", "racquetball", "pickleball"}
_TRANSITION_GROUP = {"transition"}


def _activity_group(internal_name: str) -> str:
    if internal_name in _RUN_GROUP:
        return "run"
    if internal_name in _RIDE_GROUP:
        return "ride"
    if internal_name in _SWIM_GROUP:
        return "swim"
    if internal_name in _WALK_GROUP:
        return "walk"
    if internal_name in _HIKE_GROUP:
        return "hike"
    if internal_name in _ROW_GROUP:
        return "row"
    if internal_name in _GYM_GROUP:
        return "gym"
    if internal_name in _SNOW_GROUP:
        return "snow"
    if internal_name in _SKATE_GROUP:
        return "skate"
    if internal_name in _WATER_GROUP:
        return "water"
    if internal_name in _FIELD_GROUP:
        return "field"
    if internal_name in _TRANSITION_GROUP:
        return "transition"
    return "other"


# Default templates per group and category
_RUN_DEFAULTS = {
    "hr": {
        "recovery": 110,
        "easy": 125,
        "steady": 140,
        "tempo": 155,
        "threshold": 170,
        "vo2_max": 180,
        "anaerobic": 190,
        "long": 135,
        "race": 175,
        "mixed": 150,
    },
    "distance": {
        "recovery": 3000,
        "easy": 5000,
        "steady": 8000,
        "tempo": 10000,
        "threshold": 12000,
        "vo2_max": 3000,
        "anaerobic": 1000,
        "long": 20000,
        "race": 21097,
        "mixed": 12000,
    },
    "elevation_gain": {
        "recovery": 50,
        "easy": 100,
        "steady": 200,
        "tempo": 200,
        "threshold": 200,
        "vo2_max": 100,
        "anaerobic": 50,
        "long": 600,
        "race": 300,
        "mixed": 400,
    },
    "cadence": {
        "recovery": 160,
        "easy": 165,
        "steady": 170,
        "tempo": 175,
        "threshold": 178,
        "vo2_max": 180,
        "anaerobic": 185,
        "long": 168,
        "race": 178,
        "mixed": 172,
    },
}

_RIDE_DEFAULTS = {
    "hr": {
        "recovery": 95,
        "easy": 110,
        "steady": 125,
        "tempo": 140,
        "threshold": 155,
        "vo2_max": 165,
        "anaerobic": 175,
        "long": 120,
        "race": 160,
        "mixed": 135,
    },
    "distance": {
        "recovery": 10000,
        "easy": 20000,
        "steady": 40000,
        "tempo": 50000,
        "threshold": 60000,
        "vo2_max": 20000,
        "anaerobic": 5000,
        "long": 80000,
        "race": 90000,
        "mixed": 50000,
    },
    "elevation_gain": {
        "recovery": 100,
        "easy": 300,
        "steady": 600,
        "tempo": 800,
        "threshold": 1000,
        "vo2_max": 400,
        "anaerobic": 200,
        "long": 1500,
        "race": 1200,
        "mixed": 900,
    },
    "power": {
        "recovery": 120,
        "easy": 150,
        "steady": 180,
        "tempo": 220,
        "threshold": 260,
        "vo2_max": 300,
        "anaerobic": 350,
        "long": 170,
        "race": 280,
        "mixed": 220,
    },
    "cadence": {
        "recovery": 85,
        "easy": 88,
        "steady": 90,
        "tempo": 92,
        "threshold": 95,
        "vo2_max": 98,
        "anaerobic": 100,
        "long": 88,
        "race": 95,
        "mixed": 92,
    },
}

_WALK_DEFAULTS = {
    "hr": {
        "recovery": 85,
        "easy": 95,
        "steady": 105,
        "tempo": 115,
        "threshold": 125,
        "vo2_max": 130,
        "anaerobic": 135,
        "long": 100,
        "race": 120,
        "mixed": 110,
    },
    "distance": {
        "recovery": 2000,
        "easy": 3000,
        "steady": 5000,
        "tempo": 6000,
        "threshold": 7000,
        "vo2_max": 8000,
        "anaerobic": 3000,
        "long": 10000,
        "race": 8000,
        "mixed": 6000,
    },
    "elevation_gain": {
        "recovery": 20,
        "easy": 40,
        "steady": 80,
        "tempo": 100,
        "threshold": 120,
        "vo2_max": 80,
        "anaerobic": 40,
        "long": 200,
        "race": 120,
        "mixed": 100,
    },
}

_HIKE_DEFAULTS = {
    "hr": {
        "recovery": 95,
        "easy": 105,
        "steady": 120,
        "tempo": 135,
        "threshold": 145,
        "vo2_max": 155,
        "anaerobic": 165,
        "long": 115,
        "race": 150,
        "mixed": 130,
    },
    "distance": {
        "recovery": 5000,
        "easy": 8000,
        "steady": 12000,
        "tempo": 15000,
        "threshold": 18000,
        "vo2_max": 8000,
        "anaerobic": 4000,
        "long": 20000,
        "race": 18000,
        "mixed": 15000,
    },
    "elevation_gain": {
        "recovery": 200,
        "easy": 400,
        "steady": 700,
        "tempo": 900,
        "threshold": 1100,
        "vo2_max": 600,
        "anaerobic": 300,
        "long": 1500,
        "race": 1200,
        "mixed": 900,
    },
}

_ROW_DEFAULTS = {
    "hr": {
        "recovery": 95,
        "easy": 110,
        "steady": 130,
        "tempo": 150,
        "threshold": 165,
        "vo2_max": 175,
        "anaerobic": 185,
        "long": 125,
        "race": 170,
        "mixed": 145,
    },
    "distance": {
        "recovery": 2000,
        "easy": 4000,
        "steady": 6000,
        "tempo": 8000,
        "threshold": 10000,
        "vo2_max": 3000,
        "anaerobic": 1000,
        "long": 12000,
        "race": 10000,
        "mixed": 8000,
    },
    "power": {
        "recovery": 100,
        "easy": 140,
        "steady": 180,
        "tempo": 220,
        "threshold": 260,
        "vo2_max": 300,
        "anaerobic": 340,
        "long": 170,
        "race": 280,
        "mixed": 220,
    },
    "cadence": {  # strokes per minute
        "recovery": 20,
        "easy": 22,
        "steady": 24,
        "tempo": 28,
        "threshold": 30,
        "vo2_max": 32,
        "anaerobic": 34,
        "long": 22,
        "race": 32,
        "mixed": 26,
    },
}

_SWIM_DEFAULTS = {
    "hr": {
        "recovery": 100,
        "easy": 115,
        "steady": 130,
        "tempo": 145,
        "threshold": 155,
        "vo2_max": 165,
        "anaerobic": 175,
        "long": 120,
        "race": 160,
        "mixed": 140,
    },
    "distance": {
        "recovery": 500,
        "easy": 1000,
        "steady": 1500,
        "tempo": 2000,
        "threshold": 2500,
        "vo2_max": 1200,
        "anaerobic": 600,
        "long": 3000,
        "race": 2500,
        "mixed": 2000,
    },
}

_SNOW_DEFAULTS = {
    "hr": {
        "recovery": 95,
        "easy": 110,
        "steady": 125,
        "tempo": 140,
        "threshold": 150,
        "vo2_max": 160,
        "anaerobic": 170,
        "long": 120,
        "race": 150,
        "mixed": 135,
    },
    "distance": {
        "recovery": 5000,
        "easy": 8000,
        "steady": 12000,
        "tempo": 15000,
        "threshold": 18000,
        "vo2_max": 7000,
        "anaerobic": 4000,
        "long": 20000,
        "race": 16000,
        "mixed": 12000,
    },
    "elevation_gain": {
        "recovery": 200,
        "easy": 400,
        "steady": 700,
        "tempo": 900,
        "threshold": 1100,
        "vo2_max": 600,
        "anaerobic": 300,
        "long": 1500,
        "race": 1200,
        "mixed": 900,
    },
}

_SKATE_DEFAULTS = {
    "hr": {
        "recovery": 95,
        "easy": 110,
        "steady": 125,
        "tempo": 140,
        "threshold": 155,
        "vo2_max": 165,
        "anaerobic": 175,
        "long": 120,
        "race": 160,
        "mixed": 140,
    },
    "distance": {
        "recovery": 3000,
        "easy": 6000,
        "steady": 12000,
        "tempo": 15000,
        "threshold": 20000,
        "vo2_max": 8000,
        "anaerobic": 4000,
        "long": 25000,
        "race": 20000,
        "mixed": 15000,
    },
}

_WATER_DEFAULTS = {
    "hr": {
        "recovery": 95,
        "easy": 105,
        "steady": 120,
        "tempo": 135,
        "threshold": 145,
        "vo2_max": 155,
        "anaerobic": 165,
        "long": 115,
        "race": 150,
        "mixed": 130,
    },
    "distance": {
        "recovery": 5000,
        "easy": 8000,
        "steady": 15000,
        "tempo": 20000,
        "threshold": 25000,
        "vo2_max": 10000,
        "anaerobic": 6000,
        "long": 30000,
        "race": 25000,
        "mixed": 20000,
    },
}

_FIELD_DEFAULTS = {
    "hr": {
        "recovery": 95,
        "easy": 110,
        "steady": 130,
        "tempo": 150,
        "threshold": 165,
        "vo2_max": 175,
        "anaerobic": 185,
        "long": 120,
        "race": 175,
        "mixed": 150,
    },
    "distance": {
        "recovery": 1000,
        "easy": 2000,
        "steady": 4000,
        "tempo": 6000,
        "threshold": 8000,
        "vo2_max": 4000,
        "anaerobic": 2000,
        "long": 8000,
        "race": 10000,
        "mixed": 6000,
    },
}

_GYM_DEFAULTS = {
    "hr": {
        "recovery": 90,
        "easy": 100,
        "steady": 110,
        "tempo": 120,
        "threshold": 130,
        "vo2_max": 140,
        "anaerobic": 150,
        "long": 100,
        "race": 130,
        "mixed": 115,
    },
    "distance": {cat: 0 for cat in _CATEGORY_NAMES},
    "elevation_gain": {cat: 0 for cat in _CATEGORY_NAMES},
}

_GROUP_DEFAULTS = {
    "run": _RUN_DEFAULTS,
    "ride": _RIDE_DEFAULTS,
    "swim": _SWIM_DEFAULTS,
    "walk": _WALK_DEFAULTS,
    "hike": _HIKE_DEFAULTS,
    "row": _ROW_DEFAULTS,
    "gym": _GYM_DEFAULTS,
    "snow": _SNOW_DEFAULTS,
    "skate": _SKATE_DEFAULTS,
    "water": _WATER_DEFAULTS,
    "field": _FIELD_DEFAULTS,
}


def build_activity_category_default_values() -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Construct a nested mapping of default parameter values per category for each activity.

    Structure:
    {
      "run": {
        "recovery": {"hr": 110, "distance": 3000, ...},
        "easy": {...},
        ...
      },
      "ride": { ... }
    }

    Notes:
    - Only emits parameters that are present in AI_INSIGHT_DEFAULT_PARAMS_BY_ACTIVITY for that activity.
    - Categories are pulled from CANONICAL_ACTIVITY_CATEGORIES to stay in sync with the source of truth.
    """
    result: Dict[str, Dict[str, Dict[str, float]]] = {}

    # Prepare canonical categories list (names only)
    categories = [name for _id, (name, _disp) in sorted(activity_category_utils.CANONICAL_ACTIVITY_CATEGORIES.items())]

    for _id, display_name in sorted(ACTIVITY_ID_TO_NAME.items(), key=lambda kv: kv[0]):
        internal_name = normal_to_snake_case(display_name)
        params_for_activity = AI_INSIGHT_DEFAULT_PARAMS_BY_ACTIVITY.get(internal_name, [])
        group = _activity_group(internal_name)
        group_defaults = _GROUP_DEFAULTS.get(group, {})

        per_category: Dict[str, Dict[str, float]] = {}
        for cat_name in categories:
            param_defaults: Dict[str, float] = {}
            for p in params_for_activity:
                # Only include parameters we have defaults for in this group
                defaults_for_param = group_defaults.get(p)
                if defaults_for_param is not None and cat_name in defaults_for_param:
                    param_defaults[p] = defaults_for_param[cat_name]
            per_category[cat_name] = param_defaults

        result[internal_name] = per_category

    return result


def build_activity_category_defaults_json(indent: int = 2) -> str:
    """Return the category defaults mapping as a JSON string."""
    return json.dumps(build_activity_category_default_values(), indent=indent)


def build_activity_types_seed_records() -> List[Dict[str, Any]]:
    """
    Build a list of seed records for ActivityTypes table derived from
    activities.activity.utils.ACTIVITY_ID_TO_NAME.

    Each record contains:
      - name: internal, normalized snake_case (unique, indexed)
      - display_name: user-facing name
      - ai_insight_parameters: optional list of strings or None

    This ensures that any future edits in the source ACTIVITY_ID_TO_NAME mapping
    are immediately reflected when this function is called.
    """
    records: List[Dict[str, Any]] = []

    # Preserve the numeric ID ordering from the source mapping for deterministic output
    for _id, display_name in sorted(ACTIVITY_ID_TO_NAME.items(), key=lambda kv: kv[0]):
        internal_name = normal_to_snake_case(display_name)
        params = get_parameters_for_activity(display_name)
        records.append(
            {
                "name": internal_name,
                "display_name": display_name,
                # Use None instead of [] when no static parameters are defined to respect nullable column
                "ai_insight_parameters": params if params is not None else None,
            }
        )

    return records


def build_activity_types_seed_json(indent: int = 2) -> str:
    """
    Return the seed records as a JSON string (suitable for seed files or migrations).
    """
    return json.dumps(build_activity_types_seed_records(), indent=indent)


__all__ = [
    "AI_INSIGHT_DEFAULT_PARAMS_BY_ACTIVITY",
    "get_parameters_for_activity",
    "build_activity_types_seed_records",
    "build_activity_types_seed_json",
]