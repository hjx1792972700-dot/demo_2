import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from modules.product import ProductModule
from modules.auth import AuthModule


class ProductView:
    def __init__(self, parent, user):
        self.parent = parent
        self.user = user
        self.can_edit = AuthModule.check_permission(config.ROLE_MANAGER)
        
        self._create_widgets()
    
    def _create_widgets(self):
        frame = ttk.Frame(self.parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="产品管理", font=('微软雅黑', 14, 'bold')).pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        if self.can_edit:
            ttk.Button(btn_frame, text="添加产品", command=self._add_product).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="编辑产品", command=self._edit_product).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="删除产品", command=self._delete_product).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="刷新", command=self._refresh_list).pack(side=tk.LEFT, padx=5)
        
        filter_frame = ttk.LabelFrame(frame, text="筛选条件", padding=5)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="产品名称:").pack(side=tk.LEFT, padx=5)
        self.keyword_entry = ttk.Entry(filter_frame, width=20)
        self.keyword_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="分类:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="全部")
        self.category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var, state='readonly', width=15)
        self.category_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="搜索", command=self._search).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="重置", command=self._reset_filter).pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'name', 'category_name', 'spec', 'unit', 'cost_price', 'sale_price', 'safety_stock', 'stock_quantity')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='产品名称')
        self.tree.heading('category_name', text='分类')
        self.tree.heading('spec', text='规格')
        self.tree.heading('unit', text='单位')
        self.tree.heading('cost_price', text='成本价')
        self.tree.heading('sale_price', text='销售价')
        self.tree.heading('safety_stock', text='安全库存')
        self.tree.heading('stock_quantity', text='当前库存')
        
        self.tree.column('id', width=50)
        self.tree.column('name', width=150)
        self.tree.column('category_name', width=100)
        self.tree.column('spec', width=100)
        self.tree.column('unit', width=60)
        self.tree.column('cost_price', width=80)
        self.tree.column('sale_price', width=80)
        self.tree.column('safety_stock', width=80)
        self.tree.column('stock_quantity', width=80)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._load_categories()
        self._refresh_list()
    
    def _load_categories(self):
        categories = ProductModule.get_all_categories()
        values = ["全部"]
        for cat in categories:
            values.append(cat['name'])
        self.category_combo['values'] = values
    
    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = ProductModule.get_all_products()
        
        for p in products:
            self.tree.insert('', tk.END, values=(
                p['id'],
                p['name'],
                p.get('category_name', '') or '',
                p.get('spec', '') or '',
                p.get('unit', '个'),
                p.get('cost_price', 0),
                p.get('sale_price', 0),
                p.get('safety_stock', 10),
                p.get('stock_quantity', 0)
            ))
    
    def _search(self):
        keyword = self.keyword_entry.get().strip()
        category_name = self.category_var.get()
        
        category_id = None
        if category_name != "全部":
            categories = ProductModule.get_all_categories()
            for cat in categories:
                if cat['name'] == category_name:
                    category_id = cat['id']
                    break
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = ProductModule.search_products(
            keyword=keyword if keyword else None,
            category_id=category_id
        )
        
        for p in products:
            self.tree.insert('', tk.END, values=(
                p['id'],
                p['name'],
                p.get('category_name', '') or '',
                p.get('spec', '') or '',
                p.get('unit', '个'),
                p.get('cost_price', 0),
                p.get('sale_price', 0),
                p.get('safety_stock', 10),
                p.get('stock_quantity', 0)
            ))
    
    def _reset_filter(self):
        self.keyword_entry.delete(0, tk.END)
        self.category_var.set("全部")
        self._refresh_list()
    
    def _add_product(self):
        self._show_product_dialog()
    
    def _edit_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的产品")
            return
        
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        product = ProductModule.get_product_by_id(product_id)
        self._show_product_dialog(product)
    
    def _show_product_dialog(self, product=None):
        dialog = tk.Toplevel(self.parent)
        dialog.title("添加产品" if product is None else "编辑产品")
        dialog.geometry("400x450")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="产品名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(frame)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        if product:
            name_entry.insert(0, product['name'])
        
        ttk.Label(frame, text="分类:").grid(row=1, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(frame, textvariable=category_var, state='readonly')
        categories = ProductModule.get_all_categories()
        category_values = [cat['name'] for cat in categories]
        category_combo['values'] = category_values
        category_combo.grid(row=1, column=1, sticky=tk.EW, pady=5)
        if product and product.get('category_name'):
            category_var.set(product['category_name'])
        
        ttk.Label(frame, text="规格:").grid(row=2, column=0, sticky=tk.W, pady=5)
        spec_entry = ttk.Entry(frame)
        spec_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        if product and product.get('spec'):
            spec_entry.insert(0, product['spec'])
        
        ttk.Label(frame, text="单位:").grid(row=3, column=0, sticky=tk.W, pady=5)
        unit_var = tk.StringVar(value='个')
        unit_combo = ttk.Combobox(frame, textvariable=unit_var, values=['个', '件', '箱', '台', '套', '千克', '米'])
        unit_combo.grid(row=3, column=1, sticky=tk.EW, pady=5)
        if product and product.get('unit'):
            unit_var.set(product['unit'])
        
        ttk.Label(frame, text="成本价:").grid(row=4, column=0, sticky=tk.W, pady=5)
        cost_entry = ttk.Entry(frame)
        cost_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        if product:
            cost_entry.insert(0, str(product.get('cost_price', 0)))
        
        ttk.Label(frame, text="销售价:").grid(row=5, column=0, sticky=tk.W, pady=5)
        price_entry = ttk.Entry(frame)
        price_entry.grid(row=5, column=1, sticky=tk.EW, pady=5)
        if product:
            price_entry.insert(0, str(product.get('sale_price', 0)))
        
        ttk.Label(frame, text="安全库存:").grid(row=6, column=0, sticky=tk.W, pady=5)
        safety_entry = ttk.Entry(frame)
        safety_entry.grid(row=6, column=1, sticky=tk.EW, pady=5)
        if product:
            safety_entry.insert(0, str(product.get('safety_stock', 10)))
        else:
            safety_entry.insert(0, '10')
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        def save():
            name = name_entry.get().strip()
            category_name = category_var.get()
            spec = spec_entry.get().strip()
            unit = unit_var.get()
            
            try:
                cost_price = float(cost_entry.get() or 0)
                sale_price = float(price_entry.get() or 0)
                safety_stock = int(safety_entry.get() or 10)
            except ValueError:
                messagebox.showwarning("提示", "价格和库存必须是数字")
                return
            
            if not name:
                messagebox.showwarning("提示", "请输入产品名称")
                return
            
            category_id = None
            for cat in categories:
                if cat['name'] == category_name:
                    category_id = cat['id']
                    break
            
            product_data = {
                'name': name,
                'category_id': category_id,
                'spec': spec,
                'unit': unit,
                'cost_price': cost_price,
                'sale_price': sale_price,
                'safety_stock': safety_stock
            }
            
            if product is None:
                result = ProductModule.create_product(product_data)
                if result:
                    messagebox.showinfo("成功", "产品添加成功")
                    dialog.destroy()
                    self._refresh_list()
            else:
                ProductModule.update_product(product['id'], product_data)
                messagebox.showinfo("成功", "产品更新成功")
                dialog.destroy()
                self._refresh_list()
        
        ttk.Button(btn_frame, text="保存", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def _delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的产品")
            return
        
        item = self.tree.item(selected[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        if messagebox.askyesno("确认", f"确定要删除产品【{product_name}】吗？"):
            success, message = ProductModule.delete_product(product_id)
            if success:
                messagebox.showinfo("成功", "产品删除成功")
                self._refresh_list()
            else:
                messagebox.showerror("错误", message)
