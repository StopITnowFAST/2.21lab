#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import sys
import typing as t
from pathlib import Path


def add_st(database_path: Path, name: str, group: str, lmarks: str) -> None:
    """
    Ввести данные студента в базу данных
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
            INSERT INTO marks (marks_list) 
            VALUES (?)
            """,
        (lmarks,),
    )

    mark_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO students (student_name, mark_id, student_group)
        VALUES (?, ?, ?)
        """,
        (name, mark_id, group),
    )
    conn.commit()
    conn.close()


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            marks_list TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_group TEXT NOT NULL,
            mark_id INTEGER NOT NULL,
            FOREIGN KEY(mark_id) REFERENCES marks(mark_id)
        )
        """
    )

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


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех студентов.
    """
    conn = sqlite3.connect(database_path)
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


def marks(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать всех студентов у кого присутствует оценка 2.
    """
    conn = sqlite3.connect(database_path)
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

    db_path = Path(args.db)
    create_db(db_path)

    match args.command:
        case "add":
            buf = [int(a) for a in args.marks]
            rightmarks = list(filter(lambda x: 0 < x < 6, buf))
            if len(rightmarks) != 5:
                print("ошибка в количестве или значении оценок", file=sys.stderr)
                exit()
            add_st(db_path, args.name, args.group, args.marks)

        case "show":
            show(select_all(db_path))

        case "show_marks":
            show(marks(db_path))


if __name__ == "__main__":
    main()
