import sqlite3
import os
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    url_for,
    session
)
import models.post
import models.users

app = Flask(__name__)
app.secret_key = "nuggets123"
app.config['UPLOAD_FOLDER'] = 'static/upload_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET','POST'])
def get_main():
    connection = sqlite3.connect("post.db")
    cursor = connection.cursor()
    cursor.execute(" SELECT * FROM post ")
    posts = cursor.fetchall()
    connection.commit()
    connection.close()
    return render_template('base.html', posts = posts)

@app.route('/profile', methods=['GET','POST'])
def get_profile():
    name = session.get("login", "")
    return render_template('profile.html', name = name)

@app.route('/create_post', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        image_file = request.files['image']
        filename = None

        if image_file:
            filename = image_file.filename
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('post.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO post (title, description, price, image)
            VALUES (?, ?, ?, ?)
        """, (title, description, price, f"upload_images/{filename}"))

        conn.commit()
        conn.close()

        return redirect(url_for('get_main'))  

    return render_template('create_post.html')

@app.route('/log', methods=['GET', 'POST'])
def get_log():
    if request.method == 'POST':
        login = request.form.get('login', type=str)
        password = request.form.get('password', type=str)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["login"] = user[1]
            return redirect(url_for('get_main'))
        else:
            error_message = "Неверный логин или пароль"
            return render_template('log.html', error=error_message)

    return render_template('log.html')

@app.route('/reg', methods=['GET','POST'])
def get_reg():
    if request.method == 'POST':
        login = request.form.get('login', type=str)
        email = request.form.get('email', type=str)
        password = request.form.get('password', type=str)
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users (login, email, password) VALUES (?, ?, ?)', (login, email, password))
        session["login"] = login
        conn.commit()
        conn.close()
        return redirect(url_for('get_main'))

    return render_template('reg.html')

@app.route("/logout", methods=["GET", "POST"])
def log_out():
    session.pop("login", None)
    return redirect(url_for("get_main"))

@app.route("/ascending", methods=["GET", "POST"])
def order_ascending():
    connection = sqlite3.connect("post.db")
    posts_sorted = []
    cursor = connection.cursor()
    cursor.execute(" SELECT price, id FROM post ")
    posts = cursor.fetchall()
    arr_sorted = sorted(posts)
    for i in arr_sorted:
        cursor.execute('SELECT * FROM post WHERE id = ?', (i[1],))
        posts = cursor.fetchone()
        posts_sorted.append(posts)
    connection.close()
    return render_template("base.html", posts=posts_sorted)

@app.route("/descending", methods=["GET", "POST"])
def order_descending():
    connection = sqlite3.connect("post.db")
    posts_sorted = []
    cursor = connection.cursor()
    cursor.execute(" SELECT price, id FROM post ")
    posts = cursor.fetchall()
    arr_sorted = sorted(posts, reverse=True)
    for i in arr_sorted:
        cursor.execute('SELECT * FROM post WHERE id = ?', (i[1],))
        posts = cursor.fetchone()
        posts_sorted.append(posts)
    connection.close()
    return render_template("base.html", posts=posts_sorted)

# @app.route("/up", methods=["GET", "POST"])
# def get_up():
#     conn = sqlite3.connect("post.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM post ORDER BY price")
#     posts = cursor.fetchall()
#     conn.close()
#     return render_template("base.html", posts=posts)

# @app.route("/down", methods=["GET", "POST"])
# def get_down():
#     conn = sqlite3.connect("post.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM post ORDER BY price DESC")
#     posts = cursor.fetchall()
#     conn.close()
#     return render_template("base.html", posts=posts)

@app.route("/post/<int:id>", methods=["GET", "POST"])
def get_details(id):
    connection = sqlite3.connect("post.db")
    cursor = connection.cursor()
    cursor.execute(" SELECT * FROM post WHERE id = ?", (id,))
    post = cursor.fetchone()
    connection.close()
    return render_template("post.html", post = post)

@app.route("/results", methods=["GET", "POST"])
def search_results():
    search_request = request.form.get('search_request', type=str)
    print(search_request)
    if search_request:
        connection = sqlite3.connect("post.db")
        cursor = connection.cursor()
        cursor.execute(" SELECT title, id FROM post ")
        posts = cursor.fetchall()
        posts_catched = []
        for i in posts:
            if search_request in i[0]:
                cursor.execute('SELECT * FROM post WHERE id = ?', (i[1],))
                posts = cursor.fetchone()
                posts_catched.append(posts)
        connection.close()
        return render_template("search_results.html", posts = posts_catched)
    return render_template("base.html")


if __name__ == '__main__':
    models.post.create_post_db()
    models.users.create_users_db()
    app.run(debug=True)