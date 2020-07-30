import pymysql
import click
import os
from .db_config import *
from flask import current_app, g
from flask.cli import with_appcontext

def parse_sql(filename):
     with current_app.open_resource(filename) as file:
          data = file.read().decode('utf8').split('\n')
          statements = []
          DELIMITER = ';'
          statement = ''

          for line_num, line in enumerate(data):
               if not line.strip():
                    continue

               elif DELIMITER not in line:
                    statement += line

               elif statement:
                    statement += line
                    statements.append(statement.strip())
                    statement = ''
               else:
                    statements.append(line.strip())
          return statements

        
def open_db():
     if 'db' not in g:
          g.db = pymysql.connect(host=sql_vals['host'],
                          db=sql_vals['db'],
                          user=sql_vals['user'],
                          password=sql_vals['password'])
               
     return g.db


def get_db():
    c = open_db()
    return c.cursor(pymysql.cursors.DictCursor)

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = open_db()

    db_statements = parse_sql('schema.sql')
    
        
    data_file = os.path.join(current_app.instance_path, 'family_data.sql')
    db_statements += parse_sql(data_file)

    with db.cursor() as cursor:
        for statement in db_statements:
             cursor.execute(statement)
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def query_db(query, num_rows=-1):
     db = open_db()
     with db.cursor(pymysql.cursors.DictCursor) as cursor:
          cursor.execute(query)
     if num_rows == 1:
          return cursor.fetchone()
     elif num_rows == -1:
          return cursor.fetchall()
     else:
          return cursor.fetchmany(num_rows)

def insert_db(query, values):
     db = open_db()
     with db.cursor(pymysql.cursors.DictCursor) as cursor:
          cursor.execute(query,values)
     db.commit()

def get_all_rows(table):
    query = 'SELECT * FROM {0}'.format(table)
    return query_db(query, -1)

def get_db_row(table, id):
    table_ids = {'people': 'person_id', 'memoir': 'memoir_id'}
    id_type = table_ids.get(table.lower())
    if not id_type:
        return None
    query = 'SELECT * FROM {0} WHERE {1}={2}'.format(table, id_type, id)
    return query_db(query, 1)

def display_name(table_abbreviation='', alias='display_name'):
    if table_abbreviation != '':
        table_abbreviation += '.'
    query = 'CASE WHEN {0}preferred_name IS NOT NULL THEN CONCAT_WS(" ", {0}preferred_name, {0}last_name) ' \
            'ELSE CONCAT_WS(" ",{0}first_name, {0}last_name) END AS {1}'.format(table_abbreviation, alias)
    return query
