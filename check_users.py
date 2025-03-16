from app import app, db, User

def check_users():
    with app.app_context():
        try:
            users = User.query.all()
            print(f"Количество пользователей: {len(users)}")
            
            if users:
                for user in users:
                    print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
            else:
                print("В базе данных нет пользователей")
                
            # Проверяем, есть ли пользователь с ID 1
            user_1 = User.query.get(1)
            if user_1:
                print(f"Пользователь с ID 1: {user_1.username}, {user_1.email}")
            else:
                print("Пользователь с ID 1 не найден")
                
        except Exception as e:
            print(f"Ошибка при проверке пользователей: {e}")

if __name__ == "__main__":
    check_users() 