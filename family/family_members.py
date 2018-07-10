import os
from flask import Blueprint, current_app, render_template
from .db import query_db, get_all_rows, get_db_row, display_name

bp = Blueprint('family', __name__)

@bp.route('/family_tree')
def view_family_tree():
    people = get_family_members()
    return render_template('family_tree.html', people=people)


@bp.route('/family_member/<int:person_id>')
def view_family_member(person_id):
    person = get_db_row('People', person_id)
    memoirs = get_memoirs(person_id)
    photos = get_photos(person_id)
    family_member = {'photos' : photos, 'memoirs' : memoirs}
    family_member['display_name'] = get_display_name(person)
    family_member['full_name'] = get_full_name(person)
    family_member['content'] = get_person_html(person)
    family_member['parents'] = get_parents(person_id)
    family_member['siblings'] = get_siblings(person_id)
    family_member['children'] = get_children(person_id)
    return render_template('family_member.html', family_member=family_member)

def get_memoirs(person_id):
    name_sql = display_name('p', 'author_name')
    query = 'SELECT m.memoir_id, m.name, {0} ' \
            'FROM Memoirs m INNER JOIN People p ON m.author_id=p.person_id ' \
            'LEFT JOIN Memoir_tags mt on m.memoir_id=mt.memoir_id ' \
            'WHERE (p.person_id={1} OR mt.person_id={1})'.format(name_sql, person_id)
    return query_db(query)

def get_photos(person_id):
    PHOTO_FOLDER = os.path.join(current_app.instance_path, 'images\\')
    query = 'SELECT "{0}" || p.filename as file_location, ' \
            'p.description FROM Photos p ' \
            'INNER JOIN Photo_tags pt on p.photo_id=pt.photo_id ' \
            'WHERE pt.person_id={1}'.format(PHOTO_FOLDER, person_id)
    return query_db(query)

def get_full_name(person):
    if person['middle_name']:
        return '{0} {1} {2}'.format(person['first_name'], person['middle_name'], person['last_name'])
    else:
        return '{0} {1}'.format(person['first_name'], person['last_name'])

def get_display_name(person):
    if person['preferred_name']:
        return '{0} {1}'.format(person['preferred_name'], person['last_name'])
    else:
        return '{0} {1}'.format(person['first_name'], person['last_name'])
    
def get_person_html(person):
    content = ''
    if person['blurb_file']:
        filename = os.path.join(current_app.instance_path, 'blurbs', person['blurb_file'])
        with open(filename, 'r') as file:
            content += file.read()
    return content

def get_parents(person_id):
    name_sql = display_name('p2', 'parent_name')
    query = 'SELECT p2.person_id, {0} FROM People p INNER JOIN People p2 ' \
            'ON p2.person_id IN (p.mother_id, p.father_id) ' \
            'WHERE p.person_id={1}'.format(name_sql, person_id)
    return query_db(query)

def get_siblings(person_id):
    name_sql = display_name('p2', 'sibling_name')
    query = 'SELECT p2.person_id, {0} FROM People p INNER JOIN People p2 ' \
            'ON (p.mother_id=p2.mother_id OR p.father_id=p2.father_id) AND p.person_id!=p2.person_id ' \
            'WHERE p.person_id={1}'.format(name_sql, person_id)
    return query_db(query)

def get_children(person_id):
    name_sql = display_name('p2', 'child_name')
    query = 'SELECT p2.person_id, {0} FROM People p INNER JOIN People p2 ' \
            'ON p.person_id IN (p2.mother_id, p2.father_id) ' \
            'WHERE p.person_id={1}'.format(name_sql, person_id)
    return query_db(query)

def get_family_members():
    query = 'SELECT * FROM People ORDER BY birth_year, birth_month, birth_day'
    return query_db(query, -1)
    
