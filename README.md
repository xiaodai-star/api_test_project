# FastAPI 用户管理接口项目
## 项目简介
本项目基于 **FastAPI + MySQL + JWT** 实现一套完整的用户管理后端接口，包含用户注册、登录、Token 刷新、个人信息管理、管理员用户管理功能，严格区分**普通用户/管理员**权限，配套自动化接口测试用例，可直接用于开发学习与接口测试。

## 技术栈
- 后端框架：FastAPI
- 数据库：MySQL
- 身份认证：JWT（Access Token + Refresh Token）
- 测试框架：pytest + requests
- 数据库ORM：SQLAlchemy（原生SQL写法）

## 权限设计（核心）
1. **普通用户**
   - 仅可操作 `/user/me` 系列接口（查询/修改/注销自己账号）
   - 禁止访问 `/user/{user_id}` 管理员接口
2. **管理员用户（role=admin）**
   - 可使用 `/user/me` 管理自身
   - 可使用 `/user/{user_id}` 管理所有用户（查/改/删）
   - 可查看全部用户列表 `/user/users`

## 接口文档
### 基础接口
| 请求方式 | 接口路径 | 功能说明 |
|:---|:---|:---|
| GET | `/` | 服务健康检查 |
| POST | `/register` | 用户注册 |
| POST | `/login` | 用户登录，返回双Token |
| POST | `/refresh` | 刷新Access Token（延长登录） |

### 个人中心接口（普通用户可用）
| 请求方式 | 接口路径 | 功能说明 |
|:---|:---|:---|
| GET | `/user/me` | 获取当前登录用户个人信息 |
| PUT | `/user/me` | 修改当前登录用户个人信息 |
| DELETE | `/user/me` | 注销/删除当前用户账号 |

### 管理员接口（仅admin角色可用）
| 请求方式 | 接口路径 | 功能说明 |
|:---|:---|:---|
| GET | `/user/users` | 查询所有用户列表 |
| GET | `/user/{user_id}` | 根据ID查询指定用户信息 |
| PUT | `/user/{user_id}` | 根据ID修改指定用户信息 |
| DELETE | `/user/{user_id}` | 根据ID删除指定用户账号 |

## 数据库设计
### user 表结构
```sql
CREATE TABLE `user` (
  `id` int PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  `name` varchar(50) NOT NULL COMMENT '用户名',
  `age` int NOT NULL COMMENT '年龄',
  `email` varchar(100) NOT NULL UNIQUE COMMENT '邮箱（登录账号）',
  `password` varchar(100) NOT NULL COMMENT '密码',
  `role` varchar(20) DEFAULT 'user' COMMENT '角色：user普通用户 / admin管理员'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```
> 注：测试自动注册用户默认 `role=user`；管理员需手动修改数据库角色为 `admin`。

## 项目目录结构
```
api_test_project/
├── config/
│   ├── __init__.py
│   ├── config.py      # JWT密钥、算法配置
│   └── db.py          # 数据库连接配置
├── routers/
│   └── user_api.py    # 所有用户接口实现
├── tests/
│   └── test_user_api.py  # pytest自动化接口测试用例
├── main.py            # FastAPI项目启动入口
└── README.md          # 项目说明文档
```

## 环境安装
1. 安装依赖包
```bash
pip install fastapi uvicorn sqlalchemy pymysql jwt pytest requests
```
2. 配置数据库：修改 `config/db.py` 数据库连接信息（账号、密码、库名）
3. 配置JWT：修改 `config/config.py` 中 `SECRET_KEY` 密钥

## 启动项目
```bash
# 启动FastAPI服务
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- 接口文档地址：`http://127.0.0.1:8000/docs`（Swagger在线调试）
- 服务地址：`http://127.0.0.1:8000`

## 运行自动化测试
```bash
# 执行全部接口测试用例
pytest tests/test_user_api.py -v
```
### 测试覆盖场景
1. 基础功能：注册、登录、密码校验、用户名/邮箱唯一性校验
2. 个人中心：查询/修改/注销自身账号
3. 权限校验：普通用户禁止访问管理员接口、未登录禁止访问鉴权接口
4. 异常场景：查询不存在用户、修改无字段、密码错误等

## 核心功能说明
### 1. JWT双Token认证
- **Access Token**：短期有效（1小时），用于日常接口鉴权
- **Refresh Token**：长期有效（7天），用于刷新Access Token，无需重复登录
### 2. 权限隔离
- 普通用户仅可操作自身信息，无法查看/修改其他用户
- 管理员拥有全局用户管理权限
### 3. 数据校验
- 注册时校验用户名、邮箱唯一性
- 修改信息时校验用户名、邮箱不可重复
- 接口参数非空校验、用户存在性校验

## 注意事项
1. 测试自动注册的用户默认是普通用户，如需管理员权限，手动修改数据库 `role='admin'`
2. 密码未加密（项目演示用途，生产环境需使用bcrypt等加密）
3. 所有接口通过请求头 `token` 传递鉴权凭证
4. 测试用例自动生成随机用户，避免用户名/邮箱重复冲突