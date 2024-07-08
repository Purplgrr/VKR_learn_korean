from pandas import read_sql

def get_lesson_description(conn, lesson_id):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT
                lesson_description
            FROM
                lesson
            WHERE
                lesson_id = {lesson_id}
        '''
    )

    return cursor.fetchone()[0]


def update_user_lesson(conn, lesson_id, user_id):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT
                lesson_id
            FROM
                user
            WHERE
                user_id = {user_id}
        '''
    )
    cur_lesson_id = cursor.fetchone()[0]

    # print(lesson_id + 1, cur_lesson_id)
    if (lesson_id + 1 > cur_lesson_id):
        new_lesson_id = lesson_id + 1
    else:
        new_lesson_id = cur_lesson_id
    
    conn.execute(
        f'''
            UPDATE user
            SET lesson_id = {new_lesson_id}
            WHERE user_id = {user_id}
        '''
    )

    conn.commit()
    return new_lesson_id
    



def get_lesson_short_description(conn, lesson_id):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT
                lesson_short_description
            FROM
                lesson
            WHERE
                lesson_id = {lesson_id}
        '''
    )

    return cursor.fetchone()[0]


def del_theory_fav(connection, user_id, theory_id):
    connection.execute(
        f'''
            DELETE FROM fav_theory
            WHERE
                user_id = {user_id} AND 
                theory_id = {theory_id}
        '''
    )
    connection.commit()

def add_theory_fav(connection, user_id, theory_id):
    connection.execute(
        f'''
            INSERT INTO fav_theory(user_id, theory_id)
            VALUES
                ({user_id}, {theory_id})
        '''
    )
    connection.commit()


def get_fav_theory(connection, task_theory_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                theory_id
            FROM
                task_theory_theory JOIN
                theory USING (theory_id) JOIN
                fav_theory USING (theory_id)
            WHERE
                task_theory_id = {task_theory_id} AND
                user_id = {user_id}
        '''
    )

    result = cursor.fetchall()
    if result:
        result = tuple(map(lambda x: x[0], result))
    
    return result


def get_page_title(connection, lesson_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                lesson_title
            FROM
                lesson
            WHERE
                lesson_id = {lesson_id}
        '''
    )

    return cursor.fetchone()[0]


def get_theory_tasks_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_theory_id,
               'Теоретический материал' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_theory USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_dialogue_tasks_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_dia_id,
               'Диалог' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_dia USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_complete_sentence_tasks_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_complete_sentence_id,
               'Упражнение на завершение предложения' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_complete_sentence USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_missing_word_task_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_missing_word_exercise_id,
               'Упражнение на написание слова по картинке' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_missing_word_exercise USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_complete_dialog_task_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_complete_dialog_id,
               'Упражнение на завершение диалога' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_complete_dialog USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_complete_dialog_task_with_words_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_complete_dialog_with_words_id,
               'Упражнение на завершение диалога с использованием нескольких слов' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_complete_dialog_with_words USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_writing_exercise_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_writing_exercise_id,
               'Упражнение на письмо' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_writing_exercise USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_voc_tasks_in_menu(connection, lesson_id):
    return read_sql(
        f'''
            SELECT
               task_voc_id,
               'Словарь' AS task_category,
               lesson_id 
            FROM
               lesson JOIN
               lesson_task_voc USING (lesson_id) 
            WHERE
               lesson_id = {lesson_id}
        ''',
        connection
    )

def get_task_complete_dialog_dialog(connection, task_complete_dialog_id):
    return read_sql(
        f'''
            SELECT
                complete_dialog_id,
                sentence_A,
                sentence_B,
                nessassary_word,
                time,
                style
            FROM
                task_complete_dialog_dialog JOIN
                complete_dialog USING (complete_dialog_id)
            WHERE
                task_complete_dialog_id = {task_complete_dialog_id}
        ''',
        connection
    )

def get_task_writing_exercise(connection, task_writing_exercise_id):
    return read_sql(
        f'''
            SELECT
                task_writing_exercise_id,
                max_task_score,
                task_description,
                theme,
                style,
                time,
                sentence_count
            FROM
                task_writing_exercise JOIN
                writing_exercise USING (writing_exercise_id)
            WHERE
                task_writing_exercise_id = {task_writing_exercise_id}
        ''',
        connection
    )

def get_task_complete_dialog_with_words_dialog(connection, task_complete_dialog_with_words_id):
    return read_sql(
        f'''
            SELECT
                complete_dialog_with_words_id,
                question,
                nessassary_nouns,
                nessassary_verbs,
                time,
                style
            FROM
                task_complete_dialog_with_words_dialog JOIN
                complete_dialog_with_words USING (complete_dialog_with_words_id)
            WHERE
                task_complete_dialog_with_words_id = {task_complete_dialog_with_words_id}
        ''',
        connection
    )

def get_task_theory_theory(connection, lesson_id, task_theory_id):
    return read_sql(
        f'''
            SELECT
                theory_id,
                theory_content
            FROM
               lesson_task_theory JOIN
               task_theory_theory USING (task_theory_id) JOIN
               theory USING (theory_id)
            WHERE
                lesson_id = {lesson_id} AND
                task_theory_id = {task_theory_id}
        ''',
        connection
    )

def get_task_missing_word_exercise_voc(connection, lesson_id, task_missing_word_exercise_id):
    return read_sql(
        f'''
            SELECT
                vocabulary_id,
                korean
            FROM
               lesson_task_missing_word_exercise JOIN
               task_missing_word_exercise_voc USING (task_missing_word_exercise_id) JOIN
               vocabulary USING (vocabulary_id)
            WHERE
                lesson_id = {lesson_id} AND
                task_missing_word_exercise_id = {task_missing_word_exercise_id}
        ''',
        connection
    )

def get_task_complete_sentence_data(connection, task_complete_sentence_id):
    data = read_sql(
        f'''
            SELECT
                task_description,
                max_task_score
            FROM
                task_complete_sentence
            WHERE
                task_complete_sentence_id = {task_complete_sentence_id}
        ''',
        connection
    ).to_dict('records')

    return data[0]

def get_task_complete_dialog_data(connection, task_complete_dialog_id):
    data = read_sql(
        f'''
            SELECT
                task_description,
                max_task_score
            FROM
                task_complete_dialog
            WHERE
                task_complete_dialog_id = {task_complete_dialog_id}
        ''',
        connection
    ).to_dict('records')

    return data[0]

def get_task_complete_dialog_with_words_data(connection, task_complete_dialog_with_words_id):
    data = read_sql(
        f'''
            SELECT
                task_description,
                max_task_score
            FROM
                task_complete_dialog_with_words
            WHERE
                task_complete_dialog_with_words_id = {task_complete_dialog_with_words_id}
        ''',
        connection
    ).to_dict('records')

    return data[0]


def get_task_complete_sentence_exercise(connection, lesson_id, task_complete_sentence_id):
    return read_sql(
        f'''
            SELECT
                task_complete_sentence_id,
                complete_sentence_exercise_id,
                sentence,
                GROUP_CONCAT(complete_word_id, ';') AS complete_word_ids,
                GROUP_CONCAT(word, ';') AS words,
                GROUP_CONCAT(is_correct, ';') AS correct_answers
            FROM
                lesson_task_complete_sentence JOIN
                task_complete_sentence_exercise USING (task_complete_sentence_id) JOIN
                complete_sentence_exercise USING (complete_sentence_exercise_id) JOIN
                complete_sentence_exersice_word USING (complete_sentence_exercise_id) JOIN
                complete_word USING (complete_word_id)
            WHERE
                lesson_id = {lesson_id} AND
                task_complete_sentence_id = {task_complete_sentence_id}
            GROUP BY
                task_complete_sentence_id,
                complete_sentence_exercise_id
        ''',
        connection
    )

def get_task_dialogue_dialogue(connection, lesson_id, task_dia_id):
    return read_sql(
        f'''
            SELECT
                dialogue_id,
                dialogue_content
            FROM
               lesson_task_dia JOIN
               task_dialogue_dialogue USING (task_dia_id) JOIN
               dialogue USING (dialogue_id)
            WHERE
                lesson_id = {lesson_id} AND
                task_dia_id = {task_dia_id}
        ''',
        connection
    )



def get_voc_task(connection, lesson_id, task_voc_id):
    return read_sql(
        f'''
            SELECT
                vocabulary_id,
                korean,
                transcription,
                russian
            FROM
               lesson_task_voc JOIN
               task_voc_vocabulary USING (task_voc_id) JOIN
               vocabulary USING (vocabulary_id)
            WHERE
                lesson_id = {lesson_id} AND
                task_voc_id = {task_voc_id}
        ''',
        connection
    )


def get_voc_fav(connection, user_id):
    return read_sql(
        f'''
            SELECT
                vocabulary_id
            FROM
                fav_vocabulary
            WHERE
                user_id = {user_id}
        ''',
        connection
    )


def add_voc_fav(connection, user_id, vocabulary_id):
    connection.execute(
        f'''
            INSERT INTO fav_vocabulary(user_id, vocabulary_id)
            VALUES
                ({user_id}, {vocabulary_id})
        '''
    )
    connection.commit()


def del_voc_fav(connection, user_id, vocabulary_id):
    connection.execute(
        f'''
            DELETE FROM fav_vocabulary
            WHERE
                user_id = {user_id} AND 
                vocabulary_id = {vocabulary_id}
        '''
    )
    connection.commit()


def get_task_voc(connection, task_voc_id):
    return read_sql(
        f'''
            SELECT
                *
            FROM
                task_voc
            WHERE
               task_voc_id = {task_voc_id} 
        ''',
        connection
    )

def get_task_theory(connection, task_theory_id):
    return read_sql(
        f'''
            SELECT
                *
            FROM
                task_theory
            WHERE
               task_theory_id = {task_theory_id} 
        ''',
        connection
    )

def get_task_dia(connection, task_dia_id):
    return read_sql(
        f'''
            SELECT
                *
            FROM
                task_dialogue
            WHERE
               task_dia_id = {task_dia_id} 
        ''',
        connection
    )

def get_task_missing_word(connection, task_missing_word_exercise_id):
    return read_sql(
        f'''
            SELECT
                *
            FROM
                task_missing_word_exercise
            WHERE
                task_missing_word_exercise_id = {task_missing_word_exercise_id} 
        ''',
        connection
    )

def get_task_missing_word_exersice_score(connection, task_missing_word_exercise_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_missing_word_exercise_progress
            WHERE
                task_missing_word_exercise_id = {task_missing_word_exercise_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0

def get_task_complete_dialog_score(connection, task_complete_dialog_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_complete_dialog_progress
            WHERE
                task_complete_dialog_id = {task_complete_dialog_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0

def get_task_complete_dialog_with_words_score(connection, task_complete_dialog_with_words_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_complete_dialog_with_words_progress
            WHERE
                task_complete_dialog_with_words_id = {task_complete_dialog_with_words_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0

def get_task_writing_exercise_score(connection, task_writing_exercise_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_writing_exercise_progress
            WHERE
                task_writing_exercise_id = {task_writing_exercise_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0

def get_task_theory_score(connection, task_theory_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_theory_progress
            WHERE
                task_theory_id = {task_theory_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0


def get_task_dia_score(connection, task_dia_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_dia_progress
            WHERE
                task_dia_id = {task_dia_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0


def get_task_voc_score(connection, task_voc_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_voc_progress
            WHERE
                task_voc_id = {task_voc_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0


def get_task_complete_sentence_score(connection, task_complete_sentence_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                user_score
            FROM
                task_complete_sentence_progress
            WHERE
                task_complete_sentence_id = {task_complete_sentence_id} AND
                user_id = {user_id}
        '''
    )
    result = cursor.fetchone()
    return result[0] if result else 0


def update_task_voc_result(connection, user_id, task_voc_id, user_score):
    connection.execute(
        f'''
            UPDATE task_voc_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_voc_id = {task_voc_id};
        '''
    )
    connection.commit()

def update_task_theory_result(connection, user_id, task_theory_id, user_score):
    connection.execute(
        f'''
            UPDATE task_theory_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_theory_id = {task_theory_id};
        '''
    )
    connection.commit()

def update_task_dia_result(connection, user_id, task_dia_id, user_score):
    connection.execute(
        f'''
            UPDATE task_dia_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_dia_id = {task_dia_id};
        '''
    )
    connection.commit()

def update_task_complete_sentence_result(connection, user_id, task_complete_sentence_id, user_score):
    connection.execute(
        f'''
            UPDATE task_complete_sentence_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_complete_sentence_id = {task_complete_sentence_id};
        '''
    )
    connection.commit()

def update_task_complete_dialog_result(connection, user_id, task_complete_dialog_id, user_score):
    connection.execute(
        f'''
            UPDATE task_complete_dialog_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_complete_dialog_id = {task_complete_dialog_id};
        '''
    )
    connection.commit()

def update_task_complete_dialog_with_words_result(connection, user_id, task_complete_dialog_with_words_id, user_score):
    connection.execute(
        f'''
            UPDATE task_complete_dialog_with_words_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_complete_dialog_with_words_id = {task_complete_dialog_with_words_id};
        '''
    )
    connection.commit()

def update_task_writing_exercise_result(connection, user_id, task_writing_exercise_id, user_score):
    connection.execute(
        f'''
            UPDATE task_writing_exercise_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_writing_exercise_id = {task_writing_exercise_id};
        '''
    )
    connection.commit()

def update_task_missing_word_exercise_result(connection, user_id, task_missing_word_exercise_id, user_score):
    connection.execute(
        f'''
            UPDATE task_missing_word_exercise_progress
            SET user_score = {user_score}
            WHERE user_id = {user_id} AND task_missing_word_exercise_id = {task_missing_word_exercise_id};
        '''
    )
    connection.commit()

def get_lesson_max_score(connection, lesson_id):
    return read_sql(
        f'''
            WITH get_task_voc_sum_max_score(task_voc_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_voc USING (lesson_id) LEFT JOIN
                    task_voc USING (task_voc_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            ),
            get_task_theory_sum_max_score(task_theory_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_theory USING (lesson_id) LEFT JOIN
                    task_theory USING (task_theory_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            ),
            get_task_dia_sum_max_score(task_dia_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_dia USING (lesson_id) LEFT JOIN
                    task_dialogue USING (task_dia_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            ),
            get_task_complete_sentence_sum_max_score(task_complete_sentence_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_complete_sentence USING (lesson_id) LEFT JOIN
                    task_complete_sentence USING (task_complete_sentence_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            ),
            get_task_missing_word_exercise_sum_max_score(task_missing_word_exercise_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_missing_word_exercise USING(lesson_id) LEFT JOIN
                    task_missing_word_exercise USING (task_missing_word_exercise_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            ),
            get_task_complete_dialog_sum_max_score(task_complete_dialog_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_complete_dialog USING(lesson_id) LEFT JOIN
                    task_complete_dialog USING (task_complete_dialog_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            ),
            get_task_complete_dialog_with_words_sum_max_score(task_complete_dialog_with_words_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_complete_dialog_with_words USING(lesson_id) LEFT JOIN
                    task_complete_dialog_with_words USING (task_complete_dialog_with_words_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            ),
            get_task_writing_exercise_sum_max_score(task_writing_exercise_sum_max_score)
            AS (
                SELECT
                    SUM(max_task_score)
                FROM
                    lesson LEFT JOIN
                    lesson_task_writing_exercise USING(lesson_id) LEFT JOIN
                    task_writing_exercise USING (task_writing_exercise_id)
                WHERE
                    lesson_id = {lesson_id}
                GROUP BY
                    lesson_id
            )

            
            SELECT
                IFNULL(task_voc_sum_max_score, 0) + 
                IFNULL(task_theory_sum_max_score, 0) + 
                IFNULL(task_dia_sum_max_score, 0) + 
                IFNULL(task_complete_sentence_sum_max_score, 0) + 
                IFNULL(task_missing_word_exercise_sum_max_score, 0) +
                IFNULL(task_complete_dialog_sum_max_score, 0) +
                IFNULL(task_complete_dialog_with_words_sum_max_score, 0) + 
                IFNULL(task_writing_exercise_sum_max_score, 0) AS lesson_max_score
            FROM
                get_task_voc_sum_max_score,
                get_task_theory_sum_max_score,
                get_task_dia_sum_max_score, 
                get_task_complete_sentence_sum_max_score,
                get_task_missing_word_exercise_sum_max_score,
                get_task_complete_dialog_sum_max_score,
                get_task_complete_dialog_with_words_sum_max_score,
                get_task_writing_exercise_sum_max_score
        ''',
        connection
    )


def get_lesson_user_score(connection, user_id, lesson_id):
    return read_sql(
        f'''
            WITH get_task_voc_sum_user_score(lesson_id, task_voc_sum_user_score)
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_voc ON lesson.lesson_id = lesson_task_voc.lesson_id LEFT JOIN
                    task_voc_progress ON lesson_task_voc.task_voc_id = task_voc_progress.task_voc_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            ),
            get_task_theory_sum_user_score(lesson_id, task_theory_sum_user_score)  
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_theory ON lesson.lesson_id = lesson_task_theory.lesson_id LEFT JOIN
                    task_theory_progress ON lesson_task_theory.task_theory_id = task_theory_progress.task_theory_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            ),
            get_task_dia_sum_user_score(lesson_id, task_dia_sum_user_score)  
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_dia ON lesson.lesson_id = lesson_task_dia.lesson_id LEFT JOIN
                    task_dia_progress ON task_dia_progress.task_dia_id = lesson_task_dia.task_dia_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            ),
            get_task_complete_sentence_sum_user_score(lesson_id, task_complete_sentence_sum_user_score)
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_complete_sentence ON lesson.lesson_id = lesson_task_complete_sentence.lesson_id LEFT JOIN
                    task_complete_sentence_progress ON task_complete_sentence_progress.task_complete_sentence_id = lesson_task_complete_sentence.task_complete_sentence_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            ),
            get_task_missing_word_exercise_sum_user_score(lesson_id, task_missing_word_exercise_sum_user_score)
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_missing_word_exercise ON lesson.lesson_id = lesson_task_missing_word_exercise.lesson_id LEFT JOIN
                    task_missing_word_exercise_progress ON lesson_task_missing_word_exercise.task_missing_word_exercise_id = task_missing_word_exercise_progress.task_missing_word_exercise_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            ),
            get_task_complete_dialog_sum_user_score(lesson_id, task_complete_dialog_sum_user_score)
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_complete_dialog ON lesson.lesson_id = lesson_task_complete_dialog.lesson_id LEFT JOIN
                    task_complete_dialog_progress ON task_complete_dialog_progress.task_complete_dialog_id = lesson_task_complete_dialog.task_complete_dialog_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            ),
            get_task_complete_dialog_with_words_sum_user_score(lesson_id, task_complete_dialog_with_words_sum_user_score)
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_complete_dialog_with_words ON lesson.lesson_id = lesson_task_complete_dialog_with_words.lesson_id LEFT JOIN
                    task_complete_dialog_with_words_progress ON lesson_task_complete_dialog_with_words.task_complete_dialog_with_words_id = task_complete_dialog_with_words_progress.task_complete_dialog_with_words_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            ),
            get_task_writing_exercise_sum_user_score(lesson_id, task_writing_exercise_sum_user_score)
            AS (
                SELECT
                    lesson.lesson_id,
                    SUM(user_score)
                FROM
                    user JOIN
                    lesson LEFT JOIN
                    lesson_task_writing_exercise ON lesson.lesson_id = lesson_task_writing_exercise.lesson_id LEFT JOIN
                    task_writing_exercise_progress ON lesson_task_writing_exercise.task_writing_exercise_id = task_writing_exercise_progress.task_writing_exercise_id
                WHERE
                    lesson.lesson_id = {lesson_id} AND
                    user.user_id = {user_id}
                GROUP BY
                    lesson.lesson_id
            )

            SELECT
                IFNULL(task_theory_sum_user_score, 0) + 
                IFNULL(task_voc_sum_user_score, 0) + 
                IFNULL(task_dia_sum_user_score, 0) + 
                IFNULL(task_complete_sentence_sum_user_score, 0) + 
                IFNULL(task_missing_word_exercise_sum_user_score, 0) +
                IFNULL(task_complete_dialog_sum_user_score, 0) +
                IFNULL(task_complete_dialog_with_words_sum_user_score, 0) + 
                IFNULL(task_writing_exercise_sum_user_score, 0) AS lesson_user_score
            FROM
                get_task_voc_sum_user_score LEFT JOIN
                get_task_theory_sum_user_score USING (lesson_id) LEFT JOIN  
                get_task_dia_sum_user_score USING (lesson_id) LEFT JOIN  
                get_task_complete_sentence_sum_user_score USING (lesson_id) LEFT JOIN  
                get_task_missing_word_exercise_sum_user_score USING (lesson_id) LEFT JOIN  
                get_task_complete_dialog_sum_user_score USING (lesson_id) LEFT JOIN  
                get_task_complete_dialog_with_words_sum_user_score USING (lesson_id) LEFT JOIN  
                get_task_writing_exercise_sum_user_score USING (lesson_id)
        ''',
        connection
    )