from flask import Blueprint, Flask, render_template
from .db import open_db

bp = Blueprint('memoirs', __name__)

@bp.route('/memoirs')
def view_memoirs():
    memoirs = get_memoirs()
    return render_template('memoirs.html', memoirs=memoirs)


def get_memoirs():
    db = open_db()
    query = 'SELECT m.memoir_id, m.name, p.first_name || " " || p.last_name as author ' \
            'FROM Memoirs m INNER JOIN People p on m.author_id=p.person_id'
    memoirs = db.execute(query).fetchall()
    return memoirs
