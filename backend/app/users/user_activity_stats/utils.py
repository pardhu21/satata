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

    delta = float(value) - float(mean)
    mean_new = mean + delta / (count + 1)
    delta2 = float(value) - float(mean_new)
    m2_new = m2 + delta * delta2

    return mean_new, m2_new



def update_user_category_stats(
    category_id: int,
    stats: UserActivityStats | None,
    activity: Activity,
) -> UserActivityStats:

    now = datetime.now(timezone.utc).isoformat()

    # First activity → initialize stats
    if stats is None:
        return UserActivityStats(
            user_id=activity.user_id,
            activity_type_id=activity.activity_type,
            category_id=category_id,

            avg_distance=activity.distance,
            m2_distance=0.0,

            avg_heart_rate=activity.average_hr,
            m2_heart_rate=0.0,

            avg_pace=activity.pace,
            m2_pace=0.0,

            avg_duration=activity.total_elapsed_time,
            m2_duration=0.0,

            avg_elevation_gain=activity.elevation_gain,
            m2_elevation_gain=0.0,

            avg_elevation_loss=activity.elevation_loss,
            m2_elevation_loss=0.0,

            total_count=1,
            updated_at=now,
        )

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

    avg_pace, m2_pace = update_running_stat(
        activity.pace,
        stats.avg_pace,
        stats.m2_pace,
        count,
    )

    avg_duration, m2_duration = update_running_stat(
        activity.total_elapsed_time,
        stats.avg_duration,
        stats.m2_duration,
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

    stats.avg_pace = avg_pace
    stats.m2_pace = m2_pace

    stats.avg_duration = avg_duration
    stats.m2_duration = m2_duration

    stats.avg_elevation_gain = avg_elev_gain
    stats.m2_elevation_gain = m2_elev_gain

    stats.avg_elevation_loss = avg_elev_loss
    stats.m2_elevation_loss = m2_elev_loss

    stats.total_count = new_count
    stats.updated_at = now

    return stats
