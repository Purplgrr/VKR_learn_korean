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