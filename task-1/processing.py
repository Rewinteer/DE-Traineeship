import argparse
import json
import os.path

from db import DatabaseQueries
from pathlib import Path


STUDENTS_DEFAULT_PATH = 'sample-data/students.json'
ROOMS_DEFAULT_PATH = 'sample-data/rooms.json'
OUTPUT_DEFAULT_FORMAT = 'json'
OUTPUT_PATH = 'export/'


def parse_cli_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-students', type=str, default=STUDENTS_DEFAULT_PATH)
    arg_parser.add_argument('-rooms', type=str, default=ROOMS_DEFAULT_PATH)
    arg_parser.add_argument('-format', type=str, default=OUTPUT_DEFAULT_FORMAT)
    arg_parser.add_argument('-query', type=str)
    args = arg_parser.parse_args()
    return args


def load_json(file_path):
    if Path(file_path).exists():
        data = json.loads(Path(file_path).read_text())
        return json.dumps(data)


def save_data(serialized_data: str, file_name: str):
    new_filepath = os.path.join(OUTPUT_PATH, file_name)
    with open(new_filepath, 'w') as f:
        f.write(serialized_data)


if __name__ == '__main__':
    cli_args = parse_cli_args()
    students_data = load_json(cli_args.students)
    rooms_data = load_json(cli_args.rooms)
    output_format = cli_args.format
    db = DatabaseQueries()

    with db:
        # Data initialization

        # filling the tables
        db.insert_rooms(rooms_data)
        db.insert_students(students_data)

        # applying indexes to most commonly used columns based on the requirements
        db.execute_query(
            'CREATE INDEX students_birthday ON students (birthday);'
            # bitmap index could be applied to the sex column
            # but PostgreSQL does not provide the persistent one
        )

        # data retrieval

        # user-defined query execution
        if cli_args.query:
            if cli_args.format.lower() == 'xml':
                result = db.get_xml(cli_args.query)
                if result:
                    save_data(result, 'output.xml')
            else:
                result = db.get_json(cli_args.query)
                if result:
                    save_data(result, 'output.json')
        # pre-defined task queries processing
        else:
            if cli_args.format.lower() == 'xml':
                save_data(db.get_xml(db.select_rooms_with_students_count), 'rooms_with_students_count.xml')
                save_data(db.get_xml(db.select_rooms_with_lowest_avg_age), 'rooms_with_lowest_avg_age.xml')
                save_data(db.get_xml(db.select_rooms_with_highest_age_diff), 'rooms_with_highest_age_diff.xml')
                save_data(db.get_xml(db.select_rooms_with_different_genders), 'rooms_with_different_genders.xml')
            else:
                save_data(db.get_json(db.select_rooms_with_students_count), f'rooms_with_students_count.{OUTPUT_DEFAULT_FORMAT}')
                save_data(db.get_json(db.select_rooms_with_lowest_avg_age), f'rooms_with_lowest_avg_age.{OUTPUT_DEFAULT_FORMAT}')
                save_data(db.get_json(db.select_rooms_with_highest_age_diff), f'rooms_with_highest_age_diff.{OUTPUT_DEFAULT_FORMAT}')
                save_data(db.get_json(db.select_rooms_with_different_genders), f'rooms_with_different_genders.{OUTPUT_DEFAULT_FORMAT}')



