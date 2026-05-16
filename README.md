# 用户管理接口服务 User‑API‑Service
## 项目简介
本项目基于 **FastAPI + MySQL + SQLAlchemy** 开发，实现用户注册、查询、更新、删除基础CRUD接口，配套 pytest 接口自动化回归测试，采用标准后端分层架构，接口规范统一、可直接用于业务迭代与接口交付。

## 技术栈
- 后端框架：FastAPI
- 数据库：MySQL 8.0+
- 数据库驱动：pymysql
- ORM框架：SQLAlchemy
- 自动化测试：pytest + requests + pytest‑html
- 运行环境：Python 3.8+
- 版本管理：Git
- 环境隔离：venv虚拟环境

## 项目目录结构
User‑API‑Service/
├── .gitignore # Git 忽略配置，过滤缓存、虚拟环境、报告等非业务文件
├── .pytest_cache/ # pytest 自动生成测试缓存文件
├── pycache/ # Python 运行自动生成字节码缓存
├── .venv/ # 项目独立虚拟环境，隔离第三方依赖
├── main.py # 项目服务入口，路由聚合，启动 FastAPI 应用
├── api/ # 接口控制层 Controller，接收请求、参数校验、路由分发
│ ├── init.py
│ └── user_api.py # 用户模块接口：注册、查询、修改、删除
├── config/ # 全局配置层，统一管理数据库连接信息
│ ├── init.py
│ └── config.py # 数据库账号、密码、地址、端口、库名配置
├── sql/ # 数据库层，存放初始化建库建表 SQL 脚本
│ └── init.sql # MySQL 一键初始化脚本
├── tests/ # 自动化测试层，接口功能回归测试用例
│ ├── init.py
│ └── test_user_api.py # 用户接口正向、反向场景测试用例
├── assets/ # 静态资源目录，存放文档、截图、附件
├── report.html # 自动化测试 HTML 可视化报告
└── README.md # 项目说明文档


## 分层架构说明（企业规范）
1. **配置层 config**
统一管理数据库配置，解耦硬编码，支持开发、测试、生产多环境快速切换。
2. **接口层 api**
只负责接收前端请求、参数校验、路由分发，业务逻辑与数据操作分离，结构清晰易维护。
3. **数据层 sql**
标准化数据库初始化脚本，支持一键部署，规范表结构、字段约束、索引设计。
4. **测试层 tests**
覆盖正常业务场景与异常边界场景，实现接口自动化回归，保障版本迭代稳定性。

## 环境部署与启动
### 1. 虚拟环境初始化
```bash
# 创建虚拟环境
python -m venv .venv

# Windows激活虚拟环境
.venv\Scripts\activate
# Linux/Mac激活虚拟环境
source .venv/bin/activate

2. 安装项目依赖
pip install fastapi uvicorn sqlalchemy pymysql pytest requests pytest-html

3. 数据库初始化
(1).本地启动 MySQL 服务
(2).执行 sql/init.sql 脚本，自动创建 user_db 数据库及 user 用户表
(3).修改 config/config.py 中数据库账号密码，与本地环境保持一致

4. 启动后端服务
# 开发环境热重载启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

自动接口文档：http://127.0.0.1:8000/docs
服务首页地址：http://127.0.0.1:8000


请求方式	接口路径	            接口功能	            数据格式
GET	           /	              服务健康检查	             -
POST	    /register	            用户注册	            JSON
GET	        /user/users	           查询所有用户	              -
GET	     /user/{user_id}	     根据 ID 查询单个用户	       -
PUT	      /user/{user_id}	        更新用户信息	         JSON
DELETE	  /user/{user_id}	        删除指定用户	            -


自动化测试执行
执行命令（生成可视化测试报告）
pytest tests/test_user_api.py -v --html=report.html --self-contained-html
-v：输出详细用例执行日志
生成 report.html，浏览器打开可查看用例通过率、失败原因、执行耗时

测试覆盖场景
正向场景：注册成功、查询用户、修改用户、删除用户
异常场景：重复注册、用户不存在、更新无有效字段、非法参数校验

开发规范
1.接口参数统一使用 Pydantic 模型校验，严格约束字段类型
2.数据库操作使用 SQLAlchemy，禁止裸 SQL 拼接，防止 SQL 注入风险
3.异常统一抛出标准 HTTP 状态码，返回清晰的错误提示信息
4.新增接口必须同步编写自动化测试用例，覆盖正向及异常场景
5.禁止提交缓存文件、虚拟环境、测试报告、日志文件至 Git 仓库

版本维护
Python 版本：≥3.8
数据库版本：MySQL 8.0+
维护人员：XXX
更新日期：