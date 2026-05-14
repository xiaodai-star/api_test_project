import pytest
import requests
import random

BASE_URL="http://localhost:8000"



def test_register():
    random_name = f"robot_{random.randint(0,99999)}"
    random_email = f"test_{random.randint(0,99999)}@robot.com"
    random_age = f"{random.randint(0,80)}"
    random_password = f"{random.randint(1000,99999)}"
    url = f"{BASE_URL}/register"
    data = {
        "name":random_name,
        "age":random_age,
        "email":random_email,
        "password":random_password

    }
    res = requests.post(url,json=data)


    print("接口返回数据:", res.json())
    print("状态码:", res.status_code)
    assert res.status_code == 200
    assert res.json()["msg"] == "注册成功"
 