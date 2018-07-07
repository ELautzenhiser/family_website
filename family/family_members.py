import os
from flask import Blueprint, render_template
from .db import query_db, get_all_rows

bp = Blueprint('family', __name__)

@bp.route('/family_tree')
def view_family_tree():
    people = get_all_rows('People')
    return render_template('family_tree.html', people=people)

    
