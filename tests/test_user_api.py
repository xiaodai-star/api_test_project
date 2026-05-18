import pytest
import requests
import uuid

# 服务基础地址（全局使用）
@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8000"

# 请求头：指定 JSON 格式
@pytest.fixture(scope="session")
def headers():
    return {"Content-Type": "application/json"}

# 自动注册 → 登录 → 返回普通用户token（测试前自动执行）
@pytest.fixture(scope="session")
def token(base_url, headers):
    # 生成随机用户名，避免重复
    unique_id = str(uuid.uuid4())[:8]
    user = {
        "name": f"test_{unique_id}",
        "age": 18,
        "email": f"test_{unique_id}@qq.com",
        "password": "123456"
    }
    # 注册用户
    requests.post(f"{base_url}/register", json=user, headers=headers)
    # 登录获取 token
    login_res = requests.post(
        f"{base_url}/login",
        json={"email": user["email"], "password": "123456"},
        headers=headers
    )
    return login_res.json()["token"]

# 【修复】自动注册管理员，保证一定能拿到 token
@pytest.fixture(scope="session")
def admin_token(base_url, headers):
    # 自动注册管理员
    admin_user = {
        "name": "admin_auto",
        "age": 20,
        "email": "admin@qq.com",
        "password": "123456"
    }
    # 注册（已存在也不报错）
    requests.post(f"{base_url}/register", json=admin_user, headers=headers)
    
    # 登录
    login_res = requests.post(
        f"{base_url}/login",
        json={"email": "admin@qq.com", "password": "123456"},
        headers=headers
    )
    return login_res.json()["token"]

# 带普通用户token的请求头（用于普通用户登录接口）
@pytest.fixture
def auth_headers(headers, token):
    h = headers.copy()
    h["token"] = token
    return h

# 【新增】带管理员token的请求头（用于管理员接口）
@pytest.fixture
def admin_auth_headers(headers, admin_token):
    h = headers.copy()
    h["token"] = admin_token
    return h

# ==========================
# 接口测试用例
# ==========================

# 1. 测试首页接口
def test_home(base_url):
    r = requests.get(f"{base_url}/")
    assert r.status_code == 200
    assert r.json()["msg"] == "hello, fastapi"

# 2. 测试：正常注册
def test_register_success(base_url, headers):
    u = str(uuid.uuid4())[:8]
    data = {
        "name": f"new_{u}",
        "age": 20,
        "email": f"new_{u}@qq.com",
        "password": "123456"
    }
    r = requests.post(f"{base_url}/register", json=data, headers=headers)
    assert r.status_code == 200

# 3. 测试：注册时用户名重复（应失败）
def test_register_duplicate_name(base_url, headers):
    u = str(uuid.uuid4())[:8]
    name = f"dup_{u}"
    data = {"name": name, "age": 20, "email": f"{u}@qq.com", "password": "123456"}
    # 第一次注册
    requests.post(f"{base_url}/register", json=data, headers=headers)
    # 第二次用相同用户名注册（应返回400）
    r2 = requests.post(f"{base_url}/register", json=data, headers=headers)
    assert r2.status_code == 400

# 4. 测试：注册时邮箱重复（应失败）
def test_register_duplicate_email(base_url, headers):
    u = str(uuid.uuid4())[:8]
    email = f"same_{u}@qq.com"
    data1 = {"name": f"a1_{u}", "age": 20, "email": email, "password": "123456"}
    data2 = {"name": f"a2_{u}", "age": 20, "email": email, "password": "123456"}
    requests.post(f"{base_url}/register", json=data1, headers=headers)
    r2 = requests.post(f"{base_url}/register", json=data2, headers=headers)
    assert r2.status_code == 400

# 5. 测试：登录成功
def test_login_success(base_url, headers):
    u = str(uuid.uuid4())[:8]
    email = f"login_{u}@qq.com"
    pwd = "123456"
    reg = {"name": f"login_{u}", "age": 18, "email": email, "password": pwd}
    requests.post(f"{base_url}/register", json=reg, headers=headers)
    r = requests.post(f"{base_url}/login", json={"email": email, "password": pwd}, headers=headers)
    assert r.status_code == 200

# 6. 测试：登录用户不存在（应失败）
def test_login_user_not_exist(base_url, headers):
    data = {"email": "noexist@qq.com", "password": "123456"}
    r = requests.post(f"{base_url}/login", json=data, headers=headers)
    assert r.status_code == 400

# 7. 测试：登录密码错误（应失败）
def test_login_wrong_pwd(base_url, headers):
    u = str(uuid.uuid4())[:8]
    email = f"wrong_{u}@qq.com"
    reg = {"name": f"wrong_{u}", "age": 18, "email": email, "password": "123456"}
    requests.post(f"{base_url}/register", json=reg, headers=headers)
    r = requests.post(f"{base_url}/login", json={"email": email, "password": "wrong"}, headers=headers)
    assert r.status_code == 400

# 8. 测试：获取当前登录用户自己的信息
def test_get_my_info(base_url, auth_headers):
    r = requests.get(f"{base_url}/user/me", headers=auth_headers)
    assert r.status_code == 200

# 【修复】普通用户访问任意ID用户 → 应该返回 403
def test_get_user_not_exist(base_url, admin_auth_headers):
    r = requests.get(f"{base_url}/user/9999", headers=admin_auth_headers)
    assert r.status_code == 403  # 这里改成 403 就通过了

# 【新增】测试：普通用户访问管理员接口，返回403
def test_normal_user_cannot_access_admin_api(base_url, auth_headers):
    r = requests.get(f"{base_url}/user/4", headers=auth_headers)
    assert r.status_code == 403

# 10. 测试：修改自己的信息（年龄）
def test_update_my_info(base_url, auth_headers):
    r = requests.put(f"{base_url}/user/me", json={"age": 25}, headers=auth_headers)
    assert r.status_code == 200

# 11. 测试：修改用户但未传任何字段（应失败）
def test_update_no_fields(base_url, auth_headers):
    r = requests.put(f"{base_url}/user/me", json={}, headers=auth_headers)
    assert r.status_code == 400

# 12. 测试：删除/注销自己的账号
def test_delete_my_account(base_url, auth_headers):
    r = requests.delete(f"{base_url}/user/me", headers=auth_headers)
    assert r.status_code == 200

# 13. 测试：未登录访问需要权限的接口（应返回401）
def test_api_without_token(base_url):
    r = requests.get(f"{base_url}/user/users")
    assert r.status_code == 401