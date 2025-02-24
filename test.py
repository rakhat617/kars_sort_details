import sqlite3

search_request = "Roronoa"
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
print(posts_catched)
connection.close()
