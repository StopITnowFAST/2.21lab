#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3


def sql_fetch(con):
    cursor_obj = con.cursor()
    cursor_obj.execute("SELECT * FROM employees")

    rows = cursorObj.fetchall()
    for row in rows:
        print(row)


if __name__ == "__main__":
    con = sqlite3.connect("mydatabase.db")
    sql_fetch(con)
