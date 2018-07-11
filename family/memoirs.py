import os
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from .db import display_name, insert_db, query_db

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
    name_sql = display_name('p','author_name')
    query = 'SELECT m.memoir_id, m.title, {0} ' \
            'FROM Memoirs m INNER JOIN People p on m.author_id=p.person_id'.format(name_sql)
    return query_db(query)


def get_memoir_from_id(memoir_id):
    name_sql = display_name('p', 'author_name')
    query = 'SELECT m.title, m.year_written, m.subject, m.filename, m.author_id, ' \
            '{0} ' \
            'FROM Memoirs m INNER JOIN People p on m.author_id=p.person_id ' \
            'WHERE m.memoir_id={1}'.format(name_sql, memoir_id)
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


@bp.route('/memoirs/create', methods=['GET', 'POST'])
def create_memoir():
    family_members = get_family_members() 
    if request.method == 'POST':
        title = request.form.get('title')
        author_id = request.form.get('author_id')
        subject = request.form.get('subject')
        memoir_text = request.form.get('memoir_text')
        errors = check_input(title, author_id, subject, memoir_text)
        if not errors:
            filename = generate_filename(title, author_id)
            errors = save_memoir_file(filename, memoir_text)
        if not errors:
            save_memoir_db(title, author_id, subject, filename)
        if errors:
            for error in errors:
                flash(error)
            return render_template('create_memoir.html',
                                   title=title,
                                   author_id=author_id,
                                   subject=subject,
                                   memoir_text=memoir_text,
                                   family_members=family_members)
        else:
            return redirect(url_for('memoirs.view_memoirs'))
        
        
    return render_template('create_memoir.html', family_members=family_members)


def get_family_members():
    display_sql = display_name()
    query = 'SELECT person_id, {0} FROM People ORDER BY display_name'.format(display_sql)
    return query_db(query, -1)


def check_input(title, author_id, subject, memoir_text):
    errors = []
    existing_query = 'SELECT memoir_id FROM Memoirs ' \
                     'WHERE title="{0}" AND author_id={1}'.format(title, author_id)
    results = query_db(existing_query, 1)
    if results:
        errors.append("You've already created a memoir named {0}. " \
                      "Please choose a new name.".format(title))
    return errors


def generate_filename(title, author_id):
    filename = title.replace(' ','_')+'_'+str(author_id)+'.txt'
    return filename


def save_memoir_file(filename, memoir_text):
    errors = []
    filename = os.path.join(current_app.instance_path, 'memoirs', filename)
    try:
        with open(filename, 'w') as file:
            file.write(memoir_text)
    except Exception as e:
        errors.append(str(e))
    return errors

def save_memoir_db(title, author_id, subject, filename):
    insert_sql = 'INSERT INTO Memoirs (title, author_id, year_written, subject, filename) ' \
                 'VALUES ("{0}", {1}, {2}, "{3}", "{4}")'.format(title,
                                                                 author_id,
                                                                 2018,
                                                                 subject,
                                                                 filename)
    insert_db(insert_sql)
                                                                 
