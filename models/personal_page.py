from pandas import read_sql


def get_user_data(conn, user_login, user_password):
    data = read_sql(
        f'''
            SELECT *
            FROM user
            WHERE user_login = '{user_login}' AND user_password = '{user_password}'
        ''',
        conn
    ).to_dict('records')

    return data

def update_user_name(conn, user_id, user_name):
    conn.execute(
        f'''
            UPDATE user
            SET user_name = '{user_name}'
            WHERE user_id = {user_id}
        '''
    )

    conn.commit()

def update_user_password(conn, user_id, user_password):
    conn.execute(
        f'''
            UPDATE user
            SET user_password = '{user_password}'
            WHERE user_id = {user_id}
        '''
    )

    conn.commit()

def update_user_login(conn, user_id, user_login):
    cursor = conn.cursor()
    cursor.execute(
        f'''
            SELECT
                user_id
            FROM
                user
            WHERE
                user_login = '{user_login}'
        '''
    )

    if cursor.fetchone():
        return False
    
    conn.execute(
        f'''
            UPDATE user
            SET user_login = '{user_login}'
            WHERE user_id = {user_id}
        '''
    )

    return True