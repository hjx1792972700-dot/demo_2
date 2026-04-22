import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from database.db_manager import DBManager


class ProductModule:
    
    @staticmethod
    def create_category(name, description=''):
        db = DBManager()
        category_id = db.execute_query(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (name, description),
            commit=True
        )
        return category_id
    
    @staticmethod
    def update_category(category_id, name, description=''):
        db = DBManager()
        db.execute_query(
            "UPDATE categories SET name = ?, description = ? WHERE id = ?",
            (name, description, category_id),
            commit=True
        )
        return True
    
    @staticmethod
    def delete_category(category_id):
        db = DBManager()
        products = db.execute_query(
            "SELECT COUNT(*) as count FROM products WHERE category_id = ?",
            (category_id,)
        )
        if products[0]['count'] > 0:
            return False, "该分类下存在产品，无法删除"
        
        db.execute_query("DELETE FROM categories WHERE id = ?", (category_id,), commit=True)
        return True, None
    
    @staticmethod
    def get_category_by_id(category_id):
        db = DBManager()
        categories = db.execute_query(
            "SELECT * FROM categories WHERE id = ?",
            (category_id,)
        )
        if categories:
            return dict(categories[0])
        return None
    
    @staticmethod
    def get_all_categories():
        db = DBManager()
        categories = db.execute_query("SELECT * FROM categories ORDER BY id")
        return [dict(c) for c in categories]
    
    @staticmethod
    def create_product(product_data):
        db = DBManager()
        product_id = db.execute_query(
            '''
            INSERT INTO products (name, category_id, spec, unit, cost_price, sale_price, safety_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                product_data['name'],
                product_data.get('category_id'),
                product_data.get('spec', ''),
                product_data.get('unit', '个'),
                product_data.get('cost_price', 0),
                product_data.get('sale_price', 0),
                product_data.get('safety_stock', 10)
            ),
            commit=True
        )
        
        db.execute_query(
            "INSERT INTO inventory (product_id, quantity, avg_cost) VALUES (?, 0, 0)",
            (product_id,),
            commit=True
        )
        
        return product_id
    
    @staticmethod
    def update_product(product_id, product_data):
        db = DBManager()
        fields = []
        params = []
        
        if 'name' in product_data:
            fields.append("name = ?")
            params.append(product_data['name'])
        
        if 'category_id' in product_data:
            fields.append("category_id = ?")
            params.append(product_data['category_id'])
        
        if 'spec' in product_data:
            fields.append("spec = ?")
            params.append(product_data['spec'])
        
        if 'unit' in product_data:
            fields.append("unit = ?")
            params.append(product_data['unit'])
        
        if 'cost_price' in product_data:
            fields.append("cost_price = ?")
            params.append(product_data['cost_price'])
        
        if 'sale_price' in product_data:
            fields.append("sale_price = ?")
            params.append(product_data['sale_price'])
        
        if 'safety_stock' in product_data:
            fields.append("safety_stock = ?")
            params.append(product_data['safety_stock'])
        
        if not fields:
            return False
        
        params.append(product_id)
        query = f"UPDATE products SET {', '.join(fields)} WHERE id = ?"
        
        db.execute_query(query, params, commit=True)
        return True
    
    @staticmethod
    def delete_product(product_id):
        db = DBManager()
        
        inventory = db.execute_query(
            "SELECT quantity FROM inventory WHERE product_id = ?",
            (product_id,)
        )
        if inventory and inventory[0]['quantity'] > 0:
            return False, "该产品有库存，无法删除"
        
        purchase_items = db.execute_query(
            "SELECT COUNT(*) as count FROM purchase_order_items WHERE product_id = ?",
            (product_id,)
        )
        if purchase_items[0]['count'] > 0:
            return False, "该产品有采购记录，无法删除"
        
        sales_items = db.execute_query(
            "SELECT COUNT(*) as count FROM sales_order_items WHERE product_id = ?",
            (product_id,)
        )
        if sales_items[0]['count'] > 0:
            return False, "该产品有销售记录，无法删除"
        
        db.execute_query("DELETE FROM inventory WHERE product_id = ?", (product_id,), commit=True)
        db.execute_query("DELETE FROM products WHERE id = ?", (product_id,), commit=True)
        return True, None
    
    @staticmethod
    def get_product_by_id(product_id):
        db = DBManager()
        products = db.execute_query(
            '''
            SELECT p.*, c.name as category_name, i.quantity as stock_quantity
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE p.id = ?
            ''',
            (product_id,)
        )
        if products:
            return dict(products[0])
        return None
    
    @staticmethod
    def get_all_products():
        db = DBManager()
        products = db.execute_query(
            '''
            SELECT p.*, c.name as category_name, i.quantity as stock_quantity
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            ORDER BY p.id
            '''
        )
        return [dict(p) for p in products]
    
    @staticmethod
    def search_products(keyword=None, category_id=None, min_price=None, max_price=None):
        db = DBManager()
        query = '''
            SELECT p.*, c.name as category_name, i.quantity as stock_quantity
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE 1=1
        '''
        params = []
        
        if keyword:
            query += " AND (p.name LIKE ? OR p.spec LIKE ?)"
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        
        if min_price is not None:
            query += " AND p.sale_price >= ?"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND p.sale_price <= ?"
            params.append(max_price)
        
        query += " ORDER BY p.id"
        
        products = db.execute_query(query, params)
        return [dict(p) for p in products]
