from app import app, DATABASE_NAME
from flask import render_template, request, session
from utils import get_db_connection
from models.index import *
import random
from numpy import isnan


@app.route('/', methods=['GET', 'POST'])
def main():
    conn = get_db_connection(DATABASE_NAME)

    is_login = not(session.get('user_id') is None)
    
    lesson_data = get_lesson_data(conn, session.get('lesson_id', 1))
    lesson_name = lesson_data[0]
    lesson_short_description = lesson_data[1]

    
    # print(random_word)

    lesson_max_score = tuple(get_lesson_max_score(conn, session.get('lesson_id', 1))['lesson_max_score'])[0]
    lesson_user_score = tuple(get_lesson_user_score(conn, session.get('user_id', 1), session.get('lesson_id', 1))['lesson_user_score'])[0]

    lesson_count = get_lesson_count(conn)

    if request.method == 'POST':
        if 'add_to_fav' in request.form:
            vocabulary_id = int(request.values.get('vocabulary_id'))
            add_voc_fav(conn, session['user_id'], vocabulary_id)
        else:
            vocabulary_id = int(request.values.get('vocabulary_id'))
            del_voc_fav(conn, session['user_id'], vocabulary_id)
    
    lesson_percentage = round((session.get('lesson_id', 1) / lesson_count) * 100, 2)
    words = get_words(conn, session.get('user_id', 1)).to_dict('records')
    random_word = random.choice(words)
    html = render_template(
        'main_page.html',
        is_login=is_login,
        lesson_name=lesson_name,
        lesson_short_description=lesson_short_description,
        lesson_max_score=lesson_max_score,
        lesson_user_score=lesson_user_score,
        lesson_percentage=lesson_percentage,
        random_word=random_word,
        isnan=isnan,
    )
    
    return html