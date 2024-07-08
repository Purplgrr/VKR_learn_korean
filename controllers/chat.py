from app import app
from flask import render_template, request
# from utils import get_db_connection

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # conn = get_db_connection()

    html = render_template(
        'chat.html'
    )
    
    return html