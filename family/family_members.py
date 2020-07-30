import os
from flask import Blueprint, current_app, flash, redirect, \
    render_template, request, url_for
from .db import query_db, get_all_rows, get_db_row, display_name, insert_db
from datetime import datetime

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
    query = 'SELECT m.memoir_id, m.title, {0} ' \
            'FROM Memoirs m INNER JOIN People p ON m.author_id=p.person_id ' \
            'LEFT JOIN Memoir_tags mt on m.memoir_id=mt.memoir_id ' \
            'WHERE (p.person_id={1} OR mt.person_id={1})'.format(name_sql, person_id)
    return query_db(query)

def get_photos(person_id):
    PHOTO_FOLDER = os.path.join(current_app.instance_path, 'images')
    query = 'SELECT CONCAT("{0}", p.filename) as file_location, ' \
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
    display_sql = display_name()
    query = 'SELECT {0}, People.* FROM People ORDER BY birth_year, birth_month, birth_day'.format(display_sql)
    return query_db(query, -1)

@bp.route('/family_members/create', methods=['GET', 'POST'])
def create_family_member():
    if request.method == 'POST':
        if request.form.get('action') != 'Save':
            return redirect(url_for('family.view_family_tree'))
        form_dict = request.form.copy()
        for value in form_dict:
            if form_dict[value] == '':
                form_dict[value] = None
        first_name = form_dict.get('first_name')
        last_name = form_dict.get('last_name')
        middle_name = form_dict.get('middle_name')
        preferred_name = form_dict.get('preferred_name')
        birth_year = form_dict.get('birth_year')
        birth_month = form_dict.get('birth_month')
        birth_day = form_dict.get('birth_day')
        gender = form_dict.get('gender')
        mother_id = form_dict.get('mother_id')
        father_id = form_dict.get('father_id')
        spouse_id = form_dict.get('spouse_id')
        errors = check_input(first_name, last_name, middle_name, preferred_name, birth_year, birth_month,
                             birth_day, gender, mother_id, father_id, spouse_id)
        if errors:
            for error in errors:
                flash(error)
            family_members = get_family_members()
            return render_template('create_family_member.html',
                                   first_name=first_name,
                                   last_name=last_name,
                                   middle_name=middle_name,
                                   preferred_name=preferred_name,
                                   birth_year=birth_year,
                                   birth_month=birth_month,
                                   birth_day=birth_day,
                                   gender=gender,
                                   mother_id=mother_id,
                                   father_id=father_id,
                                   spouse_id=spouse_id,
                                   family_members=family_members)
        else:
            save_family_member(first_name, last_name, middle_name, preferred_name,
                               birth_year, birth_month, birth_day, gender, mother_id,
                               father_id, spouse_id)
            flash('Family member saved successfully!')
            return redirect(url_for('family.view_family_tree'))
        
    ##Method=GET
    else:
        family_members = get_family_members()
        return render_template('create_family_member.html', family_members=family_members)

def save_family_member(first_name, last_name, middle_name, preferred_name,
                                        birth_year, birth_month, birth_day, gender, mother_id,
                                        father_id, spouse_id):
    insert_sql = 'INSERT INTO PEOPLE (first_name, last_name, middle_name, preferred_name, ' \
                        'birth_year, birth_month, birth_day, gender, mother_id, father_id) ' \
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    insert_db(insert_sql,(first_name, last_name, middle_name, preferred_name, birth_year,
                            birth_month, birth_day, gender, mother_id, father_id))

def check_input(first_name, last_name, middle_name, preferred_name, birth_year, birth_month,
                birth_day, gender, mother_id, father_id, spouse_id):
    errors = []
    try:
        if birth_year:
            birth_year = int(birth_year)
            if birth_year < 1700 or birth_year > datetime.today().year:
                errors.append('We\'re accepting family members born in the last 300 years.')
        if birth_month:
            birth_month = int(birth_month)
            if birth_month < 1 or birth_month > 12:
                errors.append('The month must be between 1 and 12.')
        if birth_day:
            birth_day = int(birth_day)
            if birth_day < 1 or birth_day > 21:
                errors.append('The day must be between 1 and 31.')
        if birth_year and birth_month and birth_day:
            datetime.datetime(birth_year, birth_month, birth_day)
    except Exception as e:
        print(e)
        errors.append('The birth date must be in the format yyyy, MM, dd.')
    if not (mother_id or father_id or spouse_id):
        errors.append('The person must be related to a Lautzenhiser somehow!')
    return errors
