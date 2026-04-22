import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from database.db_manager import DBManager
from modules.auth import AuthModule
from modules.inventory import InventoryModule


class PurchaseModule:
    
    @staticmethod
    def create_supplier(supplier_data):
        db = DBManager()
        supplier_id = db.execute_query(
            '''
            INSERT INTO suppliers (name, contact, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                supplier_data['name'],
                supplier_data.get('contact', ''),
                supplier_data.get('phone', ''),
                supplier_data.get('email', ''),
                supplier_data.get('address', '')
            ),
            commit=True
        )
        return supplier_id
    
    @staticmethod
    def update_supplier(supplier_id, supplier_data):
        db = DBManager()
        fields = []
        params = []
        
        if 'name' in supplier_data:
            fields.append("name = ?")
            params.append(supplier_data['name'])
        
        if 'contact' in supplier_data:
            fields.append("contact = ?")
            params.append(supplier_data['contact'])
        
        if 'phone' in supplier_data:
            fields.append("phone = ?")
            params.append(supplier_data['phone'])
        
        if 'email' in supplier_data:
            fields.append("email = ?")
            params.append(supplier_data['email'])
        
        if 'address' in supplier_data:
            fields.append("address = ?")
            params.append(supplier_data['address'])
        
        if not fields:
            return False
        
        params.append(supplier_id)
        query = f"UPDATE suppliers SET {', '.join(fields)} WHERE id = ?"
        
        db.execute_query(query, params, commit=True)
        return True
    
    @staticmethod
    def delete_supplier(supplier_id):
        db = DBManager()
        
        orders = db.execute_query(
            "SELECT COUNT(*) as count FROM purchase_orders WHERE supplier_id = ?",
            (supplier_id,)
        )
        if orders[0]['count'] > 0:
            return False, "该供应商有采购订单，无法删除"
        
        db.execute_query("DELETE FROM suppliers WHERE id = ?", (supplier_id,), commit=True)
        return True, None
    
    @staticmethod
    def get_supplier_by_id(supplier_id):
        db = DBManager()
        suppliers = db.execute_query(
            "SELECT * FROM suppliers WHERE id = ?",
            (supplier_id,)
        )
        if suppliers:
            return dict(suppliers[0])
        return None
    
    @staticmethod
    def get_all_suppliers():
        db = DBManager()
        suppliers = db.execute_query("SELECT * FROM suppliers ORDER BY id")
        return [dict(s) for s in suppliers]
    
    @staticmethod
    def create_purchase_order(supplier_id, items, created_by=None):
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
            INSERT INTO purchase_orders (supplier_id, total_amount, status, created_by)
            VALUES (?, ?, ?, ?)
            ''',
            (supplier_id, total_amount, config.STATUS_DRAFT, created_by),
            commit=True
        )
        
        for item in items:
            unit_price = item['unit_price']
            quantity = item['quantity']
            total_price = unit_price * quantity
            
            db.execute_query(
                '''
                INSERT INTO purchase_order_items 
                (purchase_order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (order_id, item['product_id'], quantity, unit_price, total_price),
                commit=True
            )
        
        return order_id
    
    @staticmethod
    def update_purchase_order(order_id, items):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM purchase_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "采购单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_DRAFT:
            return False, "只能修改草稿状态的采购单"
        
        db.execute_query(
            "DELETE FROM purchase_order_items WHERE purchase_order_id = ?",
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
                INSERT INTO purchase_order_items 
                (purchase_order_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (order_id, item['product_id'], quantity, unit_price, total_price),
                commit=True
            )
        
        db.execute_query(
            "UPDATE purchase_orders SET total_amount = ? WHERE id = ?",
            (total_amount, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def delete_purchase_order(order_id):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM purchase_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "采购单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_DRAFT:
            return False, "只能删除草稿状态的采购单"
        
        db.execute_query(
            "DELETE FROM purchase_order_items WHERE purchase_order_id = ?",
            (order_id,),
            commit=True
        )
        db.execute_query(
            "DELETE FROM purchase_orders WHERE id = ?",
            (order_id,),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def approve_purchase_order(order_id, approved_by=None):
        db = DBManager()
        
        if approved_by is None:
            current_user = AuthModule.get_current_user()
            if current_user:
                approved_by = current_user['id']
        
        order = db.execute_query(
            "SELECT * FROM purchase_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "采购单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_DRAFT:
            return False, "只能审批草稿状态的采购单"
        
        db.execute_query(
            '''
            UPDATE purchase_orders 
            SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''',
            (config.STATUS_APPROVED, approved_by, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def complete_purchase_order(order_id):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM purchase_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "采购单不存在"
        
        order = dict(order[0])
        if order['status'] != config.STATUS_APPROVED:
            return False, "只能完成已审批的采购单"
        
        items = db.execute_query(
            "SELECT * FROM purchase_order_items WHERE purchase_order_id = ?",
            (order_id,)
        )
        
        for item in items:
            result, msg = InventoryModule.stock_in(
                item['product_id'],
                item['quantity'],
                item['unit_price'],
                config.REFERENCE_TYPE_PURCHASE,
                order_id
            )
            if not result:
                return False, msg
        
        db.execute_query(
            "UPDATE purchase_orders SET status = ? WHERE id = ?",
            (config.STATUS_COMPLETED, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def cancel_purchase_order(order_id):
        db = DBManager()
        
        order = db.execute_query(
            "SELECT * FROM purchase_orders WHERE id = ?",
            (order_id,)
        )
        if not order:
            return False, "采购单不存在"
        
        order = dict(order[0])
        if order['status'] == config.STATUS_COMPLETED:
            return False, "已完成的采购单不能取消"
        
        db.execute_query(
            "UPDATE purchase_orders SET status = ? WHERE id = ?",
            (config.STATUS_CANCELLED, order_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def get_purchase_order_by_id(order_id):
        db = DBManager()
        
        orders = db.execute_query(
            '''
            SELECT po.*, s.name as supplier_name,
                   uc.username as creator_name, ua.username as approver_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN users uc ON po.created_by = uc.id
            LEFT JOIN users ua ON po.approved_by = ua.id
            WHERE po.id = ?
            ''',
            (order_id,)
        )
        
        if not orders:
            return None
        
        order = dict(orders[0])
        
        items = db.execute_query(
            '''
            SELECT poi.*, p.name as product_name, p.spec, p.unit
            FROM purchase_order_items poi
            JOIN products p ON poi.product_id = p.id
            WHERE poi.purchase_order_id = ?
            ''',
            (order_id,)
        )
        order['items'] = [dict(i) for i in items]
        
        return order
    
    @staticmethod
    def get_all_purchase_orders(status=None, supplier_id=None, start_date=None, end_date=None):
        db = DBManager()
        query = '''
            SELECT po.*, s.name as supplier_name,
                   uc.username as creator_name, ua.username as approver_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN users uc ON po.created_by = uc.id
            LEFT JOIN users ua ON po.approved_by = ua.id
            WHERE 1=1
        '''
        params = []
        
        if status:
            query += " AND po.status = ?"
            params.append(status)
        
        if supplier_id:
            query += " AND po.supplier_id = ?"
            params.append(supplier_id)
        
        if start_date:
            query += " AND date(po.created_at) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(po.created_at) <= date(?)"
            params.append(end_date)
        
        query += " ORDER BY po.id DESC"
        
        orders = db.execute_query(query, params)
        return [dict(o) for o in orders]
    
    @staticmethod
    def get_purchase_statistics(start_date=None, end_date=None):
        db = DBManager()
        
        query = '''
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_amount,
                SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) as completed_amount,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_count,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
            FROM purchase_orders
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
