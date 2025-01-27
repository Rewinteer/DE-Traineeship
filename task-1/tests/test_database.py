import unittest
import psycopg2
import config
from db import Database
from unittest.mock import patch, MagicMock


def get_mocked_conn_and_cursor(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn, mock_cursor


class TestDatabase(unittest.TestCase):
    @patch("db.psycopg2.connect")
    def test_enter_exit(self, mock_connect):
        mock_conn, mock_cursor = get_mocked_conn_and_cursor(mock_connect)

        with Database() as db:
            pass

        mock_connect.assert_called_once_with(
            dbname=config.dbname,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
        )

        mock_cursor.execute.assert_any_call(
            db._Database__create_rooms_table_query, None
        )
        mock_cursor.execute.assert_any_call(
            db._Database__create_students_table_query, None
        )
        mock_cursor.execute.assert_any_call(
            db._Database__create_students_birthday_index_query, None
        )

        mock_conn.close.assert_called_once()

    @patch("db.psycopg2.connect")
    def test_execute_query_success(self, mock_connect):
        mock_conn, mock_cursor = get_mocked_conn_and_cursor(mock_connect)
        mock_cursor.fetchall.return_value = [("result",)]

        with Database() as db:
            mock_conn.reset_mock()
            mock_cursor.reset_mock()
            result = db.execute_query("SELECT * FROM students;")

        # Verify query execution
        mock_cursor.execute.assert_called_once_with("SELECT * FROM students;", None)
        self.assertEqual(result, [("result",)])
        mock_conn.commit.assert_called_once()

    @patch("db.psycopg2.connect")
    def test_execute_query_exception(self, mock_connect):
        mock_conn, mock_cursor = get_mocked_conn_and_cursor(mock_connect)
        mock_cursor.execute.side_effect = psycopg2.errors.UniqueViolation

        with Database() as db:
            mock_conn.reset_mock()
            mock_cursor.reset_mock()
            db.execute_query("INSERT INTO some_table VALUES (1);")

        mock_conn.rollback.assert_called_once()

    @patch("db.psycopg2.connect")
    def test_get_json(self, mock_connect):
        mock_conn, mock_cursor = get_mocked_conn_and_cursor(mock_connect)
        mock_cursor.fetchall.return_value = [[{"id": 1, "name": "Room A"}]]

        with Database() as db:
            mock_conn.reset_mock()
            mock_cursor.reset_mock()
            result = db.get_json("SELECT * FROM rooms")

        # Verify query transformation and execution
        mock_cursor.execute.assert_called_once_with(
            "WITH t AS (SELECT * FROM rooms) SELECT json_agg(t) from t;", None
        )
        self.assertEqual(result, '{"id": 1, "name": "Room A"}')

    @patch("db.psycopg2.connect")
    def test_get_xml(self, mock_connect):
        mock_conn, mock_cursor = get_mocked_conn_and_cursor(mock_connect)
        mock_cursor.fetchall.return_value = [("<xml>mocked_xml_data</xml>",)]

        with Database() as db:
            mock_conn.reset_mock()
            mock_cursor.reset_mock()
            result = db.get_xml("SELECT * FROM rooms")

        # Verify query transformation and execution
        mock_cursor.execute.assert_called_once_with(
            "SELECT query_to_xml('SELECT * FROM rooms', true, false, '');", None
        )
        self.assertEqual(result, "<xml>mocked_xml_data</xml>")


if __name__ == "__main__":
    unittest.main()
