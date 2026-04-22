import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from modules.auth import AuthModule


class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.root = tk.Tk()
        self.root.title("ERP系统 - 登录")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        self.root.geometry(f"400x300+{x}+{y}")
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Python ERP 系统", font=('微软雅黑', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="登录", font=('微软雅黑', 12)).pack(pady=(0, 15))
        
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)
        ttk.Label(username_frame, text="用户名:", width=8").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame, font=('微软雅黑', 10), width=25)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        self.username_entry.insert(0, 'admin')
        
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        ttk.Label(password_frame, text="密  码:", width=8).pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(password_frame, show='*', font=('微软雅黑', 10), width=25)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        self.password_entry.insert(0, 'admin123')
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        login_btn = ttk.Button(button_frame, text="登录", command=self._do_login, width=12)
        login_btn.pack(side=tk.LEFT, padx=10)
        
        exit_btn = ttk.Button(button_frame, text="退出", command=self.root.quit, width=12)
        exit_btn.pack(side=tk.LEFT, padx=10)
        
        self.error_label = ttk.Label(main_frame, text="", foreground='red', font=('微软雅黑', 9))
        self.error_label.pack(pady=5)
        
        ttk.Label(main_frame, text="默认账号: admin / admin123", font=('微软雅黑', 8), foreground='gray').pack(pady=10)
        
        self.username_entry.focus_set()
        self.root.bind('<Return>', lambda e: self._do_login())
    
    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username:
            self.error_label.config(text="请输入用户名")
            return
        
        if not password:
            self.error_label.config(text="请输入密码")
            return
        
        success, user = AuthModule.login(username, password)
        
        if success:
            self.root.destroy()
            self.on_login_success(user)
        else:
            self.error_label.config(text="用户名或密码错误")
    
    def run(self):
        self.root.mainloop()
