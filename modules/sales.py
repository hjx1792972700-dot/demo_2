import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from database.db_manager import DBManager
from modules.auth import AuthModule
from modules.inventory import InventoryModule


class SalesModule:
    
    @staticmethod
    def create_customer(customer_data):
        db = DBManager()
        customer_id = db.execute_query(
            '''
            INSERT INTO customers (name, contact, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                customer_data['name'],
                customer_data.get('contact', ''),
                customer_data.get('phone', ''),
                customer_data.get('email', ''),
                customer_data.get('address', '')
            ),
            commit=True
        )
        return customer_id
    
    @staticmethod
    def update_customer(customer_id, customer_data):
        db = DBManager()
        fields = []
        params = []
        
        if 'name' in customer_data:
            fields.append("name = ?")
            params.append(customer_data['name'])
        
        if 'contact' in customer_data:
            fields.append("contact = ?")
            params.append(customer_data['contact'])
        
        if 'phone' in customer_data:
            fields.append("phone = ?")
            params.append(customer_data['phone'])
        
        if 'email' in customer_data:
            fields.append("email = ?")
            params.append(customer_data['email'])
        
        if 'address' in customer_data:
            fields.append("address = ?")
            params.append(customer_data['address'])
        
        if not fields:
            return False
        
        params.append(customer_id)
        query = f"UPDATE customers SET {', '.join(fields)} WHERE id = ?"
        
        db.execute_query(query, params, commit=True)
        return True
    
    @staticmethod
    def delete_customer(customer_id):
        db = DBManager()
        
        orders = db.execute_query(
            "SELECT COUNT(*) as count FROM sales_orders WHERE customer_id = ?",
            (customer_id,)
        )
        if orders[0]['count'] > 0:
            return False, "该客户有销售订单，无法删除"
        
        db.execute_query("DELETE FROM customers WHERE id = ?", (customer_id,), commit=True)
        return True, None
    
    @staticmethod
    def get_customer_by_id(customer_id):
        db = DBManager()
        customers = db.execute_query(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,)
        )
        if customers:
            return dict(customers[0])
        return None
    
    @staticmethod
    def get_all_customers():
        db = DBManager()
        customers = db.execute_query("SELECT * FROM customers ORDER BY id")
        return [dict(c) for c in customers]
    
    @staticmethod
    def create_sales_order(customer_id, items, created_by=None):
        db = DBManager()
        
        if created_by is None:
            current_user = AuthModule.get_current_user()
            if current_user:
                created_by = current_user['id']
        
        total_amount = 0
        for item in items:
            total_amount += item['quantity'] * item['unit_price']
        
        order_id = db.execute_query(
            '''
            INSERT INTO sales_orders (customer_id, total_amount, status, created_by)
            VALUES (?, ?, ?, ?)
            ''',
            (customer_id, total_amount, config.STATUS_DRAFT, created_by),
            commit=True
        )
        
        for item in items:
            unit_price = item['unit_price']
            quantity = item['quantity']
            total_price = unit_price * quantity
            
            db.execute_query(
                '''
                INSERT INTO sales_order_items 
                (sales_order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (order_id, item['product_id'], quantity, unit_price, total_price),
                commit=True
            )
        
        return order_id
    
    @staticmethod
    def update_sales_order(order_id, items):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM sales_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "销售单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_DRAFT:
            return False, "只能修改草稿状态的销售单"
        
        db.execute_query(
            "DELETE FROM sales_order_items WHERE sales_order_id = ?",
            (order_id,),
            commit=True
        )
        
        total_amount = 0
        for item in items:
            total_amount += item['quantity'] * item['unit_price']
            unit_price = item['unit_price']
            quantity = item['quantity']
            total_price = unit_price * quantity
            
            db.execute_query(
                '''
                INSERT INTO sales_order_items 
                (sales_order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (order_id, item['product_id'], quantity, unit_price, total_price),
                commit=True
            )
        
        db.execute_query(
            "UPDATE sales_orders SET total_amount = ? WHERE id = ?",
            (total_amount, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def delete_sales_order(order_id):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM sales_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "销售单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_DRAFT:
            return False, "只能删除草稿状态的销售单"
        
        db.execute_query(
            "DELETE FROM sales_order_items WHERE sales_order_id = ?",
            (order_id,),
            commit=True
        )
        db.execute_query(
            "DELETE FROM sales_orders WHERE id = ?",
            (order_id,),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def approve_sales_order(order_id, approved_by=None):
        db = DBManager()
        
        if approved_by is None:
            current_user = AuthModule.get_current_user()
            if current_user:
                approved_by = current_user['id']
        
        order = db.execute_query(
            "SELECT * FROM sales_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "销售单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_DRAFT:
            return False, "只能审批草稿状态的销售单"
        
        items = db.execute_query(
            "SELECT * FROM sales_order_items WHERE sales_order_id = ?",
            (order_id,)
        )
        
        for item in items:
            inventory = db.execute_query(
                "SELECT quantity FROM inventory WHERE product_id = ?",
                (item['product_id'],)
            )
            if not inventory or inventory[0]['quantity'] < item['quantity']:
                product = db.execute_query(
                    "SELECT name FROM products WHERE id = ?",
                    (item['product_id'],)
                )
                product_name = product[0]['name'] if product else "未知产品"
                current_qty = inventory[0]['quantity'] if inventory else 0
                return False, f"产品【{product_name}】库存不足，当前库存：{current_qty}，需要：{item['quantity']}"
        
        db.execute_query(
            '''
            UPDATE sales_orders 
            SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''',
            (config.STATUS_APPROVED, approved_by, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def complete_sales_order(order_id):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM sales_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "销售单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_APPROVED:
            return False, "只能完成已审批的销售单"
        
        items = db.execute_query(
            "SELECT * FROM sales_order_items WHERE sales_order_id = ?",
            (order_id,)
        )
        
        for item in items:
            result, msg = InventoryModule.stock_out(
                item['product_id'],
                item['quantity'],
                config.REFERENCE_TYPE_SALE,
                order_id
            )
            if not result:
                return False, msg
        
        db.execute_query(
            "UPDATE sales_orders SET status = ? WHERE id = ?",
            (config.STATUS_COMPLETED, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def cancel_sales_order(order_id):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM sales_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "销售单不存在"
        
        order = dict(order[0])
        if order['status'] == config.STATUS_COMPLETED:
            return False, "已完成的销售单不能取消"
        
        db.execute_query(
            "UPDATE sales_orders SET status = ? WHERE id = ?",
            (config.STATUS_CANCELLED, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def get_sales_order_by_id(order_id):
        db = DBManager()
        
        orders = db.execute_query(
            '''
            SELECT so.*, c.name as customer_name,
                   uc.username as creator_name, ua.username as approver_name
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.id
            LEFT JOIN users uc ON so.created_by = uc.id
            LEFT JOIN users ua ON so.approved_by = ua.id
            WHERE so.id = ?
            ''',
            (order_id,)
        )
        
        if not orders:
            return None
        
        order = dict(orders[0])
        
        items = db.execute_query(
            '''
            SELECT soi.*, p.name as product_name, p.spec, p.unit
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.id
            WHERE soi.sales_order_id = ?
            ''',
            (order_id,)
        )
        order['items'] = [dict(i) for i in items]
        
        return order
    
    @staticmethod
    def get_all_sales_orders(status=None, customer_id=None, start_date=None, end_date=None):
        db = DBManager()
        query = '''
            SELECT so.*, c.name as customer_name,
                   uc.username as creator_name, ua.username as approver_name
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.id
            LEFT JOIN users uc ON so.created_by = uc.id
            LEFT JOIN users ua ON so.approved_by = ua.id
            WHERE 1=1
        '''
        params = []
        
        if status:
            query += " AND so.status = ?"
            params.append(status)
        
        if customer_id:
            query += " AND so.customer_id = ?"
            params.append(customer_id)
        
        if start_date:
            query += " AND date(so.created_at) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(so.created_at) <= date(?)"
            params.append(end_date)
        
        query += " ORDER BY so.id DESC"
        
        orders = db.execute_query(query, params)
        return [dict(o) for o in orders]
    
    @staticmethod
    def get_sales_statistics(start_date=None, end_date=None):
        db = DBManager()
        
        query = '''
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_amount,
                SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) as completed_amount,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_count,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
            FROM sales_orders
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND date(created_at) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(created_at) <= date(?)"
            params.append(end_date)
        
        result = db.execute_query(query, params)
        if result:
            return dict(result[0])
        return None
