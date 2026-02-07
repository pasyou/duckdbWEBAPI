# DuckDB 并发 Web API 项目

基于 DuckDB 的高性能并发 Web API 项目，支持多节点数据同步和并发查询。

## 项目特性

- **多节点架构**: 支持 8 个 DuckDB 节点，主节点负责写入，从节点负责读取
- **按月分库**: 支持按月份自动分库，数据存储在 `data/YYYY-MM/` 目录下，实现数据隔离
- **增量同步**: 自动追踪数据变更，实时同步到所有从节点
- **并发查询**: 使用线程池实现并发查询，提升查询性能
- **异步操作**: 支持异步增删改查操作，提高系统并发能力
- **RESTful API**: 基于 FastAPI 提供完整的 RESTful 接口
- **高性能**: 查询响应时间平均 5ms，每秒可处理 200+ 查询
- **自动 ID 生成**: 插入操作时自动生成唯一 ID，确保数据一致性
- **智能查询路由**: 查询操作自动从备库（1-7）中随机选择节点，分散查询负载
- **多月份管理**: 支持同时管理多个月份的数据库实例，实现历史数据查询和未来数据预置

## 项目结构

```
duckdb/
├── src/
│   ├── main.py                      # FastAPI 主应用
│   └── DuckDBIncrementalSync.py     # DuckDB 并发管理器
├── data/                            # 数据库文件目录
│   ├── 2026-01/                     # 2026年1月数据
│   │   ├── node_0.db                # 主节点
│   │   ├── node_1.db                # 从节点1
│   │   └── ...                      # 其他从节点
│   ├── 2026-02/                     # 2026年2月数据
│   └── ...                          # 其他月份
├── venv/                            # Python 虚拟环境
├── requirements.txt                 # 项目依赖
├── start.bat                        # 启动脚本
├── DuckDBWebAPI.spec               # PyInstaller 打包配置
├── dist/                            # 打包输出目录
│   └── DuckDBWebAPI.exe          # 独立可执行文件
├── test_concurrent_query.py         # 并发查询测试脚本
├── test_monthly_partitioning.py     # 按月分库功能测试脚本
├── test_delete_insert_query.py      # 删除插入查询测试脚本
├── test_query.py                    # 查询测试脚本
├── test_simple_insert.py            # 简单插入测试脚本
└── README.md                        # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
python src/main.py
```

服务将在 http://localhost:8000 启动

### 3. 运行测试

```bash
python test_concurrent.py
python test_async_modification.py
```

## API 接口

### 基础接口

- `GET /` - API 信息和端点列表
- `GET /health` - 健康检查
- `GET /docs` - API 文档（Swagger UI）

### 同步管理

- `POST /api/v1/sync` - 触发增量同步
  - 请求参数: `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份

### 查询接口

- `POST /api/v1/query` - 执行自定义查询（异步，返回查询ID）
  - 请求参数: `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份
- `POST /api/v1/query/async` - 执行自定义查询（异步，直接返回结果）
  - 请求参数: 
    - `month` (可选) - 指定单个月份，格式为 YYYY-MM
    - `months` (可选) - 指定多个月份，格式为 `["2026-01", "2026-02"]`
    - `all_months` (可选) - 布尔值，设置为 `true` 查询所有可用月份
  - **跨月查询**: 支持同时查询多个月份的数据，返回合并后的结果
- `GET /api/v1/query/result/{query_id}` - 获取查询结果
  - 查询参数: `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份

### 数据修改接口

- `POST /api/v1/modify/async` - 执行增删改操作（异步）
  - 请求参数: 
    - `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份
    - `exec` - SQL 语句
    - `params` (可选) - 单条操作的参数数组
    - `is_batch` (可选) - 是否为批量操作，默认为 false
    - `batch_params` (可选) - 批量操作的参数数组，当 `is_batch` 为 true 时使用
  - **批量插入**: 支持批量插入操作，提高数据插入效率

### 数据表管理

- `POST /api/v1/tables` - 创建数据表
  - 请求参数: `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份
- `GET /api/v1/tables` - 查询库中所有表
  - 查询参数: `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份
- `GET /api/v1/tables/{table_name}/schema` - 查询表结构
  - 查询参数: `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份

### 节点管理

- `GET /api/v1/nodes` - 获取所有节点状态
  - 查询参数: `month` (可选) - 指定月份，格式为 YYYY-MM，默认为当前月份
- `GET /api/v1/months` - 获取所有可用月份列表

> **注意**: 所有接口都支持 `month` 参数，用于指定操作的月份。如果不提供 `month` 参数，则默认使用当前月份。月份格式为 `YYYY-MM`，例如 `2026-01`、`2026-02` 等。

## 使用示例

### 执行修改操作（异步）

```bash
curl -X POST http://localhost:8000/api/v1/modify/async \
  -H "Content-Type: application/json" \
  -d '{
    "exec": "UPDATE products SET price = ?, stock = ? WHERE id = ?",
    "params": [6999.99, 50, 1]
  }'
```

### 执行查询（异步）

```bash
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM users LIMIT 10"}'
```

> **注意**: 查询操作会自动从备库（1-7）中随机选择一个节点进行查询，分散查询负载。

### 查看节点状态

```bash
curl http://localhost:8000/api/v1/nodes
```

### 创建数据表

```bash
curl -X POST http://localhost:8000/api/v1/tables \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "employees",
    "columns": [
      {"name": "id", "type": "BIGINT PRIMARY KEY"},
      {"name": "name", "type": "VARCHAR"},
      {"name": "position", "type": "VARCHAR"},
      {"name": "salary", "type": "DECIMAL(10,2)"},
      {"name": "hire_date", "type": "TIMESTAMP"}
    ]
  }'
```

### 查询表结构

```bash
curl http://localhost:8000/api/v1/tables/users/schema
```

```bash
curl http://localhost:8000/api/v1/tables/products/schema
```

```bash
curl http://localhost:8000/api/v1/tables/employees/schema
```

### 查询库中所有表

```bash
curl http://localhost:8000/api/v1/tables
```

### 按月分库功能示例

#### 获取可用月份列表

```bash
curl http://localhost:8000/api/v1/months
```

#### 在指定月份执行修改操作

```bash
# 在当前月份插入数据
curl -X POST http://localhost:8000/api/v1/modify/async \
  -H "Content-Type: application/json" \
  -d '{
    "exec": "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
    "params": ["新产品", 99.99, 50]
  }'

# 在指定月份（2026-01）插入数据
curl -X POST http://localhost:8000/api/v1/modify/async \
  -H "Content-Type: application/json" \
  -d '{
    "exec": "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
    "params": ["历史产品", 88.88, 30],
    "month": "2026-01"
  }'

# 在指定月份（2026-03）插入数据（未来月份）
curl -X POST http://localhost:8000/api/v1/modify/async \
  -H "Content-Type: application/json" \
  -d '{
    "exec": "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
    "params": ["未来产品", 199.99, 100],
    "month": "2026-03"
  }'
```

#### 批量插入数据

```bash
# 批量插入用户数据
curl -X POST http://localhost:8000/api/v1/modify/async \
  -H "Content-Type: application/json" \
  -d '{
    "exec": "INSERT INTO users (name, email) VALUES (?, ?)",
    "is_batch": true,
    "batch_params": [
      ["用户1", "user1@example.com"],
      ["用户2", "user2@example.com"],
      ["用户3", "user3@example.com"],
      ["用户4", "user4@example.com"],
      ["用户5", "user5@example.com"]
    ]
  }'

# 批量插入产品数据到指定月份
curl -X POST http://localhost:8000/api/v1/modify/async \
  -H "Content-Type: application/json" \
  -d '{
    "exec": "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
    "is_batch": true,
    "month": "2026-01",
    "batch_params": [
      ["产品A", 99.99, 100],
      ["产品B", 199.99, 50],
      ["产品C", 299.99, 30],
      ["产品D", 399.99, 20],
      ["产品E", 499.99, 10]
    ]
  }'

# 批量插入订单数据
curl -X POST http://localhost:8000/api/v1/modify/async \
  -H "Content-Type: application/json" \
  -d '{
    "exec": "INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?)",
    "is_batch": true,
    "batch_params": [
      [1, 199.99, "pending"],
      [2, 299.99, "shipped"],
      [3, 399.99, "delivered"],
      [4, 499.99, "pending"],
      [5, 599.99, "shipped"]
    ]
  }'
```

##### 批量插入响应格式

批量插入返回的响应格式如下：

```json
{
  "status": "success",
  "batch": true,
  "total_operations": 5,
  "successful_operations": 5,
  "failed_operations": 0,
  "errors": null,
  "timestamp": "2026-02-07T14:00:00.000000"
}
```

响应字段说明：
- `status`: 操作状态，`success` 表示全部成功，`partial_success` 表示部分成功
- `batch`: 标识是否为批量操作
- `total_operations`: 总操作数
- `successful_operations`: 成功操作数
- `failed_operations`: 失败操作数
- `errors`: 失败操作的错误信息数组
- `timestamp`: 操作时间戳

##### 批量插入优势

- **高性能**: 使用异步并发执行，大幅提升插入效率
- **原子性**: 每个操作独立执行，互不影响
- **容错性**: 部分失败不影响其他操作
- **统计信息**: 提供详细的成功/失败统计
- **错误追踪**: 记录每个失败操作的详细信息

#### 获取指定月份的节点状态

```bash
# 获取当前月份的节点状态
curl http://localhost:8000/api/v1/nodes

# 获取指定月份（2026-01）的节点状态
curl "http://localhost:8000/api/v1/nodes?month=2026-01"

# 获取指定月份（2026-02）的节点状态
curl "http://localhost:8000/api/v1/nodes?month=2026-02"
```

#### 在指定月份创建数据表

```bash
# 在当前月份创建表
curl -X POST http://localhost:8000/api/v1/tables \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "orders",
    "columns": [
      {"name": "order_id", "type": "BIGINT PRIMARY KEY"},
      {"name": "customer_id", "type": "BIGINT"},
      {"name": "total_amount", "type": "DECIMAL(10,2)"},
      {"name": "order_date", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
      {"name": "status", "type": "VARCHAR"}
    ]
  }'

# 在指定月份（2026-01）创建表
curl -X POST http://localhost:8000/api/v1/tables \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "orders",
    "columns": [
      {"name": "order_id", "type": "BIGINT PRIMARY KEY"},
      {"name": "customer_id", "type": "BIGINT"},
      {"name": "total_amount", "type": "DECIMAL(10,2)"},
      {"name": "order_date", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
      {"name": "status", "type": "VARCHAR"}
    ],
    "month": "2026-01"
  }'
```

#### 跨月数据统计示例

```bash
# 统计当前月份的用户数量
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) as user_count FROM users"}'

# 统计2026年1月的用户数量
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) as user_count FROM users", "month": "2026-01"}'

# 统计2026年2月的用户数量
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) as user_count FROM users", "month": "2026-02"}'
```

#### 跨月查询示例

##### 查询多个月份的数据

```bash
# 查询指定多个月份（2026-01 和 2026-02）的用户
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM users",
    "months": ["2026-01", "2026-02"]
  }'

# 查询指定多个月份（2026-01、2026-02 和 2026-03）的用户
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM users",
    "months": ["2026-01", "2026-02", "2026-03"]
  }'
```

##### 查询所有月份的数据

```bash
# 查询所有可用月份的用户数据
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM users",
    "all_months": true
  }'

# 查询所有可用月份的产品数据
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM products",
    "all_months": true
  }'
```

##### 跨月统计查询

```bash
# 统计多个月份的用户数量
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT COUNT(*) as user_count FROM users",
    "months": ["2026-01", "2026-02", "2026-03"]
  }'

# 统计所有月份的用户总数
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT COUNT(*) as user_count FROM users",
    "all_months": true
  }'

# 查询多个月份的订单总金额
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT SUM(total_amount) as total FROM orders",
    "months": ["2026-01", "2026-02"]
  }'
```

##### 跨月数据分析

```bash
# 查询多个月份的用户活跃度
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT COUNT(*) as active_users FROM users WHERE created_at > \"2026-01-01\"",
    "months": ["2026-01", "2026-02", "2026-03"]
  }'

# 查询所有月份的产品销售趋势
curl -X POST http://localhost:8000/api/v1/query/async \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT name, stock FROM products WHERE stock < 50",
    "all_months": true
  }'
```

##### 跨月查询响应格式

跨月查询返回的响应格式如下：

```json
{
  "cross_month": true,
  "months_queried": ["2026-01", "2026-02", "2026-03"],
  "total_months": 3,
  "successful_months": 3,
  "results": [
    {
      "month": "2026-01",
      "results": [...],
      "completed": true,
      "timestamp": "2026-02-07T12:00:00.000000"
    },
    {
      "month": "2026-02",
      "results": [...],
      "completed": true,
      "timestamp": "2026-02-07T12:00:00.000000"
    },
    {
      "month": "2026-03",
      "results": [...],
      "completed": true,
      "timestamp": "2026-02-07T12:00:00.000000"
    }
  ],
  "timestamp": "2026-02-07T12:00:00.000000"
}
```

响应字段说明：
- `cross_month`: 标识是否为跨月查询
- `months_queried`: 查询的月份列表
- `total_months`: 查询的总月份数
- `successful_months`: 成功查询的月份数
- `results`: 每个月份的查询结果数组
- `timestamp`: 查询时间戳

## 性能指标

测试环境：4 节点，2 线程池

- **并发插入**: 100 条记录，平均 0.0167 秒/条
- **并发查询**: 平均响应时间 5ms
- **查询吞吐量**: 每秒 200+ 查询
- **同步延迟**: < 1 秒
- **异步操作**: 平均响应时间 < 20ms

## 按月分库优势

### 数据隔离
- 每个月份的数据完全独立，互不干扰
- 避免单表数据量过大导致的性能问题
- 便于数据备份和恢复

### 历史数据查询
- 可以快速查询任意历史月份的数据
- 支持跨月数据统计和分析
- 历史数据不会影响当前月份的性能

### 未来数据预置
- 可以提前创建未来月份的数据库
- 支持数据预加载和预热
- 便于业务规划和预测

### 灵活的数据管理
- 可以单独删除或归档某个月份的数据
- 支持不同月份使用不同的表结构
- 便于实现数据生命周期管理

### 跨月查询能力
- 支持同时查询多个月份的数据
- 支持查询所有可用月份的数据
- 自动合并多个月份的查询结果
- 提供跨月统计和分析能力

### 应用场景
- **电商订单管理**: 按月存储订单数据，便于月度统计和分析
- **日志系统**: 按月存储日志数据，便于日志查询和归档
- **财务系统**: 按月存储财务数据，便于月度报表和审计
- **用户行为分析**: 按月存储用户行为数据，便于趋势分析
- **数据仓库**: 按月分区存储数据，提高查询性能和管理效率

## 技术栈

- **DuckDB**: 高性能分析型数据库
- **FastAPI**: 现代化 Web 框架
- **Uvicorn**: ASGI 服务器
- **Pydantic**: 数据验证
- **Threading**: 多线程并发处理
- **Asyncio**: 异步操作支持

## 配置说明

在 [main.py](src/main.py#L8) 中可以配置：

```python
sync_manager = DuckDBIncrementalSync(
    num_nodes=8,        # 节点数量
    data_dir='data',    # 数据目录
    max_workers=4       # 线程池大小
)
```

### 按月分库配置

系统支持按月分库，数据存储结构如下：

```
data/
├── 2026-01/          # 2026年1月数据
│   ├── node_0.db     # 主节点
│   ├── node_1.db     # 从节点1
│   └── ...           # 其他从节点
├── 2026-02/          # 2026年2月数据
│   ├── node_0.db     # 主节点
│   ├── node_1.db     # 从节点1
│   └── ...           # 其他从节点
└── ...               # 其他月份
```

### 月份参数说明

- **格式**: `YYYY-MM`，例如 `2026-01`、`2026-02`
- **默认值**: 当前月份
- **用途**: 指定操作的月份，实现数据隔离和历史数据查询

### 多月份管理

系统使用 `get_sync_manager(month)` 函数管理多个月份的数据库实例：

- 每个月份都有独立的8个节点（1主7从）
- 月份之间数据完全隔离
- 支持历史数据查询和未来数据预置
- 首次访问某个月份时自动创建数据库文件

## 注意事项

1. 首次运行会自动创建数据库文件和表结构
2. 数据存储在 `data/` 目录下，按月份分目录存储
3. 建议定期清理 `data/` 目录以释放空间
4. 生产环境建议使用更严格的访问控制
5. 异步操作适用于高并发场景，同步操作适用于简单场景
6. 按月分库功能：
   - 每个月份的数据完全独立，互不影响
   - 可以查询历史月份的数据
   - 可以预置未来月份的数据
   - 不同月份的表结构可能不同
7. 月份参数格式必须为 `YYYY-MM`，例如 `2026-01`
8. 如果不指定月份参数，系统默认使用当前月份

## 打包成独立 EXE 应用

### 打包说明

项目已配置好 PyInstaller 打包配置文件 `DuckDBWebAPI.spec`，可以直接打包成独立的 EXE 应用。

### 打包步骤

1. **安装 PyInstaller**（如果未安装）：
   ```bash
   pip install pyinstaller
   ```

2. **执行打包命令**：
   ```bash
   pyinstaller DuckDBWebAPI.spec --clean
   ```

3. **打包完成后**：
   - EXE 文件位置：`dist/DuckDBWebAPI.exe`
   - 打包配置文件：`DuckDBWebAPI.spec`

### 使用 EXE 文件

**启动服务**：
- 双击 `dist/DuckDBWebAPI.exe` 启动服务
- 服务会自动检查 8000 端口，如果被占用则关闭相关进程
- 服务启动后自动打开浏览器访问 `http://127.0.0.1:8000/docs`

**EXE 特性**：
- 独立可执行文件，无需安装 Python 环境
- 包含所有必要的依赖库和源代码
- 自动处理端口占用问题
- 启动时自动打开 API 文档页面
- 数据文件自动创建在 `data/` 目录下

**注意事项**：
- 首次运行会自动创建数据库文件
- 可以直接复制 EXE 文件到其他机器上运行
- 确保目标机器有足够的磁盘空间存储数据
- 防火墙可能需要允许 8000 端口的访问

## GitHub Actions 自动打包

### 自动打包配置

项目已配置 GitHub Actions 自动打包工作流，当代码推送到 `main` 分支或创建 Pull Request 时，会自动执行以下操作：

1. **环境设置**: 使用 Windows Server 2022 环境
2. **Python 安装**: 安装 Python 3.12
3. **依赖安装**: 安装项目依赖和 PyInstaller
4. **打包构建**: 执行 `pyinstaller DuckDBWebAPI.spec --clean` 命令
5. **产物上传**: 将打包生成的 EXE 文件上传为 Artifact

### 工作流配置

工作流配置文件位于 `.github/workflows/build.yml`，包含以下关键配置：

- **触发条件**: `push` 到 `main` 分支、`pull_request` 到 `main` 分支、手动触发
- **运行环境**: `windows-latest`
- **Python 版本**: `3.12`
- **产物保留**: 7 天

### 如何使用

1. **代码推送**: 推送到 `main` 分支的代码会自动触发打包
2. **Pull Request**: 创建到 `main` 分支的 PR 会自动执行打包测试
3. **手动触发**: 可以在 GitHub 仓库的 Actions 标签页手动触发工作流

### 打包产物

打包完成后，会生成以下产物：

- **Artifact 名称**: `DuckDBWebAPI`
- **包含文件**: `dist/DuckDBWebAPI.exe`
- **下载方式**: 在 Actions 运行结果页面下载 Artifact

### 优势

- **自动化**: 无需手动执行打包命令
- **一致性**: 每次打包使用相同的环境和配置
- **可靠性**: 自动测试打包过程，确保产物可用
- **便捷性**: 可直接从 GitHub 下载最新打包的 EXE 文件

## 许可证

MIT License
