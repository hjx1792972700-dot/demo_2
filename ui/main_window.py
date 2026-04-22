import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from modules.auth import AuthModule
from ui.product_view import ProductView
from ui.inventory_view import InventoryView
from ui.purchase_view import PurchaseView
from ui.sales_view import SalesView
from ui.report_view import ReportView


class MainWindow:
    def __init__(self, user):
        self.user = user
        self.root = tk.Tk()
        self.root.title(f"{config.WINDOW_TITLE} - 当前用户: {user['username']}")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(1000, 600)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - config.WINDOW_WIDTH) // 2
        y = (screen_height - config.WINDOW_HEIGHT) // 2
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}")
        
        self.current_view = None
        self._create_menu()
        self._create_layout()
        self._show_default_view()
    
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="修改密码", command=self._change_password)
        file_menu.add_separator()
        file_menu.add_command(label="退出登录", command=self._logout)
        file_menu.add_command(label="退出系统", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_layout(self):
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = ttk.Frame(self.paned_window, width=180)
        right_frame = ttk.Frame(self.paned_window)
        
        self.paned_window.add(left_frame, weight=0)
        self.paned_window.add(right_frame, weight=3)
        
        self._create_navigation(left_frame)
        
        self.content_frame = right_frame
        self.content_label = ttk.Label(right_frame, text="请选择功能模块", font=('微软雅黑', 16), foreground='gray')
        self.content_label.pack(expand=True)
    
    def _create_navigation(self, parent):
        nav_frame = ttk.LabelFrame(parent, text="功能导航", padding=5)
        nav_frame.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.configure('Nav.TButton', font=('微软雅黑', 10), padding=10)
        
        buttons = [
            ("产品管理", self._show_product_view),
            ("库存管理", self._show_inventory_view),
            ("采购管理", self._show_purchase_view),
            ("销售管理", self._show_sales_view),
            ("报表统计", self._show_report_view),
        ]
        
        if self.user['role'] == config.ROLE_ADMIN:
            buttons.append(("用户管理", self._show_user_view))
        
        for text, command in buttons:
            btn = ttk.Button(nav_frame, text=text, command=command, style='Nav.TButton')
            btn.pack(fill=tk.X, pady=3)
        
        info_frame = ttk.LabelFrame(parent, text="用户信息", padding=5)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"用户名: {self.user['username']}").pack(anchor=tk.W)
        
        role_map = {
            config.ROLE_ADMIN: "管理员",
            config.ROLE_MANAGER: "经理",
            config.ROLE_EMPLOYEE: "员工"
        }
        role_display = role_map.get(self.user['role'], self.user['role'])
        ttk.Label(info_frame, text=f"角色: {role_display}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"登录时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}").pack(anchor=tk.W)
    
    def _clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_default_view(self):
        self._show_product_view()
    
    def _show_product_view(self):
        self._clear_content_frame()
        self.current_view = ProductView(self.content_frame, self.user)
    
    def _show_inventory_view(self):
        self._clear_content_frame()
        self.current_view = InventoryView(self.content_frame, self.user)
    
    def _show_purchase_view(self):
        self._clear_content_frame()
        self.current_view = PurchaseView(self.content_frame, self.user)
    
    def _show_sales_view(self):
        self._clear_content_frame()
        self.current_view = SalesView(self.content_frame, self.user)
    
    def _show_report_view(self):
        self._clear_content_frame()
        self.current_view = ReportView(self.content_frame, self.user)
    
    def _show_user_view(self):
        self._clear_content_frame()
        self._create_user_view()
    
    def _create_user_view(self):
        frame = ttk.Frame(self.content_frame, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="用户管理", font=('微软雅黑', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="添加用户", command=self._add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑用户", command=self._edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除用户", command=self._delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新", command=self._refresh_user_list).pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'username', 'role', 'email', 'phone', 'created_at')
        self.user_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        self.user_tree.heading('id', text='ID')
        self.user_tree.heading('username', text='用户名')
        self.user_tree.heading('role', text='角色')
        self.user_tree.heading('email', text='邮箱')
        self.user_tree.heading('phone', text='电话')
        self.user_tree.heading('created_at', text='创建时间')
        
        self.user_tree.column('id', width=50)
        self.user_tree.column('username', width=100)
        self.user_tree.column('role', width=80)
        self.user_tree.column('email', width=150)
        self.user_tree.column('phone', width=120)
        self.user_tree.column('created_at', width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._refresh_user_list()
    
    def _refresh_user_list(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        users = AuthModule.get_all_users()
        
        role_map = {
            config.ROLE_ADMIN: "管理员",
            config.ROLE_MANAGER: "经理",
            config.ROLE_EMPLOYEE: "员工"
        }
        
        for user in users:
            role_display = role_map.get(user['role'], user['role'])
            self.user_tree.insert('', tk.END, values=(
                user['id'],
                user['username'],
                role_display,
                user.get('email', '') or '',
                user.get('phone', '') or '',
                user.get('created_at', '') or ''
            ))
    
    def _add_user(self):
        self._show_user_dialog()
    
    def _edit_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的用户")
            return
        
        item = self.user_tree.item(selected[0])
        user_id = item['values'][0]
        user = AuthModule.get_user_by_id(user_id)
        self._show_user_dialog(user)
    
    def _show_user_dialog(self, user=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("添加用户" if user is None else "编辑用户")
        dialog.geometry("350x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="用户名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(frame)
        username_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        if user:
            username_entry.insert(0, user['username'])
            username_entry.config(state='disabled')
        
        ttk.Label(frame, text="密码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(frame, show='*')
        password_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        if user:
            ttk.Label(frame, text="(留空则不修改)", foreground='gray').grid(row=1, column=2, sticky=tk.W)
        
        ttk.Label(frame, text="角色:").grid(row=2, column=0, sticky=tk.W, pady=5)
        role_var = tk.StringVar(value=config.ROLE_EMPLOYEE)
        role_combo = ttk.Combobox(frame, textvariable=role_var, state='readonly')
        role_combo['values'] = (config.ROLE_ADMIN, config.ROLE_MANAGER, config.ROLE_EMPLOYEE)
        role_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        if user:
            role_var.set(user['role'])
        
        ttk.Label(frame, text="邮箱:").grid(row=3, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(frame)
        email_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        if user and user.get('email'):
            email_entry.insert(0, user['email'])
        
        ttk.Label(frame, text="电话:").grid(row=4, column=0, sticky=tk.W, pady=5)
        phone_entry = ttk.Entry(frame)
        phone_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        if user and user.get('phone'):
            phone_entry.insert(0, user['phone'])
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        def save():
            username = username_entry.get().strip()
            password = password_entry.get()
            role = role_var.get()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()
            
            if not username:
                messagebox.showwarning("提示", "请输入用户名")
                return
            
            if user is None:
                if not password:
                    messagebox.showwarning("提示", "请输入密码")
                    return
                
                user_data = {
                    'username': username,
                    'password': password,
                    'role': role,
                    'email': email,
                    'phone': phone
                }
                result = AuthModule.create_user(user_data)
                if result:
                    messagebox.showinfo("成功", "用户添加成功")
                    dialog.destroy()
                    self._refresh_user_list()
                else:
                    messagebox.showerror("错误", "用户名已存在")
            else:
                update_data = {
                    'role': role,
                    'email': email,
                    'phone': phone
                }
                if password:
                    update_data['password'] = password
                
                AuthModule.update_user(user['id'], update_data)
                messagebox.showinfo("成功", "用户更新成功")
                dialog.destroy()
                self._refresh_user_list()
        
        ttk.Button(btn_frame, text="保存", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def _delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的用户")
            return
        
        item = self.user_tree.item(selected[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        if user_id == self.user['id']:
            messagebox.showwarning("提示", "不能删除当前登录用户")
            return
        
        if messagebox.askyesno("确认", f"确定要删除用户【{username}】吗？"):
            AuthModule.delete_user(user_id)
            messagebox.showinfo("成功", "用户删除成功")
            self._refresh_user_list()
    
    def _change_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("修改密码")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="新密码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        new_pass_entry = ttk.Entry(frame, show='*')
        new_pass_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(frame, text="确认密码:").grid(row=1, column=0, sticky=tk.W, pady=5)
        confirm_pass_entry = ttk.Entry(frame, show='*')
        confirm_pass_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def save():
            new_pass = new_pass_entry.get()
            confirm_pass = confirm_pass_entry.get()
            
            if not new_pass or not confirm_pass:
                messagebox.showwarning("提示", "请输入密码")
                return
            
            if new_pass != confirm_pass:
                messagebox.showerror("错误", "两次输入的密码不一致")
                return
            
            AuthModule.update_user(self.user['id'], {'password': new_pass})
            messagebox.showinfo("成功", "密码修改成功")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="确定", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def _logout(self):
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            AuthModule.logout()
            self.root.destroy()
            from ui.login_window import LoginWindow
            login_window = LoginWindow(self._relogin)
            login_window.run()
    
    def _relogin(self, user):
        self.__init__(user)
        self.run()
    
    def _show_about(self):
        messagebox.showinfo("关于", f"{config.WINDOW_TITLE}\n\n版本: 1.0\n\n一个基于Python的轻量级ERP系统")
    
    def run(self):
        self.root.mainloop()
