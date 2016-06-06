import sqlite3 as sql

class SQLiteDatabase:

    database = ""
    connection = None
    verbose = False

    def __init__(self, database):
        self.database = database

    def open_database(self):
        self.verbose_print("Opening: '%s'" % self.database)
        try:
            self.connection = sql.connect(self.database, check_same_thread=False)
        except sql.Error:
            self.verbose_print("Error Opening Database")

    def close_database(self):
        self.verbose_print("Closing: '%s'" % self.database)
        self.connection.close()

    def create_table(self, table_name, table_schema, clean_slate):
        self.verbose_print("Creating table %s(%s)" % (table_name, table_schema))
        cursor = self.connection.cursor()
        if clean_slate:
            cursor.execute("DROP TABLE IF EXISTS %s" % table_name)
        cursor.execute("CREATE TABLE IF NOT EXISTS %s(%s)" % (table_name, table_schema))

    def read_from_table(self, table_name):
        cursor = self.connection.cursor()
        self.verbose_print("Reading From '%s'" % table_name)
        cursor.execute("SELECT * FROM %s" % table_name)
        rows = cursor.fetchall()
        return rows

    def write_to_table(self, table_name, table_schema, data):
        self.verbose_print("Writing to table '%s': %s" % (table_name, data))
        cursor = self.connection.cursor()
        self.verbose_print("INSERT INTO %s(%s) VALUES(%s)" % (table_name, table_schema, data))
        cursor.execute("INSERT INTO %s(%s) VALUES(%s)" % (table_name, table_schema, data))
        cursor.close()

    def commit(self):
        self.verbose_print("Submitting changes.")
        self.connection.commit()

    def verbose_print(self, string):
        if self.verbose:
            print("\t * [Database]: %s" % string)
