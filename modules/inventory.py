import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from database.db_manager import DBManager
from modules.auth import AuthModule


class InventoryModule:
    
    @staticmethod
    def stock_in(product_id, quantity, unit_cost, reference_type=config.REFERENCE_TYPE_MANUAL, reference_id=None, user_id=None):
        db = DBManager()
        
        if quantity <= 0:
            return False, "入库数量必须大于0"
        
        if user_id is None:
            current_user = AuthModule.get_current_user()
            if current_user:
                user_id = current_user['id']
        
        inventory = db.execute_query(
            "SELECT * FROM inventory WHERE product_id = ?",
            (product_id,)
        )
        
        if not inventory:
            return False, "产品库存记录不存在"
        
        inv = dict(inventory[0])
        before_quantity = inv['quantity']
        after_quantity = before_quantity + quantity
        
        old_total_cost = inv['avg_cost'] * inv['quantity']
        new_total_cost = unit_cost * quantity
        total_quantity = after_quantity
        
        if total_quantity > 0:
            new_avg_cost = (old_total_cost + new_total_cost) / total_quantity
        else:
            new_avg_cost = 0
        
        db.execute_query(
            '''
            UPDATE inventory 
            SET quantity = ?, avg_cost = ?, last_update = CURRENT_TIMESTAMP
            WHERE product_id = ?
            ''',
            (after_quantity, new_avg_cost, product_id),
            commit=True
        )
        
        db.execute_query(
            '''
            INSERT INTO inventory_transactions 
            (product_id, type, quantity, before_quantity, after_quantity, reference_type, reference_id, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (product_id, config.TRANSACTION_TYPE_IN, quantity, before_quantity, after_quantity, 
             reference_type, reference_id, user_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def stock_out(product_id, quantity, reference_type=config.REFERENCE_TYPE_MANUAL, reference_id=None, user_id=None):
        db = DBManager()
        
        if quantity <= 0:
            return False, "出库数量必须大于0"
        
        if user_id is None:
            current_user = AuthModule.get_current_user()
            if current_user:
                user_id = current_user['id']
        
        inventory = db.execute_query(
            "SELECT * FROM inventory WHERE product_id = ?",
            (product_id,)
        )
        
        if not inventory:
            return False, "产品库存记录不存在"
        
        inv = dict(inventory[0])
        before_quantity = inv['quantity']
        
        if before_quantity < quantity:
            return False, f"库存不足，当前库存：{before_quantity}，需要出库：{quantity}"
        
        after_quantity = before_quantity - quantity
        
        db.execute_query(
            '''
            UPDATE inventory 
            SET quantity = ?, last_update = CURRENT_TIMESTAMP
            WHERE product_id = ?
            ''',
            (after_quantity, product_id),
            commit=True
        )
        
        db.execute_query(
            '''
            INSERT INTO inventory_transactions 
            (product_id, type, quantity, before_quantity, after_quantity, reference_type, reference_id, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (product_id, config.TRANSACTION_TYPE_OUT, quantity, before_quantity, after_quantity,
             reference_type, reference_id, user_id),
            commit=True
        )
        
        return True, None
    
    @staticmethod
    def get_inventory_by_product(product_id):
        db = DBManager()
        inventory = db.execute_query(
            '''
            SELECT i.*, p.name as product_name, p.spec, p.unit, p.safety_stock
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.product_id = ?
            ''',
            (product_id,)
        )
        if inventory:
            return dict(inventory[0])
        return None
    
    @staticmethod
    def get_all_inventory():
        db = DBManager()
        inventory = db.execute_query(
            '''
            SELECT i.*, p.name as product_name, p.spec, p.unit, p.safety_stock,
                   (i.quantity * i.avg_cost) as stock_value
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            ORDER BY i.product_id
            '''
        )
        return [dict(inv) for inv in inventory]
    
    @staticmethod
    def get_low_stock_products():
        db = DBManager()
        products = db.execute_query(
            '''
            SELECT i.*, p.name as product_name, p.spec, p.unit, p.safety_stock
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.quantity < p.safety_stock
            ORDER BY i.quantity
            '''
        )
        return [dict(p) for p in products]
    
    @staticmethod
    def get_inventory_transactions(product_id=None, start_date=None, end_date=None):
        db = DBManager()
        query = '''
            SELECT it.*, p.name as product_name, u.username as creator_name
            FROM inventory_transactions it
            JOIN products p ON it.product_id = p.id
            LEFT JOIN users u ON it.created_by = u.id
            WHERE 1=1
        '''
        params = []
        
        if product_id:
            query += " AND it.product_id = ?"
            params.append(product_id)
        
        if start_date:
            query += " AND date(it.created_at) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(it.created_at) <= date(?)"
            params.append(end_date)
        
        query += " ORDER BY it.created_at DESC"
        
        transactions = db.execute_query(query, params)
        return [dict(t) for t in transactions]
