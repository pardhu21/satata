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


def norm_delta(value, min_val, max_val):
    if value is None or min_val is None or max_val is None:
        return 0.0

    span = max_val - min_val
    if span == 0:
        return 0.0

    mid = midpoint(min_val, max_val)
    return abs(value - mid) / span

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

        # Normalized deltas
        d_dist = norm_delta(
            activity.distance,
            rule.min_distance,
            rule.max_distance,
        )

        d_hr = norm_delta(
            activity.average_hr,
            rule.min_hr,
            rule.max_hr,
        )

        d_elev = norm_delta(
            activity.elevation_gain,
            rule.min_elevation_gain,
            rule.max_elevation_gain,
        )

        # Vector distance
        distance = math.sqrt(
            d_dist ** 2 +
            d_hr ** 2 +
            d_elev ** 2
        )

        if distance < best_distance:
            best_distance = distance
            best_category_id = rule.category_id

    return best_category_id

def compute_delta(value: float | None, baseline: float | None):
    if value is None or baseline is None:
        return None
    return value - baseline


def compute_delta_pct(delta: float | None, baseline: float | None):
    if delta is None or baseline in (None, 0):
        return None
    return (delta / baseline) * 100


def compute_activity_delta(
    stats: UserActivityStats,
    activity: Activity,
) -> ActivityDeltaRecord:

    delta_distance = compute_delta(activity.distance, stats.avg_distance)
    delta_distance_pct = compute_delta_pct(delta_distance, stats.avg_distance)

    delta_hr = compute_delta(activity.average_hr, stats.avg_heart_rate)
    delta_hr_pct = compute_delta_pct(delta_hr, stats.avg_heart_rate)

    delta_elev_gain = compute_delta(
        activity.elevation_gain, stats.avg_elevation_gain
    )
    delta_elev_gain_pct = compute_delta_pct(
        delta_elev_gain, stats.avg_elevation_gain
    )

    delta_elev_loss = compute_delta(
        activity.elevation_loss, stats.avg_elevation_loss
    )
    delta_elev_loss_pct = compute_delta_pct(
        delta_elev_loss, stats.avg_elevation_loss
    )

    return ActivityDeltaRecord(
        activity_id=activity.id,
        user_category_id=stats.user_category_id,

        delta_distance=delta_distance,
        delta_distance_pct=delta_distance_pct,

        delta_hr=delta_hr,
        delta_hr_pct=delta_hr_pct,

        delta_elevation_gain=delta_elev_gain,
        delta_elevation_gain_pct=delta_elev_gain_pct,

        delta_elevation_loss=delta_elev_loss,
        delta_elevation_loss_pct=delta_elev_loss_pct,
    )
