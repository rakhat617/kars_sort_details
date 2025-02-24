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
import models.post # Импортирую функции которые создают датабазу, если ее нет (вызов на строке 194)
import models.users

app = Flask(__name__) 
app.secret_key = "nuggets123" # Ключ для сессии
app.config['UPLOAD_FOLDER'] = 'static/upload_images' # Путь куда картинки загруженные сохранять и откуда доставать
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Это на случай если вдруг нужной папки для картинок нет

@app.route('/', methods=['GET','POST']) # Главная страница
def get_main():
    connection = sqlite3.connect("post.db") # Тут просто чтобы на главной всегда отображалось все что есть в датабазе
    cursor = connection.cursor()
    cursor.execute(" SELECT * FROM post ")
    posts = cursor.fetchall()
    connection.commit()
    connection.close()
    return render_template('base.html', posts = posts)

@app.route('/profile', methods=['GET','POST']) # Страница профиля
def get_profile():
    name = session.get("login", "") # Это чтоб в профиле показывалось имя (логин) человека который сейчас в сессии
    return render_template('profile.html', name = name)

@app.route('/create_post', methods=['GET', 'POST']) # Страница создания поста
def create():
    if request.method == 'POST': # Эта штука нужна чтобы все что внутри сработало только после того как мы нажмем на кнопку (связано с 58 строкой)
        title = request.form['title'] # Тут мы просто берем все данные которые вписал юзер и сохраняем их в переменные
        description = request.form['description']
        price = request.form['price']
        image_file = request.files['image']
        filename = None # Создаем переменную для названия файла картинки.
        # Т.к. загрузка картинки не обязательна, может случиться так, что картинки вообще нет
        # И как раз для такого случая мы создаем эту переменную заранее, в которой лежит НИЧЕГО
        # Чтобы у нас строка 53 не выдавала ошибку
        if image_file: # Тут мы чекаем загружена ли какая-то картинка, если да, то
            filename = image_file.filename # Сохраняем название файла в переменную
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # И сохраняем сам файл в указанную папку (строка 16)
        conn = sqlite3.connect('post.db') # Ну тут просто запихиваем все данные в датабазу
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO post (title, description, price, image)
            VALUES (?, ?, ?, ?)
        """, (title, description, price, f"upload_images/{filename}"))
        conn.commit()
        conn.close()
        return redirect(url_for('get_main'))  # И автоматически возвращаемся на главную страницу
    # Именно редирект, чтобы функция гетмейн сработала и обновилась со всеми только что сохраненными данными
    return render_template('create_post.html') # Здесь мы пишем ссылку на хтмл именно этой страницы, чтобы мы оставались на ней пока не нажмем на кнопку

@app.route('/log', methods=['GET', 'POST']) # Страница авторизации
def get_log():
    if request.method == 'POST': # Та же логика что и в предыдущей функции
        login = request.form.get('login', type=str) # Забираем все данные с инпута
        password = request.form.get('password', type=str)
        conn = sqlite3.connect('users.db') # Открываем датабазу чтоб найти юзера с такими логином и паролем
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password)) # Собственно, ищем
        user = cursor.fetchone()
        conn.close()
        if user: # Если нашли такого юзера, то 
            session["login"] = user[1] # Открывается сессия
            return redirect(url_for('get_main')) # И автоматически перекидывает на главную (хотя логичнее наверное здесь перекидывать на профиль, ну пофиг)
        else: # А это если не был найдет такой чел
            error_message = "Неверный логин или пароль" # Передаем сообщение об ошибке
            return render_template('log.html', error=error_message) # И заново открывается страница логина, но уже с этим сообщением
    return render_template('log.html') # Та же логика что и в предыдущей функции

@app.route('/reg', methods=['GET','POST']) # Страница регистрации
def get_reg():
    if request.method == 'POST': # Та же логика что и в предыдущей функции
        login = request.form.get('login', type=str) # Забираем все данные с инпута
        email = request.form.get('email', type=str)
        password = request.form.get('password', type=str)
        password_confirm = request.form.get('password_confirm', type=str)
        if password == password_confirm: # Если пароли совпадают, то регистрация успешна, и все данные сохраняются в датабазу
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (login, email, password) VALUES (?, ?, ?)', (login, email, password))
            session["login"] = login # Также, открывается сессия
            conn.commit()
            conn.close()
            return redirect(url_for('get_main')) # И перекидывается на главную
        else: # Если пароли не совпадают, то
            error_message = "Пароли не совпадают" # Передаем сообщение об ошибке
            return render_template('reg.html', error=error_message) # И заново открывается страница регистрации, но уже с этим сообщением
    return render_template('reg.html') # Та же логика что и в предыдущей функции

@app.route("/logout", methods=["GET", "POST"]) # Функция завершения сессии (выход из учетной записи)
def log_out():
    session.pop("login", None)
    return redirect(url_for("get_main"))

@app.route("/ascending", methods=["GET", "POST"]) # Функция сортровки по возрастанию (от малого к большому), питоновским путем
def order_ascending():
    connection = sqlite3.connect("post.db") # Открываем нашу датабазу
    cursor = connection.cursor()
    cursor.execute(" SELECT price, id FROM post ") # Берем тольео цены и айди (важно что цены именно первыми ставим)
    posts = cursor.fetchall() # Теперь у нас создался список из котрежей (цена, айди), то есть [(цена0, айди0), (цена1, айди1), и так далее]
    arr_sorted = sorted(posts) # Эта функция может сортировать список состоящий даже из кортежей
    # но по дефолту он смотрит только на первое значение (нулевой индекс) каждого кортежа (в нашем случае цена)
    posts_sorted = [] # создаем пустой массив чтобы потом туда апендить кортежи (отсортированные), но уже со всеми данными (не только цена и айди)
    for i in arr_sorted:
        cursor.execute('SELECT * FROM post WHERE id = ?', (i[1],)) # Вот теперь ясно зачем мы брали не только цену, но и айди
        # потому что именно по айди мы теперь по очереди аппендим в итоговый массив
        # Иначе у нас бы посты с одинаковой ценой не сохранялись все, а только первый
        posts = cursor.fetchone()
        posts_sorted.append(posts)
    connection.close()
    return render_template("base.html", posts=posts_sorted) # тут важно именно рендерить страницу, а не редайректить на ее функцию 
    # потому что если вызовем заново функцию гетмейн, то у нас заново отобразиться без сортировки. И нафига мы тогда все это делали?

@app.route("/descending", methods=["GET", "POST"]) # Функция сортировки по убыванию. Абсолютно тоже самое кроме 129 строки
def order_descending():
    connection = sqlite3.connect("post.db")
    posts_sorted = []
    cursor = connection.cursor()
    cursor.execute(" SELECT price, id FROM post ")
    posts = cursor.fetchall()
    arr_sorted = sorted(posts, reverse=True) # Тут просто добавили аргумент чтобы он сортировал наоборот
    for i in arr_sorted:
        cursor.execute('SELECT * FROM post WHERE id = ?', (i[1],))
        posts = cursor.fetchone()
        posts_sorted.append(posts)
    connection.close()
    return render_template("base.html", posts=posts_sorted)

# Это функции сортировки эс-кью-эль-евским путем, но так как я сам додумался до питоновского, я буду его юзать. А это просто оставил на всякий

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

@app.route("/post/<int:id>", methods=["GET", "POST"]) # Страница отдельного поста, с его описанием. Тут передаем айди поста прямо в ЮРЛ страницы
def get_details(id):
    connection = sqlite3.connect("post.db")
    cursor = connection.cursor()
    cursor.execute(" SELECT * FROM post WHERE id = ?", (id,)) # Так как мы передали в эту функцию айди поста, мы его можем легко выцепить из датабазы по айди
    post = cursor.fetchone() # Ну тут все ясно понятно, сто раз видели
    connection.close()
    return render_template("post.html", post = post)

@app.route("/search", methods=["GET", "POST"]) # Это пред-функция поиска
def search(): # Почему "пред"? Потому что ее единственный смысл просто передать поисковой запрос в уже настоящую функцию
    # Это делается затем, чтобы на странице с результатом поиска в ЮРЛе был написан этот самый запрос
    if request.method == 'POST':
        search_query = request.form["search_request"] # Тут вот получаем запрос юзера который он в инпут поиска ввел
        if search_query: # Ну и также здесь мы проверяем есть ли вообще какой-то запрос (если пустой, ничего не происходит)
            return redirect(url_for("search_results", query=search_query)) # А если не пустой, то запускаем уже настоящую функцию, и передаем туда запрос
    return redirect(url_for("get_main"))

@app.route("/results/<query>", methods=["GET", "POST"]) # Вот она настоящая страница с результатами поиска, ЮРЛ которой содержит в себе запрос
def search_results(query): # Логика у этой функции в принципе идентична логике моих функций сортировок
    connection = sqlite3.connect("post.db") # Тут мы соединяемся с датабазой
    cursor = connection.cursor()
    cursor.execute(" SELECT title, id FROM post ") # И забираем все названия и айди 
    posts = cursor.fetchall()
    posts_catched = [] # Создаем пустой массив, в который будем апендить все посты что совпали с запросом
    for i in posts: # Итерируем по всем постам
        if query.lower() in i[0].lower(): # И чекаем название каждого поста с запросом. И заметьте, что тут не строгий поиск
            # То есть тут достаточно чтобы название поста ВКЛЮЧАЛО в себя запрос, а также наплевать на регистр
            # Но не наплевать на опечатки и ошибки, но тут нужны будут какието тяжкие алгоритмы, даже яндекс не справляется, кек
            cursor.execute('SELECT * FROM post WHERE id = ?', (i[1],)) # Отбираем по айди все данные из совпавшего поста
            posts = cursor.fetchone()
            posts_catched.append(posts) # И аппендим этот пост к массиву совпавших постов
    connection.close()
    return render_template("search_results.html", posts = posts_catched)


if __name__ == '__main__':
    models.post.create_post_db() # Тут запускаем функцию по созданию датабаз (на случай если их нет)
    models.users.create_users_db()
    app.run(debug=True)