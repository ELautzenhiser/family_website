import os
from flask import Blueprint, render_template
from .db import query_db

bp = Blueprint('memoirs', __name__)

@bp.route('/memoirs')
def view_memoirs():
    memoirs = get_memoirs()
    return render_template('memoirs.html', memoirs=memoirs)


@bp.route('/memoir/<int:memoir_id>')
def memoir(memoir_id):
    memoir = get_memoir_from_id(memoir_id)
    text = get_memoir_from_file(memoir['filename'])
    return render_template('memoir.html', memoir=memoir, memoir_text=text)


def get_memoirs():
    query = 'SELECT m.memoir_id, m.name, p.first_name || " " || p.last_name as author_name ' \
            'FROM Memoirs m INNER JOIN People p on m.author_id=p.person_id'
    return query_db(query)

def get_memoir_from_id(memoir_id):
    query = 'SELECT m.name, m.year_written, m.subject, m.filename, m.author_id, ' \
            'p.first_name || " " || p.last_name as author_name ' \
            'FROM Memoirs m INNER JOIN People p on m.author_id=p.person_id ' \
            'WHERE m.memoir_id={0}'.format(memoir_id)
    return query_db(query, 1)

def get_memoir_from_file(filename):
    filename = os.path.join(current_app.instance_path, 'memoirs', filename)
    with open(filename, 'r') as f:
        text = f.read()
    return convert_to_html(text)

def convert_to_html(text):
    text_list = text.split('\n')
    is_list = False
    html_text = []
    for line in text_list:
        if line == '':
            html_text.append('<br>\n')
        elif line[0] in ('-','*'):
            if not is_list:
                html_text.append('<ul>\n')
                is_list = True
            html_text.append('<li>'+line[1:]+'</li>\n')
        else:
            if is_list:
                html_text.append('</ul>\n')
                is_list = False
            html_text.append('<p>'+line+'</p>\n')
    return '\n'.join(html_text)
