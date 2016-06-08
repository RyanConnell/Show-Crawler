from util import util

class DatabaseLayout():

    def __init__(self, schema, mask):
        self.schema = schema
        self.create_mask(schema, mask)
        self.data_types = self.create_data_types()

    def create_data_types(self):
        return ""

    def create_mask(self, schema, mask):
        self.database_vars = str.split(util.remove_character(schema, ','), " ")
        self.masked_vars = str.split(util.remove_character(mask, ','), " ")

class DatabaseData():

    def __init__(self, table_name, database_data, database_layout):
        self.table_name = table_name
        self.database_data = database_data
        self.database_layout = database_layout

    def create_database_string(self, data):
        database_string = ""
        for i in range(len(self.database_layout.database_vars)):
            data_type = type(data[self.database_layout.masked_vars[i]])
            if data_type is str or data_type is bytes:
                if database_string == "":
                    database_string = "\"%s\"" % data[self.database_layout.masked_vars[i]]
                else:
                    database_string = "%s, \"%s\"" % (database_string, data[self.database_layout.masked_vars[i]])
            elif data_type is int:
                if database_string == "":
                    database_string = "%d" % data[self.database_layout.masked_vars[i]]
                else:
                    database_string = "%s, %d" % (database_string, data[self.database_layout.masked_vars[i]])
            elif data_type is bool:
                value = 1 if data[self.database_layout.masked_vars[i]] else 0
                if database_string == "":
                    database_string = "%d" % value
                else:
                    database_string = "%s, %d" % (database_string, value)
            else:
                print("[ERROR] Was unable to add data of type %s" % data_type)
        return database_string

    def write_to_database(self, database):
        database.open_database()
        for data in self.database_data:
            if len(data) != 0:
                database.write_to_table(self.table_name, self.database_layout.schema, self.create_database_string(data))
        database.commit()
        database.close_database()
