import os
from flask import Blueprint, current_app, render_template
from .db import query_db, get_all_rows, get_db_row

bp = Blueprint('family', __name__)

@bp.route('/family_tree')
def view_family_tree():
    people = get_all_rows('People')
    return render_template('family_tree.html', people=people)


@bp.route('/family_member/<int:person_id>')
def view_family_member(person_id):
    person = get_db_row('People', person_id)
    memoirs = get_memoirs(person_id)
    photos = get_photos(person_id)
    family_member = {'photos' : photos, 'memoirs' : memoirs}
    family_member['full_name'] = get_full_name(person)
    family_member['content'] = get_person_html(person)
    return render_template('family_member.html', family_member=family_member)

def get_memoirs(person_id):
    query = 'SELECT m.memoir_id, m.name, ' \
            'p.first_name || " " || p.last_name as author_name ' \
            'FROM Memoirs m INNER JOIN People p ON m.author_id=p.person_id ' \
            'LEFT JOIN Memoir_tags mt on m.memoir_id=mt.memoir_id ' \
            'WHERE (p.person_id={0} OR mt.person_id={0})'.format(person_id)
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
        return '{0} {1} {2}'.format(person['first_name'],person['middle_name'],person['last_name'])
    else:
        return '{0} {1}'.format(person['first_name'],person['last_name'])
    
def get_person_html(person):
    content = ''
    if person['blurb_file']:
        filename = os.path.join(current_app.instance_path, 'blurbs', person['blurb_file'])
        with open(filename, 'r') as file:
            content += file.read()
    return content
    
