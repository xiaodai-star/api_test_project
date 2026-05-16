from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from config.db import get_db

# 路由对象，用来管理用户接口
router = APIRouter(prefix="/user", tags=["用户管理"])

# 请求模型（和你原来完全一样）
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

@router.get("/")
def home():
    return {"msg":"hello,fastapi"}


# 注册接口（注意路径去掉了 /user，由prefix统一加）
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    exists = db.execute(
        text("SELECT id FROM user WHERE name = :name"),
        {"name": user.name}
    ).fetchone()
    if exists:
        raise HTTPException(status_code=400, detail="用户已存在")
    db.execute(
        text("INSERT INTO user(name,age,email,password) VALUES(:name,:age,:email,:password)"),
        {"name": user.name, "age": user.age, "email": user.email, "password": user.password}
    )
    db.commit()
    return {"msg": "注册成功"}

# 查询所有用户
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.execute(text("SELECT * FROM user")).fetchall()
    if not users:
        raise HTTPException(status_code=404, detail="没有用户")
    return [{"name": user.name, "age": user.age, "email": user.email} for user in users]

# 查询单个用户
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT * FROM user WHERE id = :id"),
        {"id": user_id}
    ).fetchone()
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    return {"name": user.name, "age": user.age, "email": user.email}

# 删除用户
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT * FROM user WHERE id = :id"),
        {"id": user_id}
    ).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.execute(
        text("DELETE FROM user WHERE id = :id"),
        {"id": user_id}
    )
    db.commit()
    return {"msg": "删除成功"}

# 修改用户
@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    update_sql = []
    params = {"id": user_id}

    if user.name:
        exists = db.execute(
            text("SELECT id FROM user WHERE name = :name AND id !=:id"),
            {"name": user.name, "id": user_id}
        ).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail="用户已存在")
        update_sql.append("name=:name")
        params["name"] = user.name

    if user.email:
        exists = db.execute(
            text("SELECT id FROM user WHERE email = :email AND id !=:id"),
            {"email": user.email, "id": user_id}
        ).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail="邮箱已存在")
        update_sql.append("email=:email")
        params["email"] = user.email

    if user.age:
        update_sql.append("age=:age")
        params["age"] = user.age

    if user.password:
        update_sql.append("password=:password")
        params["password"] = user.password

    if not update_sql:
        raise HTTPException(status_code=400, detail="没有要更新的字段")

    sql = f"UPDATE user SET {','.join(update_sql)} WHERE id =:id"
    db.execute(text(sql), params)
    db.commit()
    return {"msg": "修改成功"}