from app import app, DATABASE_NAME
from flask import render_template, request, session, flash, redirect, url_for
from utils import get_db_connection
from models.login_page import *


@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    conn = get_db_connection(DATABASE_NAME)

    if request.method == 'POST':
        if 'login' in request.form:
            user_login = request.values.get('user_login')
            user_password = request.values.get('user_password')

            user_data = get_user_data(conn, user_login, user_password)
            if not user_data:
                flash('Неверный логин или пароль')
            else:
                user_data = user_data[0]
                session['user_id'] = user_data['user_id']
                session['lesson_id'] = user_data['lesson_id']
                session['user_name'] = user_data['user_name']
                session['user_login'] = user_data['user_login']
                session['user_password'] = user_data['user_password']

                return redirect(session.get('url_for_return', '/'))

    html = render_template(
        'login_page.html',
    )
    
    return html