import json
import unittest
from pathlib import Path
from xml.etree.ElementTree import ParseError

from db import Database
from processing import load_json
from xml.etree import ElementTree as ET


def drop_data():
    db = Database()
    with db:
        db.execute_query('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')

def is_valid_json(myjson:str) -> bool:
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

def is_valid_xml(myxml:str) -> bool:
    try:
        ET.fromstring(myxml)
    except ParseError:
        return False
    return True

def load_xml(file_path: str):
    if Path(file_path).exists():
        with open(file_path, 'r') as file:
            data = file.read()
            return data
    raise FileNotFoundError


TEST_CONNECTION_QUERY = 'SELECT 1'
TEST_TABLES_EXISTENCE_QUERY = """
    SELECT 
        EXISTS (SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'students' AND table_schema = 'public') AS table1_exists,
        EXISTS (SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'rooms' AND table_schema = 'public') AS table2_exists
"""
TEST_INDEX_EXISTENCE_QUERY = """
    SELECT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE schemaname = 'public'
        AND indexname = 'students_birthday'
    )
"""
TEST_ROOM_COUNT_QUERY = """
    SELECT COUNT(*)
    FROM rooms
"""
TEST_STUDENT_COUNT_QUERY = """
    SELECT COUNT(*)
    FROM students
"""
TEST_DATA_RETRIEVAL = """
    SELECT 
        r.id, 
        r.name,
        COUNT(s.id) as students_count
    FROM rooms r
    LEFT JOIN students s 
    ON s.room = r.id
    GROUP BY r.id
    ORDER BY r.id
    LIMIT 5
"""

AWAITED_ROOM_COUNT = 1000
AWAITED_STUDENT_COUNT = 10000


class TestDatabase(unittest.TestCase):
    def test_database_connection(self):
        db = Database()
        with db:
            response = db.execute_query(TEST_CONNECTION_QUERY)
            self.assertEqual(response[0][0], 1)

    def test_tables_initialization(self):
        db = Database()
        with db:
            table_existence = db.execute_query(TEST_TABLES_EXISTENCE_QUERY)[0]
            self.assertEqual(table_existence[0], True, 'students table does not exist')
            self.assertEqual(table_existence[1], True, 'rooms table does not exist')

            index_existence = db.execute_query(TEST_INDEX_EXISTENCE_QUERY)[0][0]
            self.assertEqual(index_existence, True, 'index on students.birthday column was not created')

    def test_data_insertion(self):
        db = Database()
        with db:
            rooms_data = load_json('sample-data/rooms.json')
            students_data = load_json('sample-data/students.json')
            db.insert_rooms(rooms_data)
            db.insert_students(students_data)
            room_count = db.execute_query(TEST_ROOM_COUNT_QUERY)[0][0]
            student_count = db.execute_query(TEST_STUDENT_COUNT_QUERY)[0][0]
            self.assertEqual(room_count, AWAITED_ROOM_COUNT, 'rooms table was not filled properly')
            self.assertEqual(student_count, AWAITED_STUDENT_COUNT, 'students table was not filled properly')

    def test_xml_retrieval(self):
        db = Database()
        with db:
            data = db.get_xml(TEST_DATA_RETRIEVAL)
            self.assertEqual(is_valid_xml(data), True, 'output is not a valid XML')
            test_data = load_xml('test-data/test.xml')
            self.assertEqual(data, test_data, 'output xml doesn\'t match the test xml data')

    def test_json_retrieval(self):
        db = Database()
        with db:
            result = db.get_json(TEST_DATA_RETRIEVAL)
            self.assertEqual(is_valid_json(result), True, 'output is not a valid JSON')
            data_str = json.dumps(json.loads(result))
            test_data = load_json('test-data/test.json').replace('\n', ' ')
            self.assertEqual(data_str, test_data, 'output json doesn\'t match the test json data')

    @classmethod
    def tearDownClass(cls):
        drop_data()



if __name__ == '__main__':
    unittest.main()

