import sqlite3
import os
from datetime import datetime
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class DBManager:
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self):
        if self._connection is None:
            if not os.path.exists(config.DATA_DIR):
                os.makedirs(config.DATA_DIR)
            self._connection = sqlite3.connect(config.DB_PATH, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close_connection(self):
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute_query(self, query, params=None, commit=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if commit:
                conn.commit()
                return cursor.lastrowid
            else:
                return cursor.fetchall()
        except Exception as e:
            if commit:
                conn.rollback()
            raise e
    
    def execute_script(self, script):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executescript(script)
        conn.commit()
