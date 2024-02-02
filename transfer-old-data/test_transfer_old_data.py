"""Unit tests for the ecs_load_to_s3.py script."""

from unittest.mock import MagicMock

from transfer_old_data import extract_old_data_from_database, delete_data_from_db


def test_extract_old_data_from_database_execute():
    """Tests that execute gets called in the function."""

    mock_conn = MagicMock()
    mock_execute = mock_conn.execute

    extract_old_data_from_database(mock_conn)

    assert mock_execute.call_count == 2


def test_extract_old_data_from_database_fetchall():
    """Tests that fetchall gets called within the function."""

    mock_conn = MagicMock()
    mock_fetchall = mock_conn.execute().fetchall

    extract_old_data_from_database(mock_conn)

    assert mock_fetchall.call_count == 1


def test_delete_data_from_db():
    """Tests that execute is called within this function."""

    mock_conn = MagicMock()

    mock_execute = mock_conn.execute

    delete_data_from_db(mock_conn)

    assert mock_execute.call_count == 2
