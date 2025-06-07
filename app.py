from flask import Flask, jsonify, g, request, render_template, url_for, redirect
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'db'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB', 'localdevdb'),
            user=os.getenv('POSTGRES_USER', 'root'),
            password=os.getenv('POSTGRES_PASSWORD', 'root')
        )
    return g.db_conn

@app.teardown_appcontext
def close_db_connection(exception):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

@app.get('/rows')
def get_users():
    conn = get_db_connection()
    curr = conn.cursor()
    curr.execute('SELECT * FROM IDENTITY;')
    rows = curr.fetchall()
    curr.close()

    # results = []
    # for row in rows :
    #     results.append({
    #         'id': row[0],
    #         'first_name' : row[1],
    #         'last_name' : row[2]
    #     })
    return render_template('index.html', rows=rows)

@app.route('/add', methods=['GET','POST'])
def post_user() :
    if request.method == 'POST':
        id = request.form['id']
        f_name = request.form['first_name']
        l_name = request.form['last_name']
        conn = get_db_connection()
        curr = conn.cursor()
        try:
            curr.execute(
                'INSERT INTO identity (id, first_name, last_name) VALUES (%s, %s, %s)',
                (id, f_name, l_name)
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            return "Error in insertion", 400
        finally:
            curr.close()

        return redirect(url_for('get_users'))

    return render_template('add.html')




if __name__ == '__main__' :
    app.run(port=5000)
