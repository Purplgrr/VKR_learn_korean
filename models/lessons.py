from pandas import read_sql


def get_lessons(connection):
    return read_sql(
        '''
           SELECT * FROM lesson
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