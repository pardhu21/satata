from datetime import datetime, timezone
from activities.activity.schema import Activity
from users.user_activity_stats.schema import UserActivityStats

def update_running_stat(
    value: float | None,
    mean: float | None,
    m2: float | None,
    count: int,
):
    if value is None:
        return mean, m2

    if count == 0 or mean is None or m2 is None:
        # first data point
        return value, 0.0

    delta = value - mean
    mean_new = mean + delta / (count + 1)
    delta2 = value - mean_new
    m2_new = m2 + delta * delta2

    return mean_new, m2_new

def update_user_category_stats(
    stats: UserActivityStats,
    activity: Activity,
) -> UserActivityStats:

    count = stats.total_count or 0
    new_count = count + 1

    avg_distance, m2_distance = update_running_stat(
        activity.distance,
        stats.avg_distance,
        stats.m2_distance,
        count,
    )

    avg_hr, m2_hr = update_running_stat(
        activity.average_hr,
        stats.avg_heart_rate,
        stats.m2_heart_rate,
        count,
    )

    avg_elev_gain, m2_elev_gain = update_running_stat(
        activity.elevation_gain,
        stats.avg_elevation_gain,
        stats.m2_elevation_gain,
        count,
    )

    avg_elev_loss, m2_elev_loss = update_running_stat(
        activity.elevation_loss,
        stats.avg_elevation_loss,
        stats.m2_elevation_loss,
        count,
    )

    stats.avg_distance = avg_distance
    stats.m2_distance = m2_distance

    stats.avg_heart_rate = avg_hr
    stats.m2_heart_rate = m2_hr

    stats.avg_elevation_gain = avg_elev_gain
    stats.m2_elevation_gain = m2_elev_gain

    stats.avg_elevation_loss = avg_elev_loss
    stats.m2_elevation_loss = m2_elev_loss

    stats.total_count = new_count
    stats.updated_at = datetime.now(timezone.utc).isoformat()

    return stats
