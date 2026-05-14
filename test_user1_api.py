import pytest
import requests

# ======================
# 企业规范：公共配置 + fixture
# ======================
@pytest.fixture(scope="session")
def base_url():
    return "http://127.0.0.1:8000"

@pytest.fixture(scope="session")
def headers():
    return {"Content-Type": "application/json"}

# 测试数据抽离（公司规范）
TEST_NAME = "ROOT"
TEST_AGE = 18
TEST_EMAIL = "555@QQ.COM"
TEST_PASSWORD = "159753"

# ======================
# 你原来的8个接口测试
# ======================

# 1 测试首页
def test_home(base_url):
    res = requests.get(f"{base_url}/")
    assert res.status_code == 200
    assert res.json()["msg"] == "hello,fastapi"

# 2 注册成功
def test_register_user_success(base_url, headers):
    data = {
        "name": TEST_NAME,
        "age": TEST_AGE,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    res = requests.post(f"{base_url}/register", json=data, headers=headers)
    assert res.status_code == 200
    assert res.json()["msg"] == "注册成功"

# 3 注册重复
def test_register_user_duplicate(base_url, headers):
    data = {
        "name": TEST_NAME,
        "age": 19,
        "email": "tpp@qq.com",
        "password": "Tpp"
    }
    res = requests.post(f"{base_url}/register", json=data, headers=headers)
    assert res.status_code == 400
    assert "用户已存在" in res.json()["detail"]

# 4 查询所有用户
def test_get_users_success(base_url):
    res = requests.get(f"{base_url}/user/users")
    assert res.status_code == 200

# 5 查询单个用户
def test_get_user_success(base_url):
    res = requests.get(f"{base_url}/user/15")
    assert res.status_code == 200

# 6 查询不存在用户
def test_get_user_no_exists(base_url):
    res = requests.get(f"{base_url}/user/9999")
    assert res.status_code == 400
    assert "用户不存在" in res.json()["detail"]

# 7 修改用户
def test_update_user(base_url, headers):
    update_data = {"age": 20}
    res = requests.put(f"{base_url}/user/1", json=update_data, headers=headers)
    assert res.status_code == 200
    assert res.json()["msg"] == "修改成功"

# 8 删除用户
def test_delete_user(base_url):
    res = requests.delete(f"{base_url}/user/15")
    assert res.status_code == 200
    assert res.json()["msg"] == "删除成功"