import sqlite3 # https://docs.python.org/2/library/sqlite3.html
import pathlib
import os

class Database:

    database_file_name = None

    def __init__(self, database_file_name=''):
        if not database_file_name:
            return
        
        self.database_file_name = database_file_name
        self.database_file_path = pathlib.Path(self.database_file_name)

    def run_read_sql_command(self, command, args_list):
        self.cursor.execute(command, tuple(args_list))
        return self.cursor.fetchall()

    def run_write_sql_commands(self, commands=[]):
        for sql_command, *arg_tuple in commands:
            self.cursor.execute(sql_command, tuple(arg_tuple))
        return self.connection.commit()
    
    def run_write_sql_command_many_data(self, sql_command, data_list=[]):
        self.cursor.executemany(sql_command, data_list)
        return self.connection.commit()
    
    def down(self):
        self.connection.close()
    
    def exist(self):
        return self.database_file_path.exists()
    
    def delete(self):
        if self.exist():
            os.remove(self.database_file_path.absolute())
    
    def up(self):
        self.connection = sqlite3.connect(self.database_file_name)
        self.cursor = self.connection.cursor()

class DatabaseManager:

    db_name = 'my-database.sqlite'
    database_object = None

    def __init__(self, *args, **kwargs):
        self.db = Database(self.db_name)

        self.prepare_database_and_schema()
    
    def count(self, table_name, db_object):
        if self.db.connection and self.db.cursor:
            count_command = self.filter_command(table_name, db_object).replace('*', 'COUNT(*)')
            r = self.db.run_read_sql_command(
                count_command,
                tuple(db_object.values())
            )

            return r[0][0]
    
    def filter_command(self, table_name, db_object):
        return 'SELECT * FROM {table_name} WHERE {fields_match}'.format(
                    table_name=table_name,
                    fields_match=' AND '.join([ f'{key}=?' for key in db_object.keys()])
                )

    
    def filter(self, table_name, db_object):
        if self.db.connection and self.db.cursor:
            r = self.db.run_read_sql_command(
                self.filter_command(table_name, db_object),
                # tuple for value match
                tuple(db_object.values())
            )
            
            return r
    
    def update(self, table_name, db_object, pk):
        """
            update: https://stackoverflow.com/questions/19191704/how-to-update-several-specific-columns-using-sqlite3-python
        """
        if self.db.connection and self.db.cursor and pk:
            self.db.run_write_sql_commands([
                ('UPDATE {} SET {} WHERE id=?'.format(
                    table_name,
                    ','.join([ f'{key}=?' for key in db_object.keys()])
                ),) +
                # value tuples
                tuple(db_object.values()) + 
                tuple([pk])
            ])
            return
        
    def create(self, table_name, db_object, unique_fields=[]):
        if self.db.connection and self.db.cursor:
            try:
                if not len(unique_fields) == 0:
                    unique_object = { key: db_object[key] for key in unique_fields }
                else:
                    unique_object = db_object
                count = self.count(table_name, unique_object)
                if count > 0:
                    print("INFO: object already exist, will skip creation. table={}, object: {}".format(table_name, db_object))
                    return

                self.db.run_write_sql_commands([
                    ('INSERT INTO {} ({}) VALUES ({});'.format(
                        table_name,
                        # insert question marks for field
                        ','.join(db_object.keys()),
                        # insert question marks for value
                        ','.join(['?'] * len(db_object)),
                    ),) +
                    # value tuples
                    tuple(db_object.values())
                ])
            except sqlite3.IntegrityError:
                print("INFO: create(): object already exist, will do nothing. table={}, object: {}".format(table_name, db_object))
            except Exception as err:
                print(err)
            return
    
    def prepare_database_and_schema(self):
        if self.db.exist():
            # load db file & connect
            self.db.up()
        else:
            # create db file & connect
            self.db.up()

            # create schema for tables
            self.db.run_write_sql_commands([
                ('''CREATE TABLE States (
                    id INTEGER PRIMARY KEY,
                    Name TEXT
                );
                ''',),
            ])
            self.db.run_write_sql_commands([
                ('''CREATE TABLE Sites (
                    id INTEGER PRIMARY KEY,
                    Name TEXT,
                    Type TEXT,
                    Description TEXT,
                    Location TEXT,
                    
                    StateID INTEGER,
                    FOREIGN KEY (StateID) REFERENCES States(id)
                );
                ''',),
            ])
            self.db.run_write_sql_commands([
                ('''CREATE TABLE SitePages (
                    id INTEGER PRIMARY KEY,
                    Url TEXT,
                    IsDone INTEGER
                );
                ''',),
            ])

        return self.db