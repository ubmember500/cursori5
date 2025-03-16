from app import app, db, User

with app.app_context():
    print("Список всех пользователей:")
    users = User.query.all()
    if not users:
        print("Пользователей в базе данных нет")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}") 