import sqlite3
import click
import os
from flask import current_app, g
from flask.cli import with_appcontext

def open_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = open_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        
    data_file = os.path.join(current_app.instance_path, 'family_data.sql')
    with current_app.open_resource(data_file) as f:
        db.executescript(f.read().decode('utf8'))

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
    results = db.execute(query)
    if num_rows == 1:
        return results.fetchone()
    elif num_rows == -1:
        return results.fetchall()
    else:
        return cursor.fetchmany(num_rows)

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
