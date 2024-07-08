from app import app, DATABASE_NAME
from flask import render_template, request, session, redirect, url_for, flash
from utils import get_db_connection
from models.lessons import *
from models.lesson_page import update_user_lesson
from models.login_page import get_user_data


@app.route('/lessons', methods=['GET', 'POST'])
def lessons():
    conn = get_db_connection(DATABASE_NAME)

    ###################################
    if 'user_id' not in session:
        session['url_for_return'] = request.url
        return redirect(url_for('login_page'))
    ###################################

    lessons_ = get_lessons(conn).to_dict('records')
    unlocked_lessons = list(map(lambda item: item['lesson_id'],
        list(filter(lambda item: item['lesson_id'] <= session.get('lesson_id', 1), lessons_))
    ))

    print(unlocked_lessons)

    lesson_count = get_lesson_count(conn)
    lesson_percentage = round((session.get('lesson_id', 1) / lesson_count) * 100, 2)

    html = render_template(
        'lessons.html',
        lessons_=lessons_,
        lesson_percentage=lesson_percentage,
        unlocked_lessons=unlocked_lessons,
    )
    
    return html

@app.route('/enter_test', methods=['GET', 'POST'])
def enter_test():
    conn = get_db_connection(DATABASE_NAME)

    ###################################
    if 'user_id' not in session:
        session['url_for_return'] = request.url
        return redirect(url_for('login_page'))
    ###################################

    complete_sentence_task =  read_sql(
        f'''
            SELECT
                task_complete_sentence_id,
                complete_sentence_exercise_id,
                sentence,
                GROUP_CONCAT(complete_word_id, ';') AS complete_word_ids,
                GROUP_CONCAT(word, ';') AS words,
                GROUP_CONCAT(is_correct, ';') AS correct_answers
            FROM
                task_complete_sentence_exercise JOIN
                complete_sentence_exercise USING (complete_sentence_exercise_id) JOIN
                complete_sentence_exersice_word USING (complete_sentence_exercise_id) JOIN
                complete_word USING (complete_word_id)
            WHERE
                task_complete_sentence_id = 1
            GROUP BY
                task_complete_sentence_id,
                complete_sentence_exercise_id
        ''',
        conn
    ).to_dict('records')

    completed_sentence_exercise = [item['complete_sentence_exercise_id'] for item in complete_sentence_task]
    completed_words = ['_' for _ in complete_sentence_task]
    
    correct_completed_exercise = []
   
    if request.method == 'POST':
        if 'check_word' in request.form:
            is_correct = int(request.values.get('is_correct'))
            complete_word_id = int(request.values.get('complete_word_id'))
            completed_sentence_exercise = request.values.get('completed_sentence_exercise')
            complete_sentence_exercise_id = int(request.values.get('complete_sentence_exercise_id'))
            completed_words = request.values.get('completed_words').split(';')
            completed_sentence_exercise = list(map(int, completed_sentence_exercise.split(';')))
            completed_words[completed_sentence_exercise.index(complete_sentence_exercise_id)] = request.values.get('check_word')
        if 'check' in request.form:
            completed_sentence_exercise = request.values.get('completed_sentence_exercise')
            completed_sentence_exercise = list(map(int, completed_sentence_exercise.split(';')))

            completed_words = request.values.get('completed_words').split(';')
            for index, complete_sentence_exercise_id in enumerate(completed_sentence_exercise):
                filtered_data = list(filter(lambda item: item['complete_sentence_exercise_id'] == complete_sentence_exercise_id, complete_sentence_task))[0]
                completed_word = completed_words[index]

                exercise_words = filtered_data['words'].split(';')
                is_correct_word = filtered_data['correct_answers'].split(';')

                for word, is_correct in zip(exercise_words, is_correct_word):
                    if int(is_correct) and word == completed_word:
                        correct_completed_exercise.append(complete_sentence_exercise_id)
            
            final_task_score = int((len(correct_completed_exercise) / len(complete_sentence_task)) * get_lesson_count(conn) // 2)
            print(final_task_score)
            update_user_lesson(conn, final_task_score, session.get('user_id', 1))

            user_data = get_user_data(conn, session['user_login'], session['user_password'])
            user_data = user_data[0]
            session['lesson_id'] = user_data['lesson_id']

            flash(f"Ваш результат: {final_task_score}. Вам доступно: {final_task_score if final_task_score > 0 else 1} уроков")

    html = render_template(
        'enter_test.html',
        complete_sentence_task=complete_sentence_task,
        completed_words=';'.join(completed_words),
        correct_completed_exercise=correct_completed_exercise,
        list=list,
        completed_sentence_exercise=';'.join(list(map(str, completed_sentence_exercise))),
        enumerate=enumerate,
    )
    
    return html