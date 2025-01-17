import json
import os
import psycopg2


# queries for filling the tables
INSERT_STUDENTS_QUERY = """
    INSERT INTO students
    SELECT * FROM json_populate_recordset(NULL::students, %s)
"""
INSERT_ROOMS_QUERY = """
    INSERT INTO rooms
    SELECT * FROM json_populate_recordset(NULL::rooms, %s)
"""


class Database:
    def __init__(self):
        self.conn = None
        # database initialization queries
        self.__create_rooms_table_query = """
            CREATE TABLE IF NOT EXISTS public.rooms (
                id serial4 NOT NULL,
                "name" varchar NOT NULL,
                CONSTRAINT rooms_pkey PRIMARY KEY (id)
            )
        """
        self.__create_students_table_query = """
            CREATE TABLE IF NOT EXISTS public.students (
                id serial4 NOT NULL,
                "name" varchar NOT NULL,
                birthday date NOT NULL,
                room int4 NOT NULL,
                sex varchar(1) NOT NULL,
                CONSTRAINT students_pkey PRIMARY KEY (id),
                CONSTRAINT students_sex_check CHECK ((((sex)::text = 'F'::text) OR ((sex)::text = 'M'::text))),
                CONSTRAINT students_room_fkey FOREIGN KEY (room) REFERENCES public.rooms(id)
            )
        """
        self.__create_students_birthday_index_query = """
            CREATE INDEX IF NOT EXISTS students_birthday ON public.students USING btree (birthday)
        """

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

    def execute_query(self, query: str, data=None) -> str | None:
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

    def create_tables(self) -> None:
        self.execute_query(self.__create_rooms_table_query)
        self.execute_query(self.__create_students_table_query)

    def add_birthday_index(self) -> None:
        self.execute_query(self.__create_students_birthday_index_query)

    def insert_students(self, students_data: str) -> None:
        self.execute_query(INSERT_STUDENTS_QUERY, (students_data,))

    def insert_rooms(self, rooms_data: str) -> None:
        self.execute_query(INSERT_ROOMS_QUERY, (rooms_data,))

    def get_json(self, query: str) -> str:
        upd_query = f'WITH t AS ({query}) SELECT json_agg(t) from t;'
        result = self.execute_query(upd_query)
        return json.dumps(result[0][0])

    def get_xml(self, query: str) -> str:
        upd_query = f"SELECT query_to_xml('{query}', true, false, '');"
        result = self.execute_query(upd_query)
        return result[0][0]
