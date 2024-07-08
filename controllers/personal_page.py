from app import app, DATABASE_NAME
from flask import render_template, request, session, redirect, url_for, flash
from utils import get_db_connection
from models.personal_page import *


@app.route('/personal_page', methods=['GET', 'POST'])
def personal_page():
    conn = get_db_connection(DATABASE_NAME)

    if 'user_id' not in session:
        session['url_for_return'] = request.url
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        if 'exit' in request.form:
            session.pop('user_id', None)
            session.pop('lesson_id', None)
            session.pop('user_name', None)
            session.pop('user_login', None)
            session.pop('user_password', None)
            
            return redirect(url_for('login_page'))
        if 'save' in request.form:
            new_user_name = request.values.get('user_name')
            new_user_login = request.values.get('user_login')
            new_user_password = request.values.get('user_password')

            update_user_name(conn, session['user_id'], new_user_name)
            update_user_password(conn, session['user_id'], new_user_password)

            is_login_updated = update_user_login(conn, session['user_id'], new_user_login)
            if not is_login_updated:
                if new_user_login != session['user_login']:
                    flash('Пользователь с таким логином уже есть в системе!')
            flash('Данные о пароле и имени пользователя сохранены!')

            user_data = get_user_data(
                conn, 
                session['user_login'] if not is_login_updated else new_user_login, 
                new_user_password
            )
            user_data = user_data[0]
            session['user_id'] = user_data['user_id']
            session['lesson_id'] = user_data['lesson_id']
            session['user_name'] = user_data['user_name']
            session['user_login'] = user_data['user_login']
            session['user_password'] = user_data['user_password']

    html = render_template(
        'personal_page.html'
    )
    
    return html