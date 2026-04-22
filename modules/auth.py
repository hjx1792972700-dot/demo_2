import hashlib
import os
import sys
import sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from database.db_manager import DBManager
from database.models import hash_password


class AuthModule:
    _current_user = None
    
    @classmethod
    def login(cls, username, password):
        db = DBManager()
        hashed_password = hash_password(password)
        
        users = db.execute_query(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, hashed_password)
        )
        
        if len(users) > 0:
            cls._current_user = dict(users[0])
            return True, cls._current_user
        return False, None
    
    @classmethod
    def logout(cls):
        cls._current_user = None
    
    @classmethod
    def get_current_user(cls):
        return cls._current_user
    
    @classmethod
    def check_permission(cls, required_role):
        if cls._current_user is None:
            return False
        
        user_role = cls._current_user.get('role', '')
        
        if user_role == config.ROLE_ADMIN:
            return True
        
        if user_role == config.ROLE_MANAGER:
            return required_role in [config.ROLE_MANAGER, config.ROLE_EMPLOYEE]
        
        if user_role == config.ROLE_EMPLOYEE:
            return required_role == config.ROLE_EMPLOYEE
        
        return False
    
    @staticmethod
    def create_user(user_data):
        db = DBManager()
        try:
            hashed_password = hash_password(user_data.get('password', '123456'))
            user_id = db.execute_query(
                '''
                INSERT INTO users (username, password, role, email, phone)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    user_data['username'],
                    hashed_password,
                    user_data.get('role', config.ROLE_EMPLOYEE),
                    user_data.get('email', ''),
                    user_data.get('phone', '')
                ),
                commit=True
            )
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def update_user(user_id, user_data):
        db = DBManager()
        fields = []
        params = []
        
        if 'username' in user_data:
            fields.append("username = ?")
            params.append(user_data['username'])
        
        if 'password' in user_data:
            fields.append("password = ?")
            params.append(hash_password(user_data['password']))
        
        if 'role' in user_data:
            fields.append("role = ?")
            params.append(user_data['role'])
        
        if 'email' in user_data:
            fields.append("email = ?")
            params.append(user_data['email'])
        
        if 'phone' in user_data:
            fields.append("phone = ?")
            params.append(user_data['phone'])
        
        if not fields:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        
        db.execute_query(query, params, commit=True)
        return True
    
    @staticmethod
    def delete_user(user_id):
        db = DBManager()
        db.execute_query("DELETE FROM users WHERE id = ?", (user_id,), commit=True)
        return True
    
    @staticmethod
    def get_user_by_id(user_id):
        db = DBManager()
        users = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
        if users:
            return dict(users[0])
        return None
    
    @staticmethod
    def get_all_users():
        db = DBManager()
        users = db.execute_query("SELECT * FROM users ORDER BY id")
        return [dict(u) for u in users]
