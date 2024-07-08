from pandas import read_sql


def get_articles(connection, article_category_id):
    return read_sql(
        f'''
           SELECT 
               *
           FROM 
               article
           WHERE 
               article_category_id={article_category_id}
        ''',
        connection
    )

def get_fav_articles(connection, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                article_id
            FROM
                fav_article
            WHERE
                user_id = {user_id}
        '''
    )

    return list(map(lambda x: x[0], cursor.fetchall()))
    
def add_fav_articles(connection, article_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            INSERT INTO fav_article (article_id, user_id) 
            VALUES ({article_id}, {user_id});
        '''
    )
    connection.commit()

def del_fav_articles(connection, article_id, user_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            DELETE FROM fav_article 
            WHERE article_id = {article_id} AND user_id = {user_id};
        '''
    )
    connection.commit()

def get_article(connection, article_id):
    return read_sql(
        f'''
            SELECT
                *
            FROM
                article
            WHERE
                article_id = {article_id}
        ''',
        connection
    )

def is_favorite(connection, user_id, article_id):
    cursor = connection.cursor()
    cursor.execute(
        f'''
            SELECT
                *
            FROM
                article JOIN
                fav_article USING (article_id)
            WHERE
                user_id = {user_id} AND
                article_id = {article_id}
        '''
    )

    return bool(cursor.fetchone())