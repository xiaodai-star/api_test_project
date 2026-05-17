我直接给你**排版精修好、可直接复制进 README.md 的 Markdown 版本**，结构清晰、层级分明、GitHub 预览超好看，你直接全选复制替换就行：

```markdown
# api_test_project
基于 FastAPI + MySQL + pytest 的用户管理接口自动化测试项目

## 项目目录结构
```
api_test_project/
├── api/                # 接口模块
│   └── user_api.py     # 用户CRUD、登录、注册接口
├── config/             # 配置文件
│   ├── config.py       # 数据库/JWT配置
│   └── db.py           # 数据库连接
├── tests/              # 自动化测试用例
│   └── test_user_api.py# 完整接口测试
├── sql/                # 建库建表语句
├── main.py             # 项目入口
├── requirements.txt    # 依赖包
├── README.md           # 项目说明
└── report.html         # 测试报告
```

## 技术栈
- FastAPI：接口开发
- MySQL：数据存储
- SQLAlchemy：数据库操作
- PyJWT：登录鉴权
- pytest + requests：接口自动化测试
- pytest-html：测试报告生成

## 功能说明
- 用户注册（校验用户名 / 邮箱唯一）
- 用户登录（返回 JWT Token）
- 获取用户列表（需登录）
- 获取单个用户（需登录）
- 修改用户信息（需登录）
- 删除用户（需登录）
- 完整异常场景、权限校验

## 快速部署
### 1. 安装依赖
```bash
pip install fastapi uvicorn sqlalchemy pymysql pytest requests pytest-html
```

### 2. 创建数据库与表
执行以下 SQL（MySQL）：
```sql
CREATE DATABASE IF NOT EXISTS user_db DEFAULT CHARSET utf8mb4;
USE user_db;

DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    age INT NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

### 3. 修改数据库配置（config/config.py）
```python
DB_USER="root"
DB_PWD="你的密码"
DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="user_db"

SECRET_KEY = "fastapi-test-2025"
ALGORITHM = "HS256"
```

### 4. 启动项目
```bash
python main.py
```
访问接口文档：
> http://127.0.0.1:8000/docs

## 自动化测试
### 运行所有用例
```bash
pytest tests/test_user_api.py -v
```

### 运行并生成 HTML 测试报告
```bash
pytest tests/test_user_api.py -v --html=report.html
```
报告打开：`report.html`

### 测试用例覆盖
- 首页接口
- 注册成功 / 用户名重复 / 邮箱重复
- 登录成功 / 用户不存在 / 密码错误
- 获取用户列表 / 单个用户（存在 / 不存在）
- 修改用户（正常 / 无更新字段）
- 删除用户（存在 / 不存在）
- 未登录访问鉴权接口

共 **15 条用例**，覆盖正常 + 异常 + 权限场景

## 常用SQL（清空用户表数据）
```sql
USE user_db;
TRUNCATE TABLE user;

