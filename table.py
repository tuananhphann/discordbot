import sqlite3

import constants


class Table:
    def __init__(self, database_name: str) -> None:
        self.path = constants.CUR_PATH + f"/bot_data/{database_name}"
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()

    def checkTable(self, table_name: str) -> bool:
        "Checks if a table is exists or not."
        table = self.cur.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        ).fetchall()
        if len(table) == 1:
            return True
        return False

    def createTable(self, table_name: str, *property):
        """Creates a table with the specified name if it does not exist.
        There are two ways to pass properties:
            Pass by a pair: 'property DATATYPE'
            Pass by a string: 'property1 DATATYPE, property2 DATATYPE, ...'
        """

        if len(property) == 1:
            if "," in property[0]:
                self.cur.execute(f"CREATE TABLE {table_name}({property[0]})")
        else:
            string = ", ".join(property)
            self.cur.execute(f"CREATE TABLE {table_name}({string})")

    def dropTable(self, table_name: str):
        self.cur.execute(f"DROP TABLE {table_name}")

    def addRecord(self, table_name: str, *values):
        if len(values) == 1:
            if "," in values[0]:
                sql = f"INSERT INTO {table_name} VALUES ({values[0]})"
        else:
            string = ""
            for val in values:
                if isinstance(val, str):
                    if values.index(val) == len(values) - 1:
                        string += f'"{val}"'
                    else:
                        string += f'"{val}", '

            sql = f"INSERT INTO {table_name} VALUES ({string})"
        self.cur.execute(sql)
        self.con.commit()

    def checkRecord(self, table_name: str, value, property: str = "ID"):
        if isinstance(value, str):
            sql = (
                f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {property}="{value}");'
            )
        else:
            sql = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {property}={value});"
        data = self.cur.execute(sql).fetchone()
        if data[0] == 1:
            return True
        return False

    def deleteRecord(self, table_name: str, value, property: str = "ID"):
        if isinstance(value, str):
            sql = f'DELETE FROM {table_name} WHERE {property} = "{value}"'
        else:
            sql = f"DELETE FROM {table_name} WHERE {property} = {value}"

        self.cur.execute(sql)
        self.con.commit()

    def deleteAllRecord(self, table_name: str):
        self.cur.execute(f"DELETE FROM {table_name}")
        self.con.commit()

    def query(self, query: str, commit=False):
        """Basic query to the database like query for records or insert records."""
        self.cur.execute(query)
        if commit == True:
            self.con.commit()
        else:
            return self.cur.fetchall()
