# config/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import DB_USER,DB_PWD,DB_HOST,DB_PORT,DB_NAME

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# 测试连接
try:
    with engine.connect() as conn:
        print("数据库连接成功")
except Exception as e:
     print("数据库连接失败", e)

# 数据库依赖
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()