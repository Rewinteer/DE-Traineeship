import argparse
import json
import os.path

from db import Database
from logger import logger
from pathlib import Path


STUDENTS_DEFAULT_PATH = "sample-data/students.json"
ROOMS_DEFAULT_PATH = "sample-data/rooms.json"
OUTPUT_DEFAULT_FORMAT = "json"
OUTPUT_PATH = "export/"

# Task-specific queries
SELECT_ROOMS_WITH_STUDENT_COUNT = """
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
SELECT_ROOMS_WITH_LOWEST_AVG_AGE = """
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
SELECT_ROOMS_WITH_HIGHEST_AGE_DIFF = """
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
SELECT_ROOMS_WITH_DIFFERENT_GENDERS = """
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


def parse_cli_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-students",
        type=str,
        default=STUDENTS_DEFAULT_PATH,
        help=f"path to the students.json file. Default - {STUDENTS_DEFAULT_PATH}",
    )
    arg_parser.add_argument(
        "-rooms",
        type=str,
        default=ROOMS_DEFAULT_PATH,
        help=f"path to the rooms.json file. Default - {ROOMS_DEFAULT_PATH}",
    )
    arg_parser.add_argument(
        "-format",
        type=str,
        default=OUTPUT_DEFAULT_FORMAT,
        help=f"output format for the query result. Default - {OUTPUT_DEFAULT_FORMAT}",
    )
    arg_parser.add_argument(
        "-query", type=str, help="Query to execute. Could be omitted"
    )
    args = arg_parser.parse_args()
    logger.info(f"Passed CLI args - {args}")
    return args


def load_json(file_path: str) -> str:
    if Path(file_path).exists():
        data = json.loads(Path(file_path).read_text())
        logger.info(f"loaded json data from {file_path}")
        return json.dumps(data)
    raise FileNotFoundError


def save_data(serialized_data: str, file_name: str) -> None:
    new_filepath = os.path.join(OUTPUT_PATH, file_name)
    logger.info(f"saved {file_name} at {new_filepath}")
    with open(new_filepath, "w") as f:
        f.write(serialized_data)


if __name__ == "__main__":
    cli_args = parse_cli_args()
    students_data = load_json(cli_args.students)
    rooms_data = load_json(cli_args.rooms)
    output_format = cli_args.format
    db = Database()

    with db:
        # data insertion
        db.insert_rooms(rooms_data)
        db.insert_students(students_data)

        # data retrieval

        # user-defined query execution
        if cli_args.query:
            if cli_args.format.lower() == "xml":
                result = db.get_xml(cli_args.query)
                if result:
                    save_data(result, "output.xml")
            else:
                result = db.get_json(cli_args.query)
                if result:
                    save_data(result, "output.json")
        # pre-defined task queries processing
        else:
            if cli_args.format.lower() == "xml":
                save_data(
                    db.get_xml(SELECT_ROOMS_WITH_STUDENT_COUNT),
                    "rooms_with_students_count.xml",
                )
                save_data(
                    db.get_xml(SELECT_ROOMS_WITH_LOWEST_AVG_AGE),
                    "rooms_with_lowest_avg_age.xml",
                )
                save_data(
                    db.get_xml(SELECT_ROOMS_WITH_HIGHEST_AGE_DIFF),
                    "rooms_with_highest_age_diff.xml",
                )
                save_data(
                    db.get_xml(SELECT_ROOMS_WITH_DIFFERENT_GENDERS),
                    "rooms_with_different_genders.xml",
                )
            else:
                save_data(
                    db.get_json(SELECT_ROOMS_WITH_STUDENT_COUNT),
                    f"rooms_with_students_count.{OUTPUT_DEFAULT_FORMAT}",
                )
                save_data(
                    db.get_json(SELECT_ROOMS_WITH_LOWEST_AVG_AGE),
                    f"rooms_with_lowest_avg_age.{OUTPUT_DEFAULT_FORMAT}",
                )
                save_data(
                    db.get_json(SELECT_ROOMS_WITH_HIGHEST_AGE_DIFF),
                    f"rooms_with_highest_age_diff.{OUTPUT_DEFAULT_FORMAT}",
                )
                save_data(
                    db.get_json(SELECT_ROOMS_WITH_DIFFERENT_GENDERS),
                    f"rooms_with_different_genders.{OUTPUT_DEFAULT_FORMAT}",
                )
        db.drop_data()
