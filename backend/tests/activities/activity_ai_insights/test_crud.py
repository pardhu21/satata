from types import SimpleNamespace
from importlib import import_module
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException


activity_ai_insights_crud = import_module("activities.activity_ai_insights.crud")


class QueryChain:
    """
    Minimal helper to simulate SQLAlchemy query chains used in the CRUD module.
    Supports: .filter(...).order_by(...).all() / .first()
    """

    def __init__(self, *, all_result=None, first_result=None):
        self._all_result = all_result
        self._first_result = first_result
        self._filters = []
        self._ordered = False

    def filter(self, *args, **kwargs):
        self._filters.append((args, kwargs))
        return self

    def order_by(self, *args, **kwargs):
        self._ordered = True
        return self

    def all(self):
        return self._all_result

    def first(self):
        return self._first_result


@pytest.fixture(autouse=True)
def silence_logger(monkeypatch):
    # Silence logger during tests and allow asserting it was called on error paths
    if hasattr(activity_ai_insights_crud, "core_logger") and hasattr(activity_ai_insights_crud.core_logger, "print_to_log"):
        monkeypatch.setattr(activity_ai_insights_crud.core_logger, "print_to_log", lambda *a, **k: None)
    yield


# --------------------
# get_all_insights
# --------------------

def test_get_all_insights_returns_list(monkeypatch):
    # Arrange
    insights = [MagicMock(), MagicMock()]
    db = MagicMock()
    db.query.return_value = QueryChain(all_result=insights)

    # Act
    result = activity_ai_insights_crud.get_all_insights(db)

    # Assert
    assert result == insights
    db.query.assert_called_once()


def test_get_all_insights_returns_none_when_empty(monkeypatch):
    # Arrange
    db = MagicMock()
    db.query.return_value = QueryChain(all_result=[])

    # Act
    result = activity_ai_insights_crud.get_all_insights(db)

    # Assert
    assert result is None


def test_get_all_insights_raises_http_500_on_exception(monkeypatch):
    # Arrange
    db = MagicMock()
    db.query.side_effect = Exception("boom")
    log_calls = []

    def fake_log(*a, **k):
        log_calls.append((a, k))

    monkeypatch.setattr(activity_ai_insights_crud.core_logger, "print_to_log", fake_log, raising=False)

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crud.get_all_insights(db)
    assert exc.value.status_code == 500
    assert log_calls  # ensure we logged


# --------------------
# get_insights_for_activity
# --------------------

def test_get_insights_for_activity_returns_none_if_activity_missing(monkeypatch):
    # Arrange
    db = MagicMock()
    monkeypatch.setattr(
        activity_ai_insights_crud.activity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: None,
        raising=False,
    )

    # Act
    result = activity_ai_insights_crud.get_insights_for_activity(1, 10, db)

    # Assert
    assert result is None
    db.query.assert_not_called()


def test_get_insights_for_activity_returns_latest_insight(monkeypatch):
    # Arrange
    activity = SimpleNamespace(id=1, user_id=10)
    latest = SimpleNamespace(id=99, activity_id=1, insight_text="latest")

    db = MagicMock()
    db.query.return_value = QueryChain(first_result=latest)

    monkeypatch.setattr(
        activity_ai_insights_crud.activity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: activity,
        raising=False,
    )

    # Act
    result = activity_ai_insights_crud.get_insights_for_activity(1, 10, db)

    # Assert
    assert result is latest


def test_get_insights_for_activity_returns_none_when_no_insights(monkeypatch):
    # Arrange
    activity = SimpleNamespace(id=1, user_id=10)
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=None)

    monkeypatch.setattr(
        activity_ai_insights_crud.activity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: activity,
        raising=False,
    )

    # Act
    result = activity_ai_insights_crud.get_insights_for_activity(1, 10, db)

    # Assert
    assert result is None


