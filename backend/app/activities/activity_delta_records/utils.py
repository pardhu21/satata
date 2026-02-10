import math
from typing import Iterable, Optional
from activities.activity.schema import Activity
from users.user_category_rules.schema import UserCategoryRule
from activities.activity_delta_records.schema import ActivityDeltaRecord
from users.user_activity_stats.schema import UserActivityStats


def midpoint(min_val, max_val):
    if min_val is None or max_val is None:
        return None
    return (min_val + max_val) / 2


def norm_delta(value, mid_val):
    if value is None or mid_val is None or mid_val == 0:
        return 0.0
    return abs(value - mid_val) / mid_val


def classify_activity_by_rule_vectors(
    activity: Activity,
    rules: Iterable[UserCategoryRule],
) -> Optional[int]:
    """
    Returns category_id of the closest rule centroid
    """

    best_category_id = None
    best_distance = float("inf")

    for rule in rules:
        if rule.activity_type_id != activity.activity_type:
            continue

        # Normalized deltas using midpoints (assuming these midpoints are directly provided now)
        values = rule.values
        d_dist = norm_delta(activity.distance, values.get('distance'))
        d_hr = norm_delta(activity.average_hr, values.get('hr'))
        d_elev = norm_delta(activity.elevation_gain, values.get('elevation_gain'))

        # Vector distance (Euclidean distance between points)
        distance = math.sqrt(d_dist ** 2 + d_hr ** 2 + d_elev ** 2)

        if distance < best_distance:
            best_distance = distance
            best_category_id = rule.category_id

    return best_category_id


def compute_delta(value, avg):
    if value is None or avg is None:
        return None
    return float(value) - float(avg)


def compute_delta_pct(delta: float | None, baseline: float | None):
    if delta is None or baseline in (None, 0):
        return None
    return (delta / baseline) * 100


def compute_activity_delta(
    category_id: int,
    stats: Optional[UserActivityStats],
    activity: Activity,
) -> ActivityDeltaRecord:

    # If user stats are missing, return record with no deltas
    if stats is None:
        return ActivityDeltaRecord(
            user_id=activity.user_id,
            activity_id=activity.id,
            activity_type_id=activity.activity_type,
            category_id=category_id,

            delta_distance=None,
            delta_distance_pct=None,

            delta_hr=None,
            delta_hr_pct=None,

            delta_avg_pace=None,
            delta_avg_pace_pct=None,

            delta_duration=None,
            delta_duration_pct=None,

            delta_elevation_gain=None,
            delta_elevation_gain_pct=None,

            delta_elevation_loss=None,
            delta_elevation_loss_pct=None,
        )

    delta_distance = compute_delta(activity.distance, stats.avg_distance)
    delta_distance_pct = compute_delta_pct(delta_distance, stats.avg_distance)

    delta_hr = compute_delta(activity.average_hr, stats.avg_heart_rate)
    delta_hr_pct = compute_delta_pct(delta_hr, stats.avg_heart_rate)

    delta_pace = compute_delta(activity.pace, stats.avg_pace)
    delta_pace_pct = compute_delta_pct(delta_pace, stats.avg_pace)

    delta_duration = compute_delta(activity.total_elapsed_time, stats.avg_duration)
    delta_duration_pct = compute_delta_pct(delta_duration, stats.avg_duration)

    delta_elev_gain = compute_delta(activity.elevation_gain, stats.avg_elevation_gain)
    delta_elev_gain_pct = compute_delta_pct(delta_elev_gain, stats.avg_elevation_gain)

    delta_elev_loss = compute_delta(activity.elevation_loss, stats.avg_elevation_loss)
    delta_elev_loss_pct = compute_delta_pct(delta_elev_loss, stats.avg_elevation_loss)

    return ActivityDeltaRecord(
        user_id=activity.user_id,
        activity_id=activity.id,
        activity_type_id=activity.activity_type,
        category_id=category_id,

        delta_distance=delta_distance,
        delta_distance_pct=delta_distance_pct,

        delta_hr=delta_hr,
        delta_hr_pct=delta_hr_pct,

        delta_avg_pace=delta_pace,
        delta_avg_pace_pct=delta_pace_pct,

        delta_duration=delta_duration,
        delta_duration_pct=delta_duration_pct,

        delta_elevation_gain=delta_elev_gain,
        delta_elevation_gain_pct=delta_elev_gain_pct,

        delta_elevation_loss=delta_elev_loss,
        delta_elevation_loss_pct=delta_elev_loss_pct,
    )
