import pathlib
import sqlite3
from sqlite3 import Error
import os


class Database:

    def __init__(self, file_name):
        # Path to the database file
        self.database = os.path.join(str(pathlib.Path().absolute()), "data", file_name + '.db')

        self.file_name = file_name

        # Keeping connection to the database accessible from everywhere in the class.
        self.conn = self.create_connection()

    def create_connection(self):
        """
        Create a database connection to a SQLite database
        """

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
        """
        Select status. For exemple infected or not. (NOT USED)

        Parameters
        ----------
        name: type string: Name of the person, used to access information in the database.

        Returns
        -------
        result: type list: rows of the query result

        """
        cur = self.conn.cursor()

        # The ? is used to specify that we are using a variable. We reference it when executing.
        sql = '''SELECT status FROM vertices WHERE name=?'''
        cur.execute(sql, (name,))

        result = cur.fetchall()
        return result

    def delete_item(self, item_value, field):
        """
        Delete a task by task id.

        Parameters
        ----------
        item_value: The value of the item to remove
        field: type string: The column name of the value

        Returns
        -------

        """
        sql = 'DELETE FROM ' + self.file_name + ' WHERE ' + field + '=?'
        cur = self.conn.cursor()
        cur.execute(sql, (item_value,))
        self.conn.commit()

    def change_status(self, name, value):
        """
        Update the "status" field of item verifying "name" column matches the name variable.

        Parameters
        ----------
        name:  Matches of the "name" column
        value: The new value to set.

        Returns
        -------

        """
        sql = '''UPDATE vertices
                      SET status = ?
                      WHERE name = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (value, name))
        self.conn.commit()
