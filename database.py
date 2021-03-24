import pathlib
import sqlite3
from sqlite3 import Error


class Database:

    def __init__(self, file_name):
        self.database = str(pathlib.Path().absolute()) + r"\data" + '\\' + file_name + '.db'
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

        for row in rows:
            print(row)

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


def main():

    database = Database('trump_edges')
    database.select_item()
    database2 = Database('trump_vertices')
    database2.select_item()


if __name__ == '__main__':
    main()

