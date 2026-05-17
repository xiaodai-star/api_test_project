import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8000"

@pytest.fixture(scope="session")
def headers():
    return {"Content-Type": "application/json"}

# 自动注册 + 登录，拿到 token
@pytest.fixture(scope="session")
def token(base_url, headers):
    # 先注册测试用户（每次都用全新用户，避免冲突）
    import uuid
    unique = str(uuid.uuid4())[:8]
    reg_data = {
        "name": f"root_{unique}",
        "age": 18,
        "email": f"root_{unique}@qq.com",
        "password": "159753"
    }
    requests.post(f"{base_url}/register", json=reg_data, headers=headers)

    # 登录
    login_data = {"email": reg_data["email"], "password": "159753"}
    r = requests.post(f"{base_url}/login", json=login_data, headers=headers)
    return r.json()["token"]

@pytest.fixture(scope="session")
def auth_headers(headers, token):
    h = headers.copy()
    h["token"] = token
    return h

# ==============================
# 测试用例（完整版，全覆盖）
# ==============================

# 1. 首页
def test_home(base_url):
    r = requests.get(f"{base_url}/")
    assert r.status_code == 200
    assert r.json()["msg"] == "hello, fastapi"

# 2. 注册：正常注册
def test_register_success(base_url, headers):
    data = {
        "name": "test_user1",
        "age": 20,
        "email": "test1@qq.com",
        "password": "123456"
    }
    r = requests.post(f"{base_url}/register", json=data, headers=headers)
    assert r.status_code == 200
    assert r.json()["msg"] == "注册成功"

# 3. 注册：用户名重复
def test_register_duplicate_name(base_url, headers):
    data = {
        "name": "test_user1",
        "age": 22,
        "email": "test_dup@qq.com",
        "password": "123456"
    }
    r = requests.post(f"{base_url}/register", json=data, headers=headers)
    assert r.status_code == 400

# 4. 注册：邮箱重复
def test_register_duplicate_email(base_url, headers):
    data = {
        "name": "test_unique",
        "age": 22,
        "email": "test1@qq.com",
        "password": "123456"
    }
    r = requests.post(f"{base_url}/register", json=data, headers=headers)
    assert r.status_code == 400

# 5. 登录：成功
def test_login_success(base_url, headers):
    data = {
        "email": "test1@qq.com",
        "password": "123456"
    }
    r = requests.post(f"{base_url}/login", json=data, headers=headers)
    assert r.status_code == 200
    assert "token" in r.json()

# 6. 登录：用户不存在
def test_login_user_not_exist(base_url, headers):
    data = {
        "email": "not_exist@qq.com",
        "password": "123456"
    }
    r = requests.post(f"{base_url}/login", json=data, headers=headers)
    assert r.status_code == 400

# 7. 登录：密码错误
def test_login_wrong_pwd(base_url, headers):
    data = {
        "email": "test1@qq.com",
        "password": "wrong_pwd"
    }
    r = requests.post(f"{base_url}/login", json=data, headers=headers)
    assert r.status_code == 400

# 8. 获取所有用户
def test_get_users(base_url, auth_headers):
    r = requests.get(f"{base_url}/user/users", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

# 9. 获取单个用户：存在
def test_get_user_exist(base_url, auth_headers):
    r = requests.get(f"{base_url}/user/1", headers=auth_headers)
    assert r.status_code == 200

# 10. 获取单个用户：不存在
def test_get_user_not_exist(base_url, auth_headers):
    r = requests.get(f"{base_url}/user/9999", headers=auth_headers)
    assert r.status_code == 404

# 11. 修改用户：正常修改
def test_update_user_success(base_url, auth_headers):
    data = {"age": 25}
    r = requests.put(f"{base_url}/user/1", json=data, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["msg"] == "修改成功"

# 12. 修改用户：无更新字段
def test_update_no_fields(base_url, auth_headers):
    data = {}
    r = requests.put(f"{base_url}/user/1", json=data, headers=auth_headers)
    assert r.status_code == 400

# 13. 删除用户：存在
def test_delete_user_success(base_url, auth_headers):
    r = requests.delete(f"{base_url}/user/1", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["msg"] == "删除成功"

# 14. 删除用户：不存在
def test_delete_user_not_exist(base_url, auth_headers):
    r = requests.delete(f"{base_url}/user/9999", headers=auth_headers)
    assert r.status_code == 404

# 15. 未登录访问接口（必须失败）
def test_api_without_token(base_url):
    r = requests.get(f"{base_url}/user/users")
    assert r.status_code == 401