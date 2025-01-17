import unittest
from db import Database


def drop_data():
    db = Database()
    with db:
        db.execute_query('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')


class TestDatabase(unittest.TestCase):
    def test_database_connection(self):
        db = Database()
        with db:
            response = db.execute_query('SELECT 1')
            self.assertEqual(response[0][0], 1)

    def test_create_tables(self):
        db = Database()
        with db:
            db.create_tables()
            table_existence = db.execute_query("""
            SELECT 
                EXISTS (SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'students' AND table_schema = 'public') AS table1_exists,
                EXISTS (SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'rooms' AND table_schema = 'public') AS table2_exists
            """)[0]
            self.assertEqual(table_existence[0], True)
            self.assertEqual(table_existence[1], True)
            drop_data()


if __name__ == '__main__':
    unittest.main()
