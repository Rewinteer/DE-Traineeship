# Task-1

This code is designed to run a script (`processing.py`) that connects to a PostgreSQL database, creates rooms and students tables fills it with given JSON data and queries the database either using pre-defined queries or user-defined queries passed as CLI arguments.

## Prerequisites

Before running the project, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Environment Setup

1. This project requires some environment variables to connect to the PostgreSQL database. You have to define them in the `.env` file, which should be located in the root of the project directory.

Example `.env` file:
```env
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

2. You need to copy/download the docker-compose.yml file from this repository.

### Running the Application
1. Step 1: Build the Containers
To build the containers, use the following command in the directory where the docker-compose file is located:
`docker-compose up --build`. This will create a database and execute pre-defined queries, which output will be exported in JSON format.
2. Step 2: Run the Application with the custom CLI args:

| Argument  |                   Description                    |               Default Value |
|-----------|:------------------------------------------------:|--------------------:|
| -students |         Path to the students.json file.          | "sample-data/students.json" |
| -rooms    |           Path to the rooms.json file            |    "sample-data/rooms.json" |
| -format   | Output format for the query result (json or xml) |                        json |
| -query    |                     Query to execute.                     |       None          |

Example:
`docker-compose run app \
    -students "/usr/src/app/sample-data/students.json" \
    -rooms "/usr/src/app/sample-data/rooms.json" \
    -query "SELECT * FROM students LIMIT 5" \
    -format "xml"`
