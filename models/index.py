from pandas import read_sql


def get_words(conn, user_id):
    return read_sql(
        f'''
            WITH get_user_words(vocabulary_id, korean, russian, transcription)
            AS (
                SELECT
                    vocabulary_id, 
                    korean, 
                    russian, 
                    transcription
                FROM
                    vocabulary JOIN
                    fav_vocabulary USING (vocabulary_id)
                WHERE
                    user_id = {user_id}
            )

            SELECT
                vocabulary_id, 
                korean, 
                russian, 
                transcription,
                {user_id} AS user_id
            FROM 
                get_user_words
            UNION
            SELECT
                vocabulary_id, 
                korean, 
                russian, 
                transcription,
                '' AS user_id
            FROM
                vocabulary
            WHERE
                vocabulary_id NOT IN (
                    SELECT
                        vocabulary_id
                    FROM
                        get_user_words
                )
        ''',
        conn
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


def get_lesson_data(conn, lesson_id):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT
                lesson_title,
                lesson_short_description
            FROM
                lesson
            WHERE
                lesson_id = {lesson_id}
        '''
    )

    return cursor.fetchone()


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


def get_lesson_count(conn):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT  
                COUNT(lesson_id)
            FROM
                lesson
        '''
    )

    return cursor.fetchone()[0]