def test_get_insights_for_activity_http_500_on_exception(monkeypatch):
    # Arrange
    activity = SimpleNamespace(id=1, user_id=10)
    db = MagicMock()
    db.query.side_effect = Exception("db fail")

    log_calls = []

    def fake_log(*a, **k):
        log_calls.append((a, k))

    monkeypatch.setattr(
        activity_ai_insights_crud.activity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: activity,
        raising=False,
    )
    monkeypatch.setattr(activity_ai_insights_crud.core_logger, "print_to_log", fake_log, raising=False)

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crud.get_insights_for_activity(1, 10, db)
    assert exc.value.status_code == 500
    assert log_calls


# --------------------
# get_insight_by_id
# --------------------

def test_get_insight_by_id_returns_object(monkeypatch):
    # Arrange
    insight = SimpleNamespace(id=1)
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight)

    # Act
    result = activity_ai_insights_crud.get_insight_by_id(1, db)

    # Assert
    assert result is insight


def test_get_insight_by_id_returns_none_when_missing(monkeypatch):
    # Arrange
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=None)

    # Act
    result = activity_ai_insights_crud.get_insight_by_id(1, db)

    # Assert
    assert result is None


def test_get_insight_by_id_http_500_on_exception(monkeypatch):
    # Arrange
    db = MagicMock()
    db.query.side_effect = Exception("err")
    log_calls = []

    def fake_log(*a, **k):
        log_calls.append((a, k))

    monkeypatch.setattr(activity_ai_insights_crud.core_logger, "print_to_log", fake_log, raising=False)

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crud.get_insight_by_id(1, db)
    assert exc.value.status_code == 500
    assert log_calls


# --------------------
# create_insight
# --------------------

def test_create_insight_happy_path(monkeypatch):
    # Arrange
    created_instances = []

    class FakeInsight:
        def __init__(self, activity_id, insight_text, model_used):
            self.activity_id = activity_id
            self.insight_text = insight_text
            self.model_used = model_used
            created_instances.append(self)

    monkeypatch.setattr(activity_ai_insights_crud.models, "ActivityAIInsights", FakeInsight)

    db = MagicMock()
    schema_obj = SimpleNamespace(activity_id=1, insight_text="hello", model_used="gpt")

    # Act
    result = activity_ai_insights_crud.create_insight(schema_obj, db)

    # Assert
    assert isinstance(result, FakeInsight)
    assert result.activity_id == 1
    assert result.insight_text == "hello"
    assert result.model_used == "gpt"
    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_create_insight_rollback_on_commit_failure(monkeypatch):
    # Arrange
    class FakeInsight:
        def __init__(self, activity_id, insight_text, model_used):
            self.activity_id = activity_id
            self.insight_text = insight_text
            self.model_used = model_used

    monkeypatch.setattr(activity_ai_insights_crud.models, "ActivityAIInsights", FakeInsight)

    db = MagicMock()
    db.commit.side_effect = Exception("commit failed")

    log_calls = []

    def fake_log(*a, **k):
        log_calls.append((a, k))

    monkeypatch.setattr(activity_ai_insights_crud.core_logger, "print_to_log", fake_log, raising=False)

    schema_obj = SimpleNamespace(activity_id=1, insight_text="hi", model_used="gpt")

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crud.create_insight(schema_obj, db)
    assert exc.value.status_code == 500
    db.rollback.assert_called_once()
    db.refresh.assert_not_called()
    assert log_calls


# --------------------
# edit_insight
# --------------------

def test_edit_insight_404_when_not_found(monkeypatch):
    # Arrange
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=None)

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crud.edit_insight(1, SimpleNamespace(), 10, db)
    assert exc.value.status_code == 404
    db.commit.assert_not_called()


def test_edit_insight_404_when_parent_activity_missing(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20, insight_text="a", model_used="m")
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)

    monkeypatch.setattr(
        activity_ai_insights_crud.activity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: None,
        raising=False,
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crud.edit_insight(1, SimpleNamespace(insight_text="b"), 10, db)
    assert exc.value.status_code == 404
    db.commit.assert_not_called()


def test_edit_insight_403_when_user_mismatch(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20, insight_text="a", model_used="m")
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)

    monkeypatch.setattr(
        activity_ai_insights_crud.activity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: SimpleNamespace(user_id=999),
        raising=False,
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crud.edit_insight(1, SimpleNamespace(insight_text="b"), 10, db)
    assert exc.value.status_code == 403
    db.commit.assert_not_called()


def test_edit_insight_success_updates_and_commits(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20, insight_text="old", model_used="oldm")
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)

    monkeypatch.setattr(
        activity_ai_insights_crud.activity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: SimpleNamespace(user_id=10),
        raising=False,
    )

    edit_obj = SimpleNamespace(insight_text="new text", model_used="new-model")

    # Act
    result = crud.edit_insight(1, edit_obj, 10, db)

    # Assert
    assert result is insight_obj
    assert insight_obj.insight_text == "new text"
    assert insight_obj.model_used == "new-model"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(insight_obj)


def test_edit_insight_rollback_on_generic_exception(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20, insight_text="old", model_used="oldm")
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)
    db.commit.side_effect = Exception("db error")

    monkeypatch.setattr(
        activity_ai_insights_crudactivity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: SimpleNamespace(user_id=10),
        raising=False,
    )

    log_calls = []

    def fake_log(*a, **k):
        log_calls.append((a, k))

    monkeypatch.setattr(activity_ai_insights_crudcore_logger, "print_to_log", fake_log, raising=False)

    edit_obj = SimpleNamespace(insight_text="x", model_used="y")

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_crudedit_insight(1, edit_obj, 10, db)
    assert exc.value.status_code == 500
    db.rollback.assert_called_once()
    assert log_calls


# --------------------
# delete_insight
# --------------------

def test_delete_insight_404_when_not_found(monkeypatch):
    # Arrange
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=None)

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_cruddelete_insight(1, 10, db)
    assert exc.value.status_code == 404
    db.commit.assert_not_called()


def test_delete_insight_404_when_parent_activity_missing(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20)
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)

    monkeypatch.setattr(
        activity_ai_insights_crudactivity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: None,
        raising=False,
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_cruddelete_insight(1, 10, db)
    assert exc.value.status_code == 404
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_delete_insight_403_when_user_mismatch(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20)
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)

    monkeypatch.setattr(
        activity_ai_insights_crudactivity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: SimpleNamespace(user_id=999),
        raising=False,
    )

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_cruddelete_insight(1, 10, db)
    assert exc.value.status_code == 403
    db.delete.assert_not_called()
    db.commit.assert_not_called()


def test_delete_insight_success_deletes_and_commits(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20)
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)

    monkeypatch.setattr(
        activity_ai_insights_crudactivity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: SimpleNamespace(user_id=10),
        raising=False,
    )

    # Act
    activity_ai_insights_cruddelete_insight(1, 10, db)

    # Assert
    db.delete.assert_called_once_with(insight_obj)
    db.commit.assert_called_once()


def test_delete_insight_rollback_on_exception(monkeypatch):
    # Arrange
    insight_obj = SimpleNamespace(id=1, activity_id=20)
    db = MagicMock()
    db.query.return_value = QueryChain(first_result=insight_obj)
    db.commit.side_effect = Exception("commit failed")

    monkeypatch.setattr(
        activity_ai_insights_crudactivity_crud,
        "get_activity_by_id_from_user_id",
        lambda activity_id, token_user_id, db: SimpleNamespace(user_id=10),
        raising=False,
    )

    log_calls = []

    def fake_log(*a, **k):
        log_calls.append((a, k))

    monkeypatch.setattr(activity_ai_insights_crudcore_logger, "print_to_log", fake_log, raising=False)

    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        activity_ai_insights_cruddelete_insight(1, 10, db)
    assert exc.value.status_code == 500
    db.rollback.assert_called_once()
    assert log_calls
