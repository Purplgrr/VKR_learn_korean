from sqlite3 import connect


def get_db_connection(database_name):
    return connect(database_name)


def db_init(dump_path, cursor):
    with open(dump_path, 'r', encoding='UTF-8') as input_file:
        dump = input_file.read()

    cursor.executescript(dump)


pictures = {
    15: '/static/images/watch.jpg',
    13: '/static/images/hat.jpg',
    14: '/static/images/singer.png',
}

complete_sentence_picture = {
    1: '/static/images/3rd_lesson.png',
    2: '/static/images/3rd_lesson.png',
    3: '/static/images/3rd_lesson.png',
    4: '/static/images/3rd_lesson.png',
    5: '/static/images/3rd_lesson.png',
}