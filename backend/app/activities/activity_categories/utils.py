from typing import Dict, Tuple

CANONICAL_ACTIVITY_CATEGORIES: Dict[int, Tuple[str, str]] = {
    1: ("recovery", "Recovery"),
    2: ("easy", "Easy"),
    3: ("steady", "Steady"),
    4: ("tempo", "Tempo"),
    5: ("threshold", "Threshold"),
    6: ("vo2_max", "VO₂ Max"),
    7: ("anaerobic", "Anaerobic"),
    8: ("long", "Long"),
    9: ("race", "Race / Event"),
    10: ("mixed", "Mixed / Structured"),
}
