import pathlib
import sqlite3
from sqlite3 import Error


class Database:

    def __init__(self, file_name):
        self.database = str(pathlib.Path().absolute()) + r"\data" + '\\' + file_name + ".db"
        self.conn = self.create_connection()
        self.create_table()

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

    def create_table(self):
        """ create a table from the create_table_sql statement """

        # /!\
        # contaminated values:
        # -1 = unreferenced
        # 0 = not contaminated
        # 1 = contaminated
        create_table_sql = """ CREATE TABLE IF NOT EXISTS persons (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        firt_name text,
                                        contaminated int,
                                        contaminated_date date 
                                    ); """

        if self.conn is None:
            print("Error! cannot create the database connection.")
            return

        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_item(self, item_values):
        """
        Create a new project into the projects table
        :return: item id
        """
        sql = ''' INSERT INTO persons (name, firt_name, contaminated, contaminated_date)
                  VALUES(?, ?, ?, ?) '''
        cur = self.conn.cursor()
        cur.execute(sql, item_values)
        self.conn.commit()

        # Return the generated id
        return cur.lastrowid

    def select_item(self):
        """
        Query tasks by priority
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM persons")

        rows = cur.fetchall()

        for row in rows:
            print(row)

    def delete_item(self, item_id):
        """
        Delete a task by task id
        """
        sql = 'DELETE FROM persons WHERE id=?'
        cur = self.conn.cursor()
        cur.execute(sql, (item_id,))
        self.conn.commit()


def main():

    database = Database('mydatabase')
    database.create_item(('Alexandre', 'Biden', 1, "2021-03-21"))
    database.select_item()
    # database.delete_item(1)


if __name__ == '__main__':
    main()
