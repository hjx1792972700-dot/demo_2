import os
import sys
import csv
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from database.db_manager import DBManager


class ReportModule:
    
    @staticmethod
    def generate_inventory_report():
        db = DBManager()
        
        inventory = db.execute_query(
            '''
            SELECT 
                p.id,
                p.name,
                c.name as category_name,
                p.spec,
                p.unit,
                p.cost_price,
                p.sale_price,
                p.safety_stock,
                i.quantity,
                i.avg_cost,
                (i.quantity * i.avg_cost) as stock_value,
                (i.quantity * (p.sale_price - i.avg_cost)) as potential_profit
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN inventory i ON p.id = i.product_id
            ORDER BY p.id
            '''
        )
        
        result = []
        total_quantity = 0
        total_value = 0
        total_profit = 0
        
        for item in inventory:
            item_dict = dict(item)
            result.append(item_dict)
            total_quantity += item_dict.get('quantity', 0) or 0
            total_value += item_dict.get('stock_value', 0) or 0
            total_profit += item_dict.get('potential_profit', 0) or 0
        
        summary = {
            'total_products': len(result),
            'total_quantity': total_quantity,
            'total_value': total_value,
            'total_profit': total_profit
        }
        
        return {'data': result, 'summary': summary}
    
    @staticmethod
    def generate_purchase_report(start_date=None, end_date=None):
        db = DBManager()
        
        query = '''
            SELECT 
                po.id,
                po.supplier_id,
                s.name as supplier_name,
                po.total_amount,
                po.status,
                po.created_at,
                po.approved_at,
                uc.username as creator_name,
                ua.username as approver_name,
                COUNT(poi.id) as item_count
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            LEFT JOIN users uc ON po.created_by = uc.id
            LEFT JOIN users ua ON po.approved_by = ua.id
            LEFT JOIN purchase_order_items poi ON po.id = poi.purchase_order_id
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND date(po.created_at) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(po.created_at) <= date(?)"
            params.append(end_date)
        
        query += " GROUP BY po.id ORDER BY po.id DESC"
        
        orders = db.execute_query(query, params)
        
        result = []
        total_amount = 0
        completed_amount = 0
        
        for order in orders:
            order_dict = dict(order)
            result.append(order_dict)
            total_amount += order_dict.get('total_amount', 0) or 0
            if order_dict.get('status') == config.STATUS_COMPLETED:
                completed_amount += order_dict.get('total_amount', 0) or 0
        
        summary = {
            'total_orders': len(result),
            'total_amount': total_amount,
            'completed_amount': completed_amount
        }
        
        return {'data': result, 'summary': summary}
    
    @staticmethod
    def generate_sales_report(start_date=None, end_date=None):
        db = DBManager()
        
        query = '''
            SELECT 
                so.id,
                so.customer_id,
                c.name as customer_name,
                so.total_amount,
                so.status,
                so.created_at,
                so.approved_at,
                uc.username as creator_name,
                ua.username as approver_name,
                COUNT(soi.id) as item_count
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.id
            LEFT JOIN users uc ON so.created_by = uc.id
            LEFT JOIN users ua ON so.approved_by = ua.id
            LEFT JOIN sales_order_items soi ON so.id = soi.sales_order_id
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += " AND date(so.created_at) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(so.created_at) <= date(?)"
            params.append(end_date)
        
        query += " GROUP BY so.id ORDER BY so.id DESC"
        
        orders = db.execute_query(query, params)
        
        result = []
        total_amount = 0
        completed_amount = 0
        
        for order in orders:
            order_dict = dict(order)
            result.append(order_dict)
            total_amount += order_dict.get('total_amount', 0) or 0
            if order_dict.get('status') == config.STATUS_COMPLETED:
                completed_amount += order_dict.get('total_amount', 0) or 0
        
        summary = {
            'total_orders': len(result),
            'total_amount': total_amount,
            'completed_amount': completed_amount
        }
        
        return {'data': result, 'summary': summary}
    
    @staticmethod
    def generate_profit_report(start_date=None, end_date=None):
        db = DBManager()
        
        query = '''
            SELECT 
                soi.product_id,
                p.name as product_name,
                c.name as category_name,
                SUM(soi.quantity) as total_quantity,
                SUM(soi.total_price) as total_sales_amount,
                SUM(soi.quantity * p.cost_price) as total_cost_amount,
                SUM(soi.total_price - soi.quantity * p.cost_price) as profit_amount
            FROM sales_order_items soi
            JOIN sales_orders so ON soi.sales_order_id = so.id
            JOIN products p ON soi.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE so.status = ?
        '''
        params = [config.STATUS_COMPLETED]
        
        if start_date:
            query += " AND date(so.created_at) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(so.created_at) <= date(?)"
            params.append(end_date)
        
        query += " GROUP BY soi.product_id ORDER BY profit_amount DESC"
        
        items = db.execute_query(query, params)
        
        result = []
        total_quantity = 0
        total_sales = 0
        total_cost = 0
        total_profit = 0
        
        for item in items:
            item_dict = dict(item)
            result.append(item_dict)
            total_quantity += item_dict.get('total_quantity', 0) or 0
            total_sales += item_dict.get('total_sales_amount', 0) or 0
            total_cost += item_dict.get('total_cost_amount', 0) or 0
            total_profit += item_dict.get('profit_amount', 0) or 0
        
        profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
        
        summary = {
            'total_products': len(result),
            'total_quantity': total_quantity,
            'total_sales': total_sales,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'profit_margin': profit_margin
        }
        
        return {'data': result, 'summary': summary}
    
    @staticmethod
    def export_to_csv(data, filename, fieldnames=None):
        if not data:
            return False, "没有数据可导出"
        
        try:
            if fieldnames is None:
                fieldnames = list(data[0].keys())
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    row_filtered = {k: row.get(k, '') for k in fieldnames}
                    writer.writerow(row_filtered)
            
            return True, f"导出成功: {filename}"
        except Exception as e:
            return False, f"导出失败: {str(e)}"
