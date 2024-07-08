from app import app, DATABASE_NAME
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.favourites import *

@app.route('/favourites', methods=['GET', 'POST'])
def favourites():
    connection = get_db_connection(DATABASE_NAME)
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = request.url
        return redirect(url_for('login_page'))
    #########################

    session['article_back_url'] = request.url

    if not session.get('fav_category'):
        session['fav_category'] = 'articles'
    
    articles = get_fav_articles(connection, session['user_id']).to_dict('records')

    if request.method == 'POST':
        if 'articles' in request.form:
            session['fav_category'] = 'articles'
        elif 'vocabulary' in request.form:
            session['fav_category'] = 'vocabulary'
        elif 'theory' in request.form:
            session['fav_category'] = 'theory'
        elif 'del_article' in request.form:
            article_id = int(request.values.get('article_id'))
            session['fav_category'] = 'articles'
            del_fav_articles(connection, article_id, session['user_id'])
        elif 'del_voc_fav' in request.form:
            vocabulary_id = int(request.values.get('vocabulary_id'))
            session['fav_category'] = 'vocabulary'
            del_voc_fav(connection, session['user_id'], vocabulary_id)
    
    if 'flash_card' in request.values:
        session['fav_category'] = 'vocabulary'
        flash_card_params = request.values.getlist('flash_card_params')
        params_type = 0
        if 'korean_russian' in flash_card_params and 'russian_korean' in flash_card_params:
            params_type = 3
        elif 'korean_russian' in flash_card_params:
            params_type = 1
        elif 'russian_korean' in flash_card_params:
            params_type = 2
        if params_type:
            session['flash_cards'] = []
            vocabulary_ids = request.values.get('vocabulary_ids')
            if vocabulary_ids:
                return redirect(url_for('flash_cards', params_type=params_type, ids=vocabulary_ids))


    articles = get_fav_articles(connection, session['user_id']).to_dict('records')
    vocabulary = get_fav_voc(connection, session['user_id']).to_dict('records')
    theories = get_fav_theory(connection, session['user_id']).to_dict('records')

    html = render_template(
        'favourites.html',
        fav_category=session['fav_category'], 
        articles=articles,
        vocabulary=vocabulary,
        theories=theories,
    )
    
    return html


@app.route('/favourites/theory/<int:theory_id>', methods=['GET', 'POST'])
def theory(theory_id):
    connection = get_db_connection(DATABASE_NAME)
    # #########################
    # session['user_id'] = 1
    # #########################

    theory_data = get_theory_data(connection, theory_id)

    if request.method == 'POST':
        if 'del_fav_theory' in request.form:
            del_theory_fav(connection, session['user_id'], theory_id)
            return redirect(url_for('favourites'))
        if 'back' in request.form:
            return redirect(url_for('favourites'))

    html = render_template(
        'full_theory.html',
        theory_data=theory_data,
    )
    
    return html


@app.route('/flash_cards/<int:params_type>/<string:ids>', methods=['GET', 'POST'])
def flash_cards(params_type, ids):
    connection = get_db_connection(DATABASE_NAME)
    # #########################
    # session['user_id'] = 1
    # #########################

    vocabulary_ids = tuple(ids.split(';'))

    if not session.get('flash_cards'):
       session['flash_cards'] = get_flash_cards(connection, params_type, session['user_id'], (*vocabulary_ids, vocabulary_ids[0])).to_dict('records')
    
    word_index = 0
    show_answer = 0

    if request.method == 'POST':
        if 'answer_button' in request.form:
            word_index = int(request.form.get('word_index'))
            show_answer = 1
        elif 'question_button' in request.form:
            word_index = int(request.form.get('word_index'))
            show_answer = 0
        elif 'next' in request.form:
            word_index = (int(request.form.get('word_index')) + 1) % len(session['flash_cards'])
        elif 'previous' in request.form:
            word_index = int(request.form.get('word_index')) - 1
            if word_index < 0:
                word_index = len(session['flash_cards']) - 1

    html = render_template(
        'flash_cards.html',
        flash_cards=session['flash_cards'],
        word_index=word_index,
        show_answer=show_answer,
    )
    
    return html