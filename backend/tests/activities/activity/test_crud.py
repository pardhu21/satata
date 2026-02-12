import types
from importlib import import_module
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, AsyncMock, call

import pytest


# Target module
activities_crud = import_module("activities.activity.crud")


# -----------------------------
# Helpers
# -----------------------------
class QueryChain:
    """
    Chainable SQLAlchemy-like query mock supporting:
    - filter, join, order_by, offset, limit, distinct
    - all(), first(), delete()

    Each method returns self so you can build chains like:
      db.query(Model).filter(...).order_by(...).all()
    """

    def __init__(self, all_result=None, first_result=None, delete_result=0):
        self._all_result = all_result
        self._first_result = first_result
        self._delete_result = delete_result
        # Track calls for assertions if needed
        self.calls = []

    # chainable modifiers
    def filter(self, *args, **kwargs):
        self.calls.append(("filter", args, kwargs))
        return self

    def join(self, *args, **kwargs):
        self.calls.append(("join", args, kwargs))
        return self

    def order_by(self, *args, **kwargs):
        self.calls.append(("order_by", args, kwargs))
        return self

    def offset(self, *args, **kwargs):
        self.calls.append(("offset", args, kwargs))
        return self

    def limit(self, *args, **kwargs):
        self.calls.append(("limit", args, kwargs))
        return self

    def distinct(self, *args, **kwargs):
        self.calls.append(("distinct", args, kwargs))
        return self

    # terminal operations
    def all(self):
        self.calls.append(("all", (), {}))
        return self._all_result

    def first(self):
        self.calls.append(("first", (), {}))
        return self._first_result

    def delete(self):
        self.calls.append(("delete", (), {}))
        return self._delete_result


def build_db_with_query(mock_db: MagicMock, query_obj: QueryChain) -> MagicMock:
    mock_db.query.return_value = query_obj
    return mock_db


class DummyActivity(SimpleNamespace):
    pass


def make_activity(id=1, user_id=1, name="Run", start_time_str="2024-01-01T10:00:00"):
    # Stored model object (pre-serialization)
    start_dt = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
    return DummyActivity(
        id=id,
        user_id=user_id,
        name=name,
        start_time=start_dt,
        end_time=start_dt,
        hide_start_time=False,
        hide_location=False,
        hide_gear=False,
        private_notes="secret",
        city="X",
        town="Y",
        country="Z",
        gear_id=10,
        strava_gear_id="s1",
        garminconnect_gear_id="g1",
        activity_type=1,
        total_timer_time=100,
        distance=1000,
        calories=100,
        elevation_gain=10,
        pace=300,
        average_hr=140,
        is_hidden=False,
        strava_activity_id=None,
    )


# -----------------------------
# Tests: get_all_activities
# -----------------------------

def test_get_all_activities_returns_none_when_empty(mock_db, monkeypatch):
    q = QueryChain(all_result=[])
    build_db_with_query(mock_db, q)

    # ensure serialize_activity not called
    monkeypatch.setattr(activities_crud.activities_utils, "serialize_activity", MagicMock())

    result = activities_crud.get_all_activities(mock_db)
    assert result is None
    activities_crud.activities_utils.serialize_activity.assert_not_called()


def test_get_all_activities_serializes_each_and_returns_list(mock_db, monkeypatch):
    act1 = make_activity(id=1)
    act2 = make_activity(id=2)
    q = QueryChain(all_result=[act1, act2])
    build_db_with_query(mock_db, q)

    serialize_mock = MagicMock(side_effect=lambda a: a)
    monkeypatch.setattr(activities_crud.activities_utils, "serialize_activity", serialize_mock)

    result = activities_crud.get_all_activities(mock_db)
    assert result == [act1, act2]
    assert serialize_mock.call_count == 2


# -----------------------------
# Tests: get_user_activities
# -----------------------------

def test_get_user_activities_returns_none_when_empty(mock_db, monkeypatch):
    q = QueryChain(all_result=[])
    build_db_with_query(mock_db, q)

    monkeypatch.setattr(activities_crud.activities_utils, "serialize_activity", MagicMock())

    result = activities_crud.get_user_activities(user_id=1, db=mock_db)
    assert result is None


def test_get_user_activities_with_name_search_returns_serialized_list(mock_db, monkeypatch):
    act1 = make_activity(id=1, user_id=1, name="Morning Run")
    act2 = make_activity(id=2, user_id=1, name="Evening Run")
    q = QueryChain(all_result=[act1, act2])
    build_db_with_query(mock_db, q)

    serialize_mock = MagicMock(side_effect=lambda a: SimpleNamespace(id=a.id, name=a.name))
    monkeypatch.setattr(activities_crud.activities_utils, "serialize_activity", serialize_mock)

    result = activities_crud.get_user_activities(
        user_id=1,
        db=mock_db,
        name_search="Run",
    )
    assert isinstance(result, list)
    assert [r.id for r in result] == [1, 2]
    assert serialize_mock.call_count == 2


# -----------------------------
# Tests: get_distinct_activity_types_for_user
# -----------------------------

def test_get_distinct_activity_types_for_user_maps_ids_excluding_none(mock_db, monkeypatch):
    # distinct()...all() returns a list of single-tuple values as SQLAlchemy would
    q = QueryChain(all_result=[(1,), (2,), (None,), (3,)])
    build_db_with_query(mock_db, q)

    # Patch constant mapping in the module under test
    monkeypatch.setattr(activities_crud, "ACTIVITY_ID_TO_NAME", {1: "Run", 2: "Ride", 3: "Swim"})

    result = activities_crud.get_distinct_activity_types_for_user(user_id=99, db=mock_db)
    assert result == {1: "Run", 2: "Ride", 3: "Swim"}


# -----------------------------
# Tests: create_activity (async)
# -----------------------------
@pytest.mark.asyncio
async def test_create_activity_new_calls_notification_and_commits(mock_db, monkeypatch):
    # Prepare activity schema-like object
    activity_schema = SimpleNamespace(
        id=None,
        user_id=1,
        start_time="2024-01-01T10:00:00",
        is_hidden=False,
        created_at=None,
    )

    # No duplicate start time
    monkeypatch.setattr(activities_crud, "get_activity_by_start_time", MagicMock(return_value=None))

    # transform -> returns model with id/created_at
    model_obj = SimpleNamespace(id=123, created_at="2024-01-02T00:00:00")
    monkeypatch.setattr(
        activities_crud.activities_utils,
        "transform_schema_activity_to_model_activity",
        MagicMock(return_value=model_obj),
    )

    # Notifications
    notif_mod = activities_crud.notifications_utils
    new_notif_mock = AsyncMock()
    dup_notif_mock = AsyncMock()
    monkeypatch.setattr(notif_mod, "create_new_activity_notification", new_notif_mock)
    monkeypatch.setattr(notif_mod, "create_new_duplicate_start_time_activity_notification", dup_notif_mock)

    # AI insights
    ai_mock = MagicMock()
    monkeypatch.setattr(activities_crud.activity_ai_insights_utils, "get_activity_ai_insights", ai_mock)

    # Websocket manager dummy
    ws_mgr = SimpleNamespace()

    # DB behaviors
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = await activities_crud.create_activity(activity_schema, ws_mgr, mock_db, create_notification=True)

    # Assertions
    assert result is activity_schema
    assert activity_schema.id == 123
    assert activity_schema.created_at == "2024-01-02T00:00:00"
    assert activity_schema.is_hidden is False

    mock_db.add.assert_called_once_with(model_obj)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(model_obj)

    new_notif_mock.assert_awaited_once()
    dup_notif_mock.assert_not_called()
    ai_mock.assert_called_once()


@pytest.mark.asyncio
async def test_create_activity_duplicate_sets_hidden_and_sends_duplicate_notification(mock_db, monkeypatch):
    activity_schema = SimpleNamespace(
        id=None,
        user_id=1,
        start_time="2024-01-01T10:00:00",
        is_hidden=False,
        created_at=None,
    )

    # Duplicate exists
    monkeypatch.setattr(activities_crud, "get_activity_by_start_time", MagicMock(return_value=SimpleNamespace(id=1)))

    # transform -> returns model with id/created_at
    model_obj = SimpleNamespace(id=222, created_at="2024-01-03T00:00:00")
    monkeypatch.setattr(
        activities_crud.activities_utils,
        "transform_schema_activity_to_model_activity",  # Typo guard: ensure correct attribute name
        getattr(activities_crud.activities_utils, "transform_schema_activity_to_model_activity", MagicMock())
    )
    monkeypatch.setattr(
        activities_crud.activities_utils,
        "transform_schema_activity_to_model_activity",
        MagicMock(return_value=model_obj),
    )

    # Notifications
    notif_mod = activities_crud.notifications_utils
    new_notif_mock = AsyncMock()
    dup_notif_mock = AsyncMock()
    monkeypatch.setattr(notif_mod, "create_new_activity_notification", new_notif_mock)
    monkeypatch.setattr(notif_mod, "create_new_duplicate_start_time_activity_notification", dup_notif_mock)

    # AI insights
    ai_mock = MagicMock()
    monkeypatch.setattr(activities_crud.activity_ai_insights_utils, "get_activity_ai_insights", ai_mock)

    ws_mgr = SimpleNamespace()

    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = await activities_crud.create_activity(activity_schema, ws_mgr, mock_db, create_notification=True)

    assert result is activity_schema
    assert activity_schema.id == 222
    assert activity_schema.created_at == "2024-01-03T00:00:00"
    assert activity_schema.is_hidden is True

    mock_db.add.assert_called_once_with(model_obj)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(model_obj)

    new_notif_mock.assert_not_called()
    dup_notif_mock.assert_awaited_once()
    ai_mock.assert_called_once()


# -----------------------------
# Tests: delete_activity
# -----------------------------

def test_delete_activity_404_when_not_found(mock_db, monkeypatch):
    # get_activity_by_id -> None
    monkeypatch.setattr(activities_crud, "get_activity_by_id", MagicMock(return_value=None))

    with pytest.raises(activities_crud.HTTPException) as ex:
        activities_crud.delete_activity(activity_id=999, db=mock_db)
    assert ex.value.status_code == 404


def test_delete_activity_success_updates_stats_and_deletes(mock_db, monkeypatch):
    act = make_activity(id=10)
    monkeypatch.setattr(activities_crud, "get_activity_by_id", MagicMock(return_value=act))

    # stats update
    update_mock = MagicMock()
    monkeypatch.setattr(activities_crud.user_stats_crud, "update_stats_on_activity_delete", update_mock)

    # query().filter(...).delete()
    q = QueryChain(delete_result=1)
    build_db_with_query(mock_db, q)

    mock_db.commit = MagicMock()
    activities_crud.delete_activity(activity_id=10, db=mock_db)

    update_mock.assert_called_once_with(act, mock_db)
    # Ensure delete() was called in the chain
    assert any(c[0] == "delete" for c in q.calls)
    mock_db.commit.assert_called_once()


# -----------------------------
# Tests: get_activity_by_id_if_is_public
# -----------------------------

def test_get_activity_by_id_if_is_public_returns_none_when_disabled(mock_db, monkeypatch):
    settings = SimpleNamespace(public_shareable_links=False)
    monkeypatch.setattr(
        activities_crud.server_settings_utils,
        "get_server_settings_or_404",
        MagicMock(return_value=settings),
    )

    result = activities_crud.get_activity_by_id_if_is_public(activity_id=1, db=mock_db)
    assert result is None


def test_get_activity_by_id_if_is_public_enabled_and_found_strips_private_fields(mock_db, monkeypatch):
    settings = SimpleNamespace(public_shareable_links=True)
    monkeypatch.setattr(
        activities_crud.server_settings_utils,
        "get_server_settings_or_404",
        MagicMock(return_value=settings),
    )

    act = make_activity(id=1, user_id=1)

    # query().filter(...).first() -> act
    q = QueryChain(first_result=act)
    build_db_with_query(mock_db, q)

    # serialize returns same object for simplicity
    serialize_mock = MagicMock(side_effect=lambda a: a)
    monkeypatch.setattr(activities_crud.activities_utils, "serialize_activity", serialize_mock)

    result = activities_crud.get_activity_by_id_if_is_public(activity_id=1, db=mock_db)

    assert result is act
    assert result.private_notes is None
    if hasattr(result, "hide_start_time") and result.hide_start_time:
        assert result.start_time is None and result.end_time is None
    if hasattr(result, "hide_location") and result.hide_location:
        assert result.city is None and result.town is None and result.country is None
    if hasattr(result, "hide_gear") and result.hide_gear:
        assert (
            result.gear_id is None
            and result.strava_gear_id is None
            and result.garminconnect_gear_id is None
        )
    serialize_mock.assert_called_once_with(act)
