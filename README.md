# Python ERP 系统

一个基于 Python 的轻量级企业资源计划（ERP）系统，使用 SQLite 本地数据库。

## 项目简介

本项目是一个功能完整的 ERP 系统，包含企业日常运营所需的核心功能模块，采用简洁易用，适合中小企业使用。

## 功能模块

### 1. 用户管理模块
- 用户注册与登录
- 用户角色管理（管理员、经理、员工）
- 用户权限控制
- 用户信息修改

### 2. 产品管理模块
- 产品信息增删改查
- 产品分类管理
- 产品库存查询
- 产品价格管理

### 3. 库存管理模块
- 入库登记
- 出库登记
- 库存盘点
- 库存预警（低库存提醒）
- 库存流水记录

### 4. 采购管理模块
- 供应商管理
- 采购订单创建
- 采购订单审批
- 采购入库
- 采购报表统计

### 5. 销售管理模块
- 客户管理
- 销售订单创建
- 销售订单审批
- 销售出库
- 销售报表统计

### 6. 报表统计模块
- 库存报表
- 采购报表
- 销售报表
- 利润分析报表
- 数据导出（CSV格式）

## 技术栈

- **编程语言**: Python 3.8+
- **数据库**: SQLite3（本地文件数据库）
- **GUI框架**: Tkinter（Python内置，无需额外安装）
- **数据处理**: csv（内置模块）

## 项目结构

```
erp_system/
├── README.md              # 项目说明文档
├── plan.md               # 开发计划
├── main.py               # 程序入口
├── config.py             # 配置文件
├── database/
│   ├── __init__.py
│   ├── db_manager.py     # 数据库管理类
│   └── models.py         # 数据模型
├── modules/
│   ├── __init__.py
│   ├── auth.py           # 用户认证模块
│   ├── product.py        # 产品管理模块
│   ├── inventory.py      # 库存管理模块
│   ├── purchase.py       # 采购管理模块
│   ├── sales.py          # 销售管理模块
│   └── report.py         # 报表模块
├── ui/
│   ├── __init__.py
│   ├── main_window.py    # 主窗口
│   ├── login_window.py   # 登录窗口
│   ├── product_view.py    # 产品视图
│   ├── inventory_view.py  # 库存视图
│   ├── purchase_view.py   # 采购视图
│   ├── sales_view.py      # 销售视图
│   └── report_view.py     # 报表视图
└── data/
    └── erp.db            # SQLite数据库文件（运行时生成）
```

## 安装与运行

### 环境要求
- Python 3.8 或更高版本
- pip（Python包管理器）

### 安装步骤

1. 克隆或下载项目到本地
2. 进入项目目录
3. 无需安装依赖（本项目使用Python内置库，无需额外安装）

### 运行程序

```bash
python main.py
```

首次运行会自动创建数据库文件和必要的表结构。

## 默认账号

系统首次运行会创建一个管理员账号：
- 用户名: `admin`
- 密码: `admin123`

建议首次登录后立即修改密码。

## 功能说明

### 登录界面
- 输入用户名和密码登录系统
- 根据用户角色显示不同的功能菜单
- 管理员拥有全部权限
- 经理拥有采购、销售、库存管理权限
- 员工拥有基本查询权限

### 产品管理
- 添加新产品：填写产品名称、分类、规格、单位、成本价、销售价等信息
- 编辑产品：修改已有产品信息
- 删除产品：删除不需要的产品（有库存或订单关联的产品不能删除）
- 查询产品：按名称、分类、价格范围等条件查询

### 库存管理
- 入库登记：记录产品入库（采购入库、退货入库等）
- 出库登记：记录产品出库（销售出库、领用出库等）
- 库存查询：查看当前库存数量、库存价值
- 库存预警：库存数量低于安全库存时自动提醒
- 库存流水：查看所有出入库记录

### 采购管理
- 供应商管理：添加、编辑、删除、查询供应商信息
- 创建采购单：选择供应商、产品、数量、价格
- 审批采购单：经理或管理员审批采购单
- 采购入库：采购单审批通过后，执行入库
- 采购报表：按时间段、供应商、产品等统计采购数据

### 销售管理
- 客户管理：添加、编辑、删除、查询客户信息
- 创建销售单：选择客户、产品、数量、价格
- 审批销售单：经理或管理员审批销售单
- 销售出库：销售单审批通过后，执行出库
- 销售报表：按时间段、客户、产品等统计销售数据

### 报表统计
- 库存报表：库存数量、库存价值、库存周转率
- 采购报表：采购金额、采购数量、采购趋势
- 销售报表：销售金额、销售数量、销售趋势、利润
- 数据导出：支持将报表数据导出为CSV文件

## 数据库设计

### 主要数据表：

1. **users**（用户表）
   - id, username, password, role, email, phone, created_at

2. **categories**（产品分类表）
   - id, name, description, created_at

3. **products**（产品表）
   - id, name, category_id, spec, unit, cost_price, sale_price, safety_stock, created_at

4. **suppliers**（供应商表）
   - id, name, contact, phone, email, address, created_at

5. **customers**（客户表）
   - id, name, contact, phone, email, address, created_at

6. **inventory**（库存表）
   - id, product_id, quantity, avg_cost, last_update

7. **purchase_orders**（采购单表）
   - id, supplier_id, total_amount, status, created_by, approved_by, created_at, approved_at

8. **purchase_order_items**（采购单明细表）
   - id, purchase_order_id, product_id, quantity, unit_price, total_price

9. **sales_orders**（销售单表）
   - id, customer_id, total_amount, status, created_by, approved_by, created_at, approved_at

10. **sales_order_items**（销售单明细表）
    - id, sales_order_id, product_id, quantity, unit_price, total_price

11. **inventory_transactions**（库存流水表）
    - id, product_id, type(in/out), quantity, before_quantity, after_quantity, reference_type, reference_id, created_by, created_at

## 注意事项

1. 本系统使用本地SQLite数据库，数据存储在 `data/erp.db` 文件中，建议定期备份该文件。

2. 首次登录请使用默认管理员账号，登录后请及时修改密码。

3. 系统中的所有操作都会记录在数据库中，便于追溯。

4. 建议定期导出报表数据，便于数据分析和备份。

## 开发说明

本项目采用面向对象的设计思想，模块化结构清晰，便于维护和扩展。

主要设计模式：
- 单例模式：数据库连接管理
- MVC模式：数据模型、视图、控制器分离
- 工厂模式：创建不同类型的窗口对象

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发者。
