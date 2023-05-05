#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3


def sql_fetch(con):
    cursor_obj = con.cursor()
    cursor_obj.execute("CREATE TABLE IF NOT EXISTS projects(id INTEGER, name TEXT)")

    con.commit()


if __name__ == "__main__":
    con = sqlite3.connect("mydatabase.db")
    sql_fetch(con)
