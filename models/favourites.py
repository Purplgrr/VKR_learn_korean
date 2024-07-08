from pandas import read_sql, concat


def get_fav_theory(connection, user_id):
    return read_sql(
        f'''
            SELECT
                *
            FROM
                user JOIN
                fav_theory USING (user_id) JOIN
                theory USING (theory_id)
            WHERE
                user_id = {user_id}
        ''',
        connection
    )


def get_fav_articles(connection, user_id):
    return read_sql(
        f'''
           SELECT
                *
            FROM
                user JOIN
                fav_article USING (user_id) JOIN
                article USING (article_id)
            WHERE
                user_id = {user_id}
        ''',
        connection
    )


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


def get_fav_voc(connection, user_id):
    return read_sql(
        f'''
            SELECT
                *
            FROM
                fav_vocabulary JOIN
                vocabulary USING (vocabulary_id)
            WHERE
                user_id = {user_id}
        ''',
        connection
    )


def del_fav_articles(connection, article_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            DELETE FROM fav_article 
            WHERE article_id = {article_id} AND user_id = {user_id};
        '''
    )
    connection.commit()


def get_flash_cards(connection, params_type, user_id, vocabulary_ids):
    korean_russian_query = f'''
        SELECT
            korean || transcription AS visible_part,
            russian AS hidden_part
        FROM
            fav_vocabulary JOIN
            vocabulary USING (vocabulary_id)
        WHERE
            user_id = {user_id} AND vocabulary_id IN {vocabulary_ids}
    '''

    russian_korean_query = f'''
        SELECT
            russian AS visible_part,
            korean || transcription AS hidden_part
        FROM
            fav_vocabulary JOIN
            vocabulary USING (vocabulary_id)
        WHERE
            user_id = {user_id} AND vocabulary_id IN {vocabulary_ids}
    '''

    if params_type == 1:
        result = read_sql(korean_russian_query + 'ORDER BY RANDOM()', connection)
    elif params_type == 2:
        result = read_sql(russian_korean_query + 'ORDER BY RANDOM()', connection)
    else:
        result = concat(
            [
                read_sql(korean_russian_query + 'ORDER BY RANDOM()', connection), 
                read_sql(russian_korean_query + 'ORDER BY RANDOM()', connection)
            ], 
            ignore_index=True
        )

    return result


def get_theory_data(conn, theory_id):
    data = read_sql(
        f'''
            SELECT
                *
            FROM
                theory
            WHERE
                theory_id = {theory_id}
        ''',
        conn
    )

    return data.to_dict('records')[0]


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