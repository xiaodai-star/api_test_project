from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from config.db import get_db
import jwt
from config.config import SECRET_KEY, ALGORITHM

router = APIRouter()

# ==========================
# 数据模型
# ==========================
class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

# ==========================
# 密码（保持你原来的稳定方案）
# ==========================
def get_pwd_hash(pwd):
    return pwd

def verify_pwd(plain, hashed):
    return plain == hashed

# ==========================
# JWT
# ==========================
def create_token(user_id: int):
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm=ALGORITHM)

def check_token(token: Optional[str] = Header(None)):
    if not token:
        raise HTTPException(401, "未登录")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(401, "token无效")
        return user_id
    except:
        raise HTTPException(401, "token无效")

# ==========================
# 接口（已删除 get_page）
# ==========================
@router.get("/")
def home():
    return {"msg": "hello, fastapi"}

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否重复
    exists = db.execute(text("SELECT id FROM user WHERE name=:name"), {"name": user.name}).fetchone()
    if exists:
        raise HTTPException(400, "用户名已存在")
    # 检查邮箱是否重复
    exists_email = db.execute(text("SELECT id FROM user WHERE email=:email"), {"email": user.email}).fetchone()
    if exists_email:
        raise HTTPException(400, "邮箱已被注册")

    hashed_pwd = get_pwd_hash(user.password)
    db.execute(text(
        "INSERT INTO user(name, age, email, password) VALUES (:n, :a, :e, :p)"
    ), {"n": user.name, "a": user.age, "e": user.email, "p": hashed_pwd})
    db.commit()
    return {"msg": "注册成功"}

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.execute(text(
        "SELECT id, password FROM user WHERE email=:email"
    ), {"email": data.email}).fetchone()

    if not user:
        raise HTTPException(400, "用户不存在")
    if not verify_pwd(data.password, user.password):
        raise HTTPException(400, "密码错误")

    token = create_token(user.id)
    return {"token": token}

@router.get("/user/users")
def get_users(db: Session = Depends(get_db), user_id=Depends(check_token)):
    users = db.execute(text("SELECT id, name, age, email FROM user")).fetchall()
    if not users:
        raise HTTPException(404, "暂无用户")
    return [{"id": u.id, "name": u.name, "age": u.age, "email": u.email} for u in users]

@router.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), uid=Depends(check_token)):
    user = db.execute(text(
        "SELECT id, name, age, email FROM user WHERE id=:id"
    ), {"id": user_id}).fetchone()

    if not user:
        raise HTTPException(404, "用户不存在")
    return {"id": user.id, "name": user.name, "age": user.age, "email": user.email}

@router.put("/user/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), uid=Depends(check_token)):
    # 检查用户是否存在
    exists_user = db.execute(text("SELECT id FROM user WHERE id=:id"), {"id": user_id}).fetchone()
    if not exists_user:
        raise HTTPException(404, "用户不存在")

    update_fields = []
    params = {"id": user_id}

    if user.name is not None:
        check = db.execute(text(
            "SELECT id FROM user WHERE name=:name AND id!=:id"
        ), {"name": user.name, "id": user_id}).fetchone()
        if check:
            raise HTTPException(400, "用户名已存在")
        update_fields.append("name=:name")
        params["name"] = user.name

    if user.email is not None:
        check = db.execute(text(
            "SELECT id FROM user WHERE email=:email AND id!=:id"
        ), {"email": user.email, "id": user_id}).fetchone()
        if check:
            raise HTTPException(400, "邮箱已被使用")
        update_fields.append("email=:email")
        params["email"] = user.email

    if user.age is not None:
        update_fields.append("age=:age")
        params["age"] = user.age

    if user.password is not None:
        update_fields.append("password=:pwd")
        params["pwd"] = get_pwd_hash(user.password)

    if not update_fields:
        raise HTTPException(400, "未提供任何更新字段")

    sql = f"UPDATE user SET {','.join(update_fields)} WHERE id=:id"
    db.execute(text(sql), params)
    db.commit()
    return {"msg": "修改成功"}

@router.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), uid=Depends(check_token)):
    user = db.execute(text("SELECT id FROM user WHERE id=:id"), {"id": user_id}).fetchone()
    if not user:
        raise HTTPException(404, "用户不存在")

    db.execute(text("DELETE FROM user WHERE id=:id"), {"id": user_id})
    db.commit()
    return {"msg": "删除成功"}