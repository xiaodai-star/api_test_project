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
# 数据模型定义（接口参数格式）
# ==========================
# 注册接口参数
class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    password: str

# 修改用户接口参数（全部可选）
class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None

# 登录接口参数
class UserLogin(BaseModel):
    email: str
    password: str

# ==========================
# 密码工具方法
# ==========================
def get_pwd_hash(pwd):
    return pwd

def verify_pwd(plain, hashed):
    return plain == hashed

# ==========================
# JWT 令牌生成（登录凭证）
# ==========================
# 生成短期 token（1小时有效期）
def create_token(user_id: int):
    import time
    payload = {
        "user_id": user_id,
        "exp": time.time() + 3600
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# 生成长期刷新 token（7天有效期）
def create_refresh_token(user_id: int):
    import time
    payload = {
        "user_id": user_id,
        "exp": time.time() + 604800
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ==========================
# 登录校验工具（所有需要登录的接口都会用）
# ==========================
def check_token(token: Optional[str] = Header(None)):
    if not token:
        raise HTTPException(401, "未登录")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(401, "token无效")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "token已过期")
    except:
        raise HTTPException(401, "token无效")

# 获取当前登录用户信息（含角色）
def get_current_user(
    user_id: int = Depends(check_token),
    db: Session = Depends(get_db)
):
    user = db.execute(text("SELECT id, role FROM user WHERE id=:id"), {"id": user_id}).fetchone()
    if not user:
        raise HTTPException(401, "用户不存在")
    return user

# ==========================
# 基础接口
# ==========================
# 首页接口（测试服务是否正常）
@router.get("/")
def home():
    return {"msg": "hello, fastapi"}

# 用户注册接口
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    exists = db.execute(text("SELECT id FROM user WHERE name=:name"), {"name": user.name}).fetchone()
    if exists:
        raise HTTPException(400, "用户名已存在")
    exists_email = db.execute(text("SELECT id FROM user WHERE email=:email"), {"email": user.email}).fetchone()
    if exists_email:
        raise HTTPException(400, "邮箱已被注册")

    hashed_pwd = get_pwd_hash(user.password)
    db.execute(text(
        "INSERT INTO user(name, age, email, password) VALUES (:n, :a, :e, :p)"
    ), {"n": user.name, "a": user.age, "e": user.email, "p": hashed_pwd})
    db.commit()
    return {"msg": "注册成功"}

# 用户登录接口
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
    refresh_token = create_refresh_token(user.id)
    return {
        "token": token,
        "refresh_token": refresh_token
    }

# 刷新 token 接口（token过期时使用）
@router.post("/refresh")
def refresh_token(refresh_token: Optional[str] = Header(None)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(401, "refresh_token无效")
        new_token = create_token(user_id)
        return {"token": new_token}
    except:
        raise HTTPException(401, "refresh_token无效")

# ==========================
# 【个人中心接口】普通用户只能操作自己
# ==========================
# 查询当前登录用户自己的信息
@router.get("/user/me")
def get_my_info(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = db.execute(text("SELECT id, name, age, email FROM user WHERE id=:id"), {"id": current_user.id}).fetchone()
    if not user:
        raise HTTPException(404, "用户不存在")
    return {"id": user.id, "name": user.name, "age": user.age, "email": user.email}

# 修改当前登录用户自己的信息
@router.put("/user/me")
def update_my_info(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    update_fields = []
    params = {"id": current_user.id}

    if user.name is not None:
        check = db.execute(text("SELECT id FROM user WHERE name=:name AND id!=:id"), {"name": user.name, "id": current_user.id}).fetchone()
        if check:
            raise HTTPException(400, "用户名已存在")
        update_fields.append("name=:name")
        params["name"] = user.name

    if user.email is not None:
        check = db.execute(text("SELECT id FROM user WHERE email=:email AND id!=:id"), {"email": user.email, "id": current_user.id}).fetchone()
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

# 注销/删除自己的账号
@router.delete("/user/me")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db.execute(text("DELETE FROM user WHERE id=:id"), {"id": current_user.id})
    db.commit()
    return {"msg": "注销成功"}

# ==========================
# 【管理员接口】需要 admin 权限
# ==========================
# 查询所有用户列表（仅管理员）
@router.get("/user/users")
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看用户列表")

    users = db.execute(text("SELECT id, name, age, email FROM user")).fetchall()
    if not users:
        raise HTTPException(404, "暂无用户")
    return [{"id": u.id, "name": u.name, "age": u.age, "email": u.email} for u in users]

# 根据ID查询单个用户
@router.get("/user/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # =============== 修复权限 ===============
    if current_user.role != "admin":
        raise HTTPException(403, "仅管理员可查询其他用户信息")
    # =======================================

    user = db.execute(text(
        "SELECT id, name, age, email FROM user WHERE id=:id"
    ), {"id": user_id}).fetchone()
    if not user:
        raise HTTPException(404, "用户不存在")
    return {"id": user.id, "name": user.name, "age": user.age, "email": user.email}

# 根据ID修改用户（仅管理员）
@router.put("/user/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # =============== 修复权限 ===============
    if current_user.role != "admin":
        raise HTTPException(403, "仅管理员可修改其他用户信息")
    # =======================================

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

# 根据ID删除用户（仅管理员）
@router.delete("/user/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(403, "仅管理员可删除用户")

    user = db.execute(text("SELECT id FROM user WHERE id=:id"), {"id": user_id}).fetchone()
    if not user:
        raise HTTPException(404, "用户不存在")

    db.execute(text("DELETE FROM user WHERE id=:id"), {"id": user_id})
    db.commit()
    return {"msg": "删除成功"}