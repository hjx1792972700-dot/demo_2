# Python ERP 系统开发计划

## 一、项目概述

### 1.1 项目名称
Python ERP 企业资源计划系统

### 1.2 项目目标
开发一个功能完整、易用的轻量级 ERP 系统，包含企业日常运营所需的核心功能模块，帮助中小企业实现信息化管理。

### 1.3 项目范围
- 用户管理与权限控制
- 产品管理
- 库存管理
- 采购管理
- 销售管理
- 报表统计与数据导出

## 二、技术架构

### 2.1 技术栈选择
| 组件 | 技术 | 说明 |
|------|------|------|
| 编程语言 | Python 3.8+ | 跨平台、生态丰富 |
| 数据库 | SQLite 3 | 本地文件数据库，无需额外安装 |
| GUI 框架 | Tkinter | Python 内置，无需额外安装依赖 |
| 数据导出 | CSV 格式 | 通用格式，便于数据分析 |

### 2.2 系统架构
采用分层架构设计：
1. **表现层（UI）**：Tkinter 窗口界面，负责用户交互
2. **业务逻辑层（Modules）**：各功能模块，处理业务逻辑
3. **数据访问层（Database）**：数据库管理和数据模型

### 2.3 项目目录结构
```
erp_system/
├── README.md              # 项目说明文档
├── plan.md               # 开发计划
├── main.py               # 程序入口
├── config.py             # 配置文件
├── database/
│   ├── __init__.py
│   ├── db_manager.py     # 数据库管理类（单例模式）
│   └── models.py         # 数据模型定义
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
│   ├── main_window.py    # 主窗口（菜单导航）
│   ├── login_window.py   # 登录窗口
│   ├── product_view.py    # 产品管理视图
│   ├── inventory_view.py  # 库存管理视图
│   ├── purchase_view.py   # 采购管理视图
│   ├── sales_view.py      # 销售管理视图
│   └── report_view.py     # 报表视图
└── data/
    └── erp.db            # SQLite 数据库文件（运行时生成）
```

## 三、开发阶段规划

### 阶段一：基础架构搭建（第1-2天）

#### 3.1.1 任务清单
- [ ] 创建项目目录结构
- [ ] 编写配置文件 config.py
- [ ] 实现数据库管理类 db_manager.py（单例模式）
- [ ] 设计并创建数据库表结构
- [ ] 实现数据模型 models.py

#### 3.1.2 数据库表设计

**1. 用户表 (users)**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'employee',  -- admin/manager/employee
    email TEXT,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**2. 产品分类表 (categories)**
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**3. 产品表 (products)**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    spec TEXT,                    -- 规格
    unit TEXT DEFAULT '个',        -- 单位
    cost_price REAL DEFAULT 0,     -- 成本价
    sale_price REAL DEFAULT 0,     -- 销售价
    safety_stock INTEGER DEFAULT 10, -- 安全库存
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

**4. 供应商表 (suppliers)**
```sql
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,                  -- 联系人
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**5. 客户表 (customers)**
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,                  -- 联系人
    phone TEXT,
    email TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**6. 库存表 (inventory)**
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER UNIQUE NOT NULL,
    quantity INTEGER DEFAULT 0,    -- 当前库存数量
    avg_cost REAL DEFAULT 0,        -- 平均成本
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**7. 采购单表 (purchase_orders)**
```sql
CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    total_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'draft',    -- draft/approved/completed/cancelled
    created_by INTEGER,             -- 创建人ID
    approved_by INTEGER,            -- 审批人ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);
```

**8. 采购单明细表 (purchase_order_items)**
```sql
CREATE TABLE purchase_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**9. 销售单表 (sales_orders)**
```sql
CREATE TABLE sales_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    total_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'draft',    -- draft/approved/completed/cancelled
    created_by INTEGER,             -- 创建人ID
    approved_by INTEGER,            -- 审批人ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (approved_by) REFERENCES users(id)
);
```

**10. 销售单明细表 (sales_order_items)**
```sql
CREATE TABLE sales_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sales_order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**11. 库存流水表 (inventory_transactions)**
```sql
CREATE TABLE inventory_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    type TEXT NOT NULL,             -- 'in' 入库 / 'out' 出库
    quantity INTEGER NOT NULL,
    before_quantity INTEGER NOT NULL,
    after_quantity INTEGER NOT NULL,
    reference_type TEXT,             -- 关联类型：purchase/sale/manual
    reference_id INTEGER,            -- 关联单据ID
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

#### 3.1.3 验收标准
- 项目目录结构完整
- 数据库管理类能够正常连接和操作 SQLite
- 所有数据库表能够成功创建
- 实现基本的 CRUD 操作接口

---

### 阶段二：核心模块开发（第3-5天）

#### 3.2.1 用户认证模块 (auth.py)

**功能需求：**
1. 用户登录验证
2. 用户密码加密存储（使用 SHA256 哈希）
3. 用户角色权限检查
4. 用户信息的增删改查
5. 当前登录用户的状态管理

**核心函数：**
- `login(username, password)` - 登录验证
- `logout()` - 登出
- `get_current_user()` - 获取当前登录用户
- `create_user(user_data)` - 创建用户
- `update_user(user_id, user_data)` - 更新用户
- `delete_user(user_id)` - 删除用户
- `get_user_by_id(user_id)` - 根据ID获取用户
- `get_all_users()` - 获取所有用户列表
- `check_permission(required_role)` - 检查权限

#### 3.2.2 产品管理模块 (product.py)

**功能需求：**
1. 产品分类的增删改查
2. 产品信息的增删改查
3. 产品的多条件查询（名称、分类、价格范围等）
4. 产品与库存的关联查询

**核心函数：**
- **分类管理：**
  - `create_category(name, description)` - 创建分类
  - `update_category(category_id, name, description)` - 更新分类
  - `delete_category(category_id)` - 删除分类
  - `get_category_by_id(category_id)` - 获取分类
  - `get_all_categories()` - 获取所有分类

- **产品管理：**
  - `create_product(product_data)` - 创建产品
  - `update_product(product_id, product_data)` - 更新产品
  - `delete_product(product_id)` - 删除产品
  - `get_product_by_id(product_id)` - 获取产品详情
  - `get_all_products()` - 获取所有产品
  - `search_products(keyword, category_id, min_price, max_price)` - 搜索产品

#### 3.2.3 库存管理模块 (inventory.py)

**功能需求：**
1. 产品入库处理
2. 产品出库处理
3. 库存数量查询
4. 库存预警检查（低于安全库存）
5. 库存流水记录查询

**核心函数：**
- `stock_in(product_id, quantity, unit_cost, reference_type, reference_id, user_id)` - 入库
- `stock_out(product_id, quantity, reference_type, reference_id, user_id)` - 出库
- `get_inventory_by_product(product_id)` - 获取产品库存
- `get_all_inventory()` - 获取所有库存
- `get_low_stock_products()` - 获取低库存产品
- `get_inventory_transactions(product_id, start_date, end_date)` - 获取库存流水
- `update_inventory_cost(product_id, new_quantity, new_cost)` - 更新库存成本（加权平均）

#### 3.2.4 采购管理模块 (purchase.py)

**功能需求：**
1. 供应商的增删改查
2. 采购单的创建、编辑、删除
3. 采购单的审批流程
4. 采购入库处理
5. 采购单查询与统计

**核心函数：**
- **供应商管理：**
  - `create_supplier(supplier_data)` - 创建供应商
  - `update_supplier(supplier_id, supplier_data)` - 更新供应商
  - `delete_supplier(supplier_id)` - 删除供应商
  - `get_supplier_by_id(supplier_id)` - 获取供应商
  - `get_all_suppliers()` - 获取所有供应商

- **采购单管理：**
  - `create_purchase_order(supplier_id, items, created_by)` - 创建采购单
  - `update_purchase_order(order_id, items)` - 更新采购单
  - `delete_purchase_order(order_id)` - 删除采购单（仅草稿状态）
  - `approve_purchase_order(order_id, approved_by)` - 审批采购单
  - `complete_purchase_order(order_id)` - 完成采购（执行入库）
  - `cancel_purchase_order(order_id)` - 取消采购单
  - `get_purchase_order_by_id(order_id)` - 获取采购单详情
  - `get_all_purchase_orders(status, supplier_id, start_date, end_date)` - 查询采购单
  - `get_purchase_statistics(start_date, end_date)` - 采购统计

#### 3.2.5 销售管理模块 (sales.py)

**功能需求：**
1. 客户的增删改查
2. 销售单的创建、编辑、删除
3. 销售单的审批流程
4. 销售出库处理
5. 销售单查询与统计

**核心函数：**
- **客户管理：**
  - `create_customer(customer_data)` - 创建客户
  - `update_customer(customer_id, customer_data)` - 更新客户
  - `delete_customer(customer_id)` - 删除客户
  - `get_customer_by_id(customer_id)` - 获取客户
  - `get_all_customers()` - 获取所有客户

- **销售单管理：**
  - `create_sales_order(customer_id, items, created_by)` - 创建销售单
  - `update_sales_order(order_id, items)` - 更新销售单
  - `delete_sales_order(order_id)` - 删除销售单（仅草稿状态）
  - `approve_sales_order(order_id, approved_by)` - 审批销售单
  - `complete_sales_order(order_id)` - 完成销售（执行出库）
  - `cancel_sales_order(order_id)` - 取消销售单
  - `get_sales_order_by_id(order_id)` - 获取销售单详情
  - `get_all_sales_orders(status, customer_id, start_date, end_date)` - 查询销售单
  - `get_sales_statistics(start_date, end_date)` - 销售统计

#### 3.2.6 报表模块 (report.py)

**功能需求：**
1. 库存报表生成
2. 采购报表生成
3. 销售报表生成
4. 利润分析报表
5. 数据导出为 CSV 格式

**核心函数：**
- `generate_inventory_report()` - 生成库存报表
- `generate_purchase_report(start_date, end_date)` - 生成采购报表
- `generate_sales_report(start_date, end_date)` - 生成销售报表
- `generate_profit_report(start_date, end_date)` - 生成利润分析报表
- `export_to_csv(data, filename)` - 导出数据到 CSV

#### 3.2.7 验收标准
- 所有模块的核心函数正常工作
- 数据库操作正确，数据一致性保证
- 模块间依赖关系正确
- 代码结构清晰，注释完整

---

### 阶段三：UI 界面开发（第6-7天）

#### 3.3.1 登录窗口 (login_window.py)

**界面组件：**
- 用户名输入框
- 密码输入框（隐藏显示）
- 登录按钮
- 错误提示标签

**功能逻辑：**
- 验证用户名和密码
- 登录成功后打开主窗口
- 登录失败显示错误信息

#### 3.3.2 主窗口 (main_window.py)

**界面组件：**
- 菜单栏（文件、编辑、帮助）
- 左侧导航栏（功能模块菜单）
  - 产品管理
  - 库存管理
  - 采购管理
  - 销售管理
  - 报表统计
  - 用户管理（仅管理员可见）
- 右侧内容区域（显示选中的功能模块）
- 底部状态栏（显示当前用户、登录时间等）

**功能逻辑：**
- 根据用户角色显示/隐藏菜单
- 左侧菜单点击切换右侧内容
- 集成所有子视图

#### 3.3.3 产品管理视图 (product_view.py)

**界面组件：**
- 产品列表（Treeview 表格）
  - 列：ID、名称、分类、规格、单位、成本价、销售价、安全库存、库存数量
- 功能按钮区
  - 添加产品
  - 编辑产品
  - 删除产品
  - 刷新列表
- 搜索筛选区
  - 产品名称输入框
  - 分类下拉选择框
  - 价格范围输入框（最小/最大）
  - 搜索按钮
  - 重置按钮

**弹窗对话框：**
- 添加/编辑产品对话框
- 删除确认对话框

#### 3.3.4 库存管理视图 (inventory_view.py)

**界面组件：**
- 库存列表（Treeview 表格）
  - 列：产品ID、产品名称、规格、单位、当前库存、平均成本、库存价值、最后更新时间
- 功能按钮区
  - 入库登记
  - 出库登记
  - 查看流水
  - 库存预警检查
  - 刷新列表
- 库存预警提示区（显示低库存产品）

**弹窗对话框：**
- 入库登记对话框（产品选择、数量、单价）
- 出库登记对话框（产品选择、数量）
- 库存流水查看对话框（表格显示流水记录）

#### 3.3.5 采购管理视图 (purchase_view.py)

**Tab 页设计：**
1. **采购单管理** Tab
2. **供应商管理** Tab

**采购单管理 Tab：**
- 采购单列表（Treeview 表格）
  - 列：单号、供应商、总金额、状态、创建人、创建时间、审批人、审批时间
- 功能按钮区
  - 新建采购单
  - 编辑采购单
  - 删除采购单
  - 审批采购单
  - 完成采购（入库）
  - 取消采购单
  - 查看详情
  - 刷新列表
- 筛选区
  - 状态下拉选择
  - 日期范围选择
  - 搜索按钮

**供应商管理 Tab：**
- 供应商列表（Treeview 表格）
  - 列：ID、名称、联系人、电话、邮箱、地址
- 功能按钮区
  - 添加供应商
  - 编辑供应商
  - 删除供应商
  - 刷新列表

**弹窗对话框：**
- 新建/编辑采购单对话框（供应商选择、产品明细表格）
- 采购单详情对话框
- 添加/编辑供应商对话框

#### 3.3.6 销售管理视图 (sales_view.py)

**Tab 页设计：**
1. **销售单管理** Tab
2. **客户管理** Tab

**销售单管理 Tab：**
- 销售单列表（Treeview 表格）
  - 列：单号、客户、总金额、状态、创建人、创建时间、审批人、审批时间
- 功能按钮区
  - 新建销售单
  - 编辑销售单
  - 删除销售单
  - 审批销售单
  - 完成销售（出库）
  - 取消销售单
  - 查看详情
  - 刷新列表
- 筛选区
  - 状态下拉选择
  - 日期范围选择
  - 搜索按钮

**客户管理 Tab：**
- 客户列表（Treeview 表格）
  - 列：ID、名称、联系人、电话、邮箱、地址
- 功能按钮区
  - 添加客户
  - 编辑客户
  - 删除客户
  - 刷新列表

**弹窗对话框：**
- 新建/编辑销售单对话框（客户选择、产品明细表格）
- 销售单详情对话框
- 添加/编辑客户对话框

#### 3.3.7 报表视图 (report_view.py)

**Tab 页设计：**
1. **库存报表** Tab
2. **采购报表** Tab
3. **销售报表** Tab
4. **利润分析** Tab

**公共组件：**
- 日期范围选择器
- 生成报表按钮
- 导出 CSV 按钮
- 报表数据表格（Treeview）

**各 Tab 功能：**
- **库存报表**：显示所有产品的库存数量、价值、成本等
- **采购报表**：按时间段统计采购金额、数量、趋势
- **销售报表**：按时间段统计销售金额、数量、趋势
- **利润分析**：显示销售利润、成本、毛利率等

#### 3.3.8 验收标准
- 所有 UI 窗口能够正常显示
- 界面布局合理，操作流畅
- 所有按钮和输入框响应正常
- 数据能够正确显示和更新

---

### 阶段四：集成测试与优化（第8天）

#### 3.4.1 集成测试
- 测试完整的业务流程：
  1. 管理员登录
  2. 创建产品分类和产品
  3. 创建供应商
  4. 创建采购单 → 审批 → 完成（入库）
  5. 创建客户
  6. 创建销售单 → 审批 → 完成（出库）
  7. 查看库存流水
  8. 生成报表并导出

#### 3.4.2 边界情况测试
- 空数据输入测试
- 负数数量测试
- 库存不足时出库测试
- 非法字符输入测试
- 权限测试（不同角色的访问限制）

#### 3.4.3 优化内容
- 代码性能优化
- 用户体验优化（添加加载提示、确认对话框等）
- 错误处理完善（try-except 捕获异常）
- 日志记录（关键操作记录日志）

#### 3.4.4 验收标准
- 完整业务流程测试通过
- 边界情况处理正确
- 无明显性能问题
- 用户体验良好

## 四、角色权限设计

### 4.1 角色定义

| 角色 | 权限说明 |
|------|----------|
| **admin（管理员）** | 拥有系统所有权限，包括用户管理 |
| **manager（经理）** | 拥有采购、销售、库存管理权限，可审批单据 |
| **employee（员工）** | 拥有基本查询权限，可创建草稿单据 |

### 4.2 权限矩阵

| 功能模块 | admin | manager | employee |
|----------|-------|---------|----------|
| 用户管理 | ✅ | ❌ | ❌ |
| 产品管理（增删改查） | ✅ | ✅ | 仅查询 |
| 库存查询 | ✅ | ✅ | ✅ |
| 入库登记 | ✅ | ✅ | ❌ |
| 出库登记 | ✅ | ✅ | ❌ |
| 供应商管理 | ✅ | ✅ | 仅查询 |
| 采购单创建 | ✅ | ✅ | ✅ |
| 采购单审批 | ✅ | ✅ | ❌ |
| 采购单完成 | ✅ | ✅ | ❌ |
| 客户管理 | ✅ | ✅ | 仅查询 |
| 销售单创建 | ✅ | ✅ | ✅ |
| 销售单审批 | ✅ | ✅ | ❌ |
| 销售单完成 | ✅ | ✅ | ❌ |
| 报表查看 | ✅ | ✅ | ✅ |
| 数据导出 | ✅ | ✅ | ❌ |

## 五、数据初始化

### 5.1 默认数据

系统首次运行时自动创建以下数据：

1. **默认管理员账号**
   - 用户名：`admin`
   - 密码：`admin123`（SHA256 加密）
   - 角色：`admin`

2. **示例产品分类**
   - 电子产品
   - 办公用品
   - 生活用品

3. **示例产品**（可选，用于演示）

### 5.2 初始化流程
1. 检查数据库是否存在
2. 不存在则创建所有表
3. 检查是否已有管理员账号
4. 没有则创建默认管理员
5. 创建示例分类（可选）

## 六、风险与应对措施

### 6.1 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| SQLite 并发性能 | 低 | 中 | 本系统为单机应用，并发少；添加事务处理 |
| 数据丢失 | 中 | 高 | 定期提示用户备份数据库文件 |
| 权限漏洞 | 中 | 中 | 在所有关键操作前验证用户权限 |

### 6.2 进度风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| UI 开发耗时超出预期 | 中 | 中 | 简化部分界面，优先保证核心功能 |
| 业务逻辑复杂度过高 | 中 | 高 | 分阶段实现，先做核心流程 |

## 七、交付物清单

### 7.1 代码文件
- [ ] `main.py` - 程序入口
- [ ] `config.py` - 配置文件
- [ ] `database/__init__.py`
- [ ] `database/db_manager.py`
- [ ] `database/models.py`
- [ ] `modules/__init__.py`
- [ ] `modules/auth.py`
- [ ] `modules/product.py`
- [ ] `modules/inventory.py`
- [ ] `modules/purchase.py`
- [ ] `modules/sales.py`
- [ ] `modules/report.py`
- [ ] `ui/__init__.py`
- [ ] `ui/main_window.py`
- [ ] `ui/login_window.py`
- [ ] `ui/product_view.py`
- [ ] `ui/inventory_view.py`
- [ ] `ui/purchase_view.py`
- [ ] `ui/sales_view.py`
- [ ] `ui/report_view.py`

### 7.2 文档文件
- [ ] `README.md` - 项目说明文档
- [ ] `plan.md` - 开发计划文档

### 7.3 运行文件
- [ ] `data/erp.db` - 数据库文件（运行时自动生成）

## 八、测试计划

### 8.1 单元测试
- 测试各模块的核心函数
- 测试数据库 CRUD 操作
- 测试权限检查逻辑

### 8.2 集成测试
- 测试完整业务流程
- 测试模块间数据传递
- 测试 UI 与业务逻辑的交互

### 8.3 用户验收测试
- 使用默认管理员账号登录
- 执行完整的采购-入库-销售-出库流程
- 验证报表数据的正确性
- 验证权限控制的有效性

## 九、维护计划

### 9.1 代码维护
- 定期检查代码优化点
- 修复发现的 Bug
- 添加日志记录便于排查问题

### 9.2 数据维护
- 提示用户定期备份数据库
- 提供数据库压缩优化建议

### 9.3 功能扩展（可选）
- 添加更多报表类型
- 支持数据导入
- 添加数据图表展示
- 支持多语言

---

**开发周期：8 个工作日**

**预计完成日期：从开始日起第 8 天**

**状态：开发中**
