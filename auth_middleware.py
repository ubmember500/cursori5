# Этот файл содержит middleware для проверки аутентификации пользователя
from flask import g, session, request, redirect, url_for
from functools import wraps

def load_logged_in_user():
    """
    Middleware функция, которая загружает информацию о пользователе
    из сессии и делает ее доступной через g.user
    """
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        # Импортируем User здесь, чтобы избежать циклических импортов
        from models import User
        g.user = User.query.get(user_id)

def login_required(view):
    """
    Декоратор для маршрутов, которые требуют авторизации
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return view(**kwargs)
    return wrapped_view 