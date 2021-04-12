import pathlib
import sqlite3
from sqlite3 import Error
import os


class Database:

    def __init__(self, file_name):
        self.database = os.path.join(str(pathlib.Path().absolute()), "data", file_name + '.db')
        self.file_name = file_name
        self.conn = self.create_connection()

    def create_connection(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(self.database)
            return conn
        except Error as e:
            print(self.database)
            print("create_connection error is saying:")
            print(e)

        return conn

    def select_item(self):
        """
        Query tasks by priority
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM " + self.file_name)

        rows = cur.fetchall()

        return rows

    def select_status(self, name):
        cur = self.conn.cursor()
        sql = '''SELECT status FROM vertices WHERE name=?'''
        cur.execute(sql, (name,))
        result = cur.fetchall()
        return result

    def delete_item(self, item_value, field):
        """
        Delete a task by task id
        :param item_value: the value of the item to remove
        :param field: the column name of the value
        """
        sql = 'DELETE FROM ' + self.file_name + ' WHERE ' + field + '=?'
        cur = self.conn.cursor()
        cur.execute(sql, (item_value,))
        self.conn.commit()

    def change_status(self, name, value):
        """
        Update the "status" field of item with a name parameter
        :param name: identifier
        :param value: status value
        """
        sql = '''UPDATE vertices
                      SET status = ?
                      WHERE name = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (value, name))
        self.conn.commit()

