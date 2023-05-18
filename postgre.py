#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import psycopg2
import sys
import typing as t
from pathlib import Path
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def connect(name_db: str):
    conn = psycopg2.connect(
        user="postgres",
        password="hehehaha",
        host="127.0.0.1",
        port="5432",
        database=name_db
    )
    return conn


def add_st(name: str, group: str, lmarks: str, db_name: str) -> None:
    """
    Ввести данные студента в базу данных
    """

    conn = connect(db_name)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO marks (marks_list) 
        VALUES (%s)
        """,
        (lmarks, )
    )

    cursor.execute(
        """
        INSERT INTO students (student_name, student_group)
        VALUES (%s, %s)
        """,
        (name, group)
    )
    conn.commit()
    conn.close()


def create_db(name_db: str) -> None:
    """
    Создать базу данных.
    """

    conn = connect(name_db)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS marks 
        (mark_id serial PRIMARY KEY,
        marks_list TEXT NOT NULL);''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS students 
        (student_id serial PRIMARY KEY,
        student_name TEXT NOT NULL,
        student_group TEXT NOT NULL,
        mark_id serial REFERENCES marks);''')

    conn.commit()
    conn.close()


def show(staff: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Вывод записей базы данных
    """
    if staff:
        line = "+-{}-+-{}-+-{}-+-{}-+".format("-" * 4, "-" * 30, "-" * 20, "-" * 15)
        print(line)
        print(
            "| {:^4} | {:^30} | {:^20} | {:^15} |".format(
                "№", "Ф.И.О.", "Группа", "Успеваемость"
            )
        )
        print(line)

        for idx, student in enumerate(staff, 1):
            lmarks = student.get("marks", "")
            print(
                "| {:>4} | {:<30} | {:<20} | {:>15} |".format(
                    idx,
                    student.get("name", ""),
                    student.get("group", ""),
                    " ".join(map(str, lmarks)),
                )
            )
        print(line)
    else:
        print("Список пуст")


def select_all(db_name: str) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех студентов.
    """
    conn = connect(db_name)

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT students.student_name, students.student_group, marks.marks_list
        FROM students
        INNER JOIN marks ON marks.mark_id = students.mark_id
        """
    )
    rows = cursor.fetchall()

    conn.close()
    return [
        {
            "name": row[0],
            "group": row[1],
            "marks": row[2],
        }
        for row in rows
    ]


def marks(db_name: str) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех студентов у кого присутствует оценка 2.
    """
    conn = connect(db_name)

    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT students.student_name, marks.marks_list
        FROM students
        INNER JOIN marks ON marks.mark_id = students.mark_id
        WHERE marks.marks_list LIKE '%2%';
        """
    )
    rows = cursor.fetchall()

    conn.close()
    return [
        {
            "name": row[0],
            "marks": row[1],
        }
        for row in rows
    ]


def main(command_line=None):
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "workers.db"),
        help="The database file name",
    )

    parser = argparse.ArgumentParser("students")

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser("add", parents=[file_parser], help="Add a new student")

    add.add_argument(
        "-n", "--name", action="store", required=True, help="The student's name"
    )
    add.add_argument(
        "-g", "--group", action="store", required=True, help="The student's group"
    )
    add.add_argument(
        "-m",
        "--marks",
        action="store",
        type=str,
        required=True,
        help="The student's marks",
    )

    showmarks = subparsers.add_parser(
        "show_marks", parents=[file_parser], help="Show students with mark 2"
    )

    _ = subparsers.add_parser(
        "show", parents=[file_parser], help="Display all students"
    )

    args = parser.parse_args(command_line)

    match args.command:
        case "add":
            conn = psycopg2.connect(
                user="postgres",
                password="hehehaha",
                host="127.0.0.1",
                port="5432"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT datname FROM pg_database;")
            list_database = cursor.fetchall()
            if (args.db,) in list_database:
                buf = [int(a) for a in args.marks]
                rightmarks = list(filter(lambda x: 0 < x < 6, buf))
                if len(rightmarks) != 5:
                    print("ошибка в количестве или значении оценок", file=sys.stderr)
                    exit()
                add_st(args.name, args.group, args.marks, args.db)
            else:
                conn = psycopg2.connect(
                    user="postgres",
                    password="hehehaha"
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                create = "create database " + args.db + ";"
                cursor.execute(create)

                create_db(args.db)

                buf = [int(a) for a in args.marks]
                rightmarks = list(filter(lambda x: 0 < x < 6, buf))
                if len(rightmarks) != 5:
                    print("ошибка в количестве или значении оценок", file=sys.stderr)
                    exit()
                add_st(args.name, args.group, args.marks, args.db)

        case "show":
            show(select_all(args.db))

        case "show_marks":
            show(marks(args.db))


if __name__ == "__main__":
    main()
