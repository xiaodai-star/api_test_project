import requests

BASE_URL = "http://localhost:8000"

#请求首页
res = requests.get(f"{BASE_URL}/")
assert res.status_code == 200
assert res.json()["message"] == "hello,fastapi"

data = {
    "name":"jk",
    "age":18,
    "email":"123@q.com",
    "password": "123456"
}

res = requests.post(
    f"{BASE_URL}/register",json = data
)
print("注册接口状态码：",res.status_code)
print("注册接口返回:",res.json())

user_id = 1 
res = requests.get(f"{BASE_URL}/user/{user_id}")
print("查询用户状态码：",res.status_code)
print("查询用户返回：",res.json())


update_date = {
    "name":"kj",
    "age": 20
}

res = requests.put(
    f"{BASE_URL}/user/{user_id}",json = update_date
)

print("修改用户状态码:",res.status_code)
print("修改用户返回:",res.json())


user_id = 3
res = requests.delete(
    f"{BASE_URL}/user/{user_id}"
)
print("删除用户状态码：",res.status_code)
print("删除用户返回：",res.json())
