from flask import Flask, url_for, request
import os
from sqlite3 import OperationalError
from utils import db_init, get_db_connection
# from task import *

DATABASE_NAME = 'db.sqlite'
DB_DUMP_PATH = 'db.txt'

app = Flask(__name__)
app.secret_key = 'MARINA'

import controllers.index
import controllers.articles
import controllers.chat
import controllers.favourites
import controllers.lessons
import controllers.personal_page
import controllers.lesson_page
import controllers.login_page

if __name__ == '__main__':
    if not os.path.exists(DATABASE_NAME):
        connection = get_db_connection(DATABASE_NAME)
        cursor = connection.cursor()

        try:
            db_init(DB_DUMP_PATH, cursor)
            cursor.executescript(
                '''
                    INSERT INTO task_theory_progress (task_theory_id, user_id, user_score)
                    SELECT task_theory_id, user_id, 0
                    FROM (SELECT task_theory_id, user_id FROM task_theory JOIN user);

                    INSERT INTO task_voc_progress (task_voc_id, user_id, user_score)
                    SELECT task_voc_id, user_id, 0
                    FROM (SELECT task_voc_id, user_id FROM task_voc JOIN user);

                    INSERT INTO task_dia_progress (task_dia_id, user_id, user_score)
                    SELECT task_dia_id, user_id, 0
                    FROM (SELECT task_dia_id, user_id FROM task_dialogue JOIN user);

                    INSERT INTO task_complete_sentence_progress (task_complete_sentence_id, user_id, user_score)
                    SELECT task_complete_sentence_id, user_id, 0
                    FROM (SELECT task_complete_sentence_id, user_id FROM task_complete_sentence JOIN user);

                    INSERT INTO task_missing_word_exercise_progress (task_missing_word_exercise_id, user_id, user_score)
                    SELECT task_missing_word_exercise_id, user_id, 0
                    FROM (SELECT task_missing_word_exercise_id, user_id FROM task_missing_word_exercise JOIN user);

                    INSERT INTO task_complete_dialog_progress (task_complete_dialog_id, user_id, user_score)
                    SELECT task_complete_dialog_id, user_id, 0
                    FROM (SELECT task_complete_dialog_id, user_id FROM task_complete_dialog JOIN user);

                    INSERT INTO task_complete_dialog_with_words_progress (task_complete_dialog_with_words_id, user_id, user_score)
                    SELECT task_complete_dialog_with_words_id, user_id, 0
                    FROM (SELECT task_complete_dialog_with_words_id, user_id FROM task_complete_dialog_with_words JOIN user);

                    INSERT INTO task_writing_exercise_progress (task_writing_exercise_id, user_id, user_score)
                    SELECT task_writing_exercise_id, user_id, 0
                    FROM (SELECT task_writing_exercise_id, user_id FROM task_writing_exercise JOIN user);
                '''
            )
        except OperationalError as db_error:
            print(db_error)
        connection.commit()

    # test = CompleteDialog(
    #     u'샤키라는 스페인 사람이에요?',
    #     u'아니요, 샤키라는 스페인 서람에요.',
    #     [WordPart(word_part, name) for word_part, name in komoran.pos('샤키라')]
    # )

    # test.check()

    