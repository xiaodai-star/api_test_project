import requests
import pytest

BASE_URL = "http://localhost:8000"

TEST_NAME = "ROOT"
TEST_AGE = "18"
TEST_EMAIL = "555@QQ.COM"
TEST_PASSWORD = "159753"

# 1测试首页接口：
def test_home():
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code ==200
    assert res.json()["msg"] == "hello,fastapi"


# 2测试注册成功：
def test_register_user_success():
    data = {
        "name" : TEST_NAME,
        "age":TEST_AGE,
        "email":TEST_EMAIL,
        "password":TEST_PASSWORD
    }
    res = requests.post(f"{BASE_URL}/register",json=data)
    assert res.status_code == 200
    assert res.json()["msg"] == "注册成功"


# 3测试注册重复：
def test_register_user_duplicate():
    data={
        "name" : TEST_NAME,
        "age":19,
        "email":"tpp@qq.com",
        "password":"Tpp"
    }
    res = requests.post(f"{BASE_URL}/register",json=data)
    assert res.status_code == 400
    assert "用户已存在" in res.json()["detail"]

    # 4测试查询所有用户
def test_get_users_success():
    res = requests.get(f"{BASE_URL}/user/users")
    assert res.status_code == 200

# 5测试查询单个用户：
def test_get_user_success():
    res = requests.get(f"{BASE_URL}/user/9")
    assert res.status_code ==200

#6测试查询单个用户（不存在）
def  test_get_user_no_exists():
    res = requests.get(f"{BASE_URL}/user/9999")
    assert res.status_code == 400
    assert "用户不存在" in res.json()["detail"]

    
# 7修改用户：
def test_update_user():
    update_data = {"age":20}
    res = requests.put(f"{BASE_URL}/user/1",json=update_data)
    assert res.status_code == 200
    assert res.json()["msg"] =="修改成功"


# 8测试删除用户
def test_delete_user():
    res = requests.delete(f"{BASE_URL}/user/9")
    assert res.status_code == 200
    assert res.json()["msg"] =="删除成功"
