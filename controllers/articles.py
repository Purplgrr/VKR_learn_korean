from app import app, DATABASE_NAME
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.articles import *

@app.route('/articles', methods=['GET', 'POST'])
def articles():
    connection = get_db_connection(DATABASE_NAME)
    #########################
    if 'user_id' not in session:
        session['url_for_return'] = request.url
        return redirect(url_for('login_page'))
    #########################
    article_category_id = 1

    session['article_back_url'] = request.url
    
    if request.method == 'POST':
        if 'russian_button' in request.form:
            article_category_id = 1
        elif 'korean_button' in request.form:
            article_category_id = 2
        elif 'add_fav' in request.form:
            article_id = int(request.values.get('article_id'))
            add_fav_articles(connection, article_id, session['user_id'])
        elif 'del_fav' in request.form:
            article_id = int(request.values.get('article_id'))
            del_fav_articles(connection, article_id, session['user_id'])

    articles = get_articles(connection, article_category_id).to_dict('records')
    fav_articles = get_fav_articles(connection, session['user_id'])

    print(fav_articles)

    html = render_template(
        'articles.html',
        articles=articles,
        fav_articles=fav_articles,
        article_category_id=article_category_id,
    )
    
    return html


@app.route('/articles/<int:article_id>', methods=['GET', 'POST'])
def full_article(article_id):
    connection = get_db_connection(DATABASE_NAME)
    # #########################
    # session['user_id'] = 1
    # #########################
    
    if request.method == 'POST':
        if 'add_fav' in request.form:
            article_id = int(request.values.get('article_id'))
            add_fav_articles(connection, article_id, session['user_id'])
        elif 'del_fav' in request.form:
            article_id = int(request.values.get('article_id'))
            del_fav_articles(connection, article_id, session['user_id'])
    
    article = get_article(connection, article_id).to_dict('records')[0]
    is_fav = is_favorite(connection, session['user_id'], article_id)

    html = render_template(
        'full_article.html',
        article=article,
        is_fav=is_fav,
        article_back_url=session['article_back_url'],
    )
    
    return html