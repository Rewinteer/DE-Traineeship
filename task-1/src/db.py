import json
import os
import psycopg2


class Database:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, data=None):
        with self.conn.cursor() as cur:
            try:
                cur.execute(query, data)
                if cur.description:
                    result = cur.fetchall()
                else:
                    result = None
                self.conn.commit()
                return result
            # already exists
            except (psycopg2.errors.UniqueViolation, psycopg2.errors.DuplicateTable):
                self.conn.rollback()


class DatabaseQueries(Database):
    def __init__(self):
        super().__init__()
        self._insert_students_query = """
            INSERT INTO students
            SELECT * FROM json_populate_recordset(NULL::students, %s)
        """
        self._insert_rooms_query = """
            INSERT INTO rooms
            SELECT * FROM json_populate_recordset(NULL::rooms, %s)
        """
        # pre-defined queries specified in the task
        self.select_rooms_with_students_count = """
            SELECT 
	            r.id, 
                r.name,
                COUNT(s.id) as students_count
            FROM rooms r
            LEFT JOIN students s 
            ON s.room = r.id
            GROUP BY r.id
            ORDER BY r.id
        """
        self.select_rooms_with_lowest_avg_age = """
            SELECT 
                r.id,
                r.name,
                AVG(CURRENT_DATE - s.birthday) as avg_age_in_days
            FROM 
                rooms r
            LEFT JOIN students s
            ON r.id = s.room 
            GROUP BY r.id
            ORDER BY avg_age_in_days
            limit 5
        """
        self.select_rooms_with_highest_age_diff = """
            SELECT 
                r.id,
                r.name,
                MAX(CURRENT_DATE - s.birthday) - MIN(CURRENT_DATE - s.birthday) as age_diff_in_days
            FROM 
                rooms r
            JOIN students s
            ON r.id = s.room 
            GROUP BY r.id
            ORDER BY age_diff_in_days DESC
            LIMIT 5
        """
        self.select_rooms_with_different_genders = """
            SELECT 
                r.id,
                r.name,
                COUNT(DISTINCT(s.sex )) AS sex_count
            FROM 
                rooms r
            JOIN students s
            ON r.id = s.room
            GROUP BY r.id
            HAVING COUNT(DISTINCT(s.sex )) > 1
        """

    def insert_students(self, students_data):
        self.execute_query(self._insert_students_query, (students_data,))

    def insert_rooms(self, rooms_data):
        self.execute_query(self._insert_rooms_query, (rooms_data,))

    def get_json(self, query):
        upd_query = f'WITH t AS ({query}) SELECT json_agg(t) from t;'
        result = self.execute_query(upd_query)
        return json.dumps(result[0][0])

    def get_xml(self, query):
        upd_query = f"SELECT query_to_xml('{query}', true, false, '');"
        result = self.execute_query(upd_query)
        return result[0][0]
