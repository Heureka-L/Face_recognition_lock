import sqlite3
import os
from contextlib import contextmanager

class DataBaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # 默认数据库路径为根目录下的database文件夹
            db_path = os.path.join('database', 'smartlock.db')
        
        # 确保database目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        # 初始化数据库（创建表等）
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"数据库操作错误: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # 以字典形式返回所有查询结果
    def fetch_all(self, sql, args=None):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
                
                # 将sqlite3.Row转换为字典列表
                return [dict(row) for row in result]
        except sqlite3.Error as e:
            print(f"查询错误: {e}")
            return []

    # 以字典形式返回一条查询结果
    def fetch_one(self, sql, args=None):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                result = cursor.fetchone()
                
                # 将sqlite3.Row转换为字典
                return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"查询错误: {e}")
            return None
    
    # 插入数据
    def insert_data(self, sql, args=None):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                conn.commit()
                return cursor.lastrowid  # 返回插入的ID
        except sqlite3.Error as e:
            print(f"插入数据错误: {e}")
            return None
    
    def _init_database(self):
        """初始化数据库，创建必要的表"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建admin_users表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS admin_users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建face_features表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS face_features (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        face_encoding TEXT NOT NULL,  -- JSON格式存储人脸编码
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"数据库初始化错误: {e}")
            raise