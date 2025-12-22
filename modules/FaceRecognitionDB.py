import pymysql
from pymysql import Error

class DataBaseManager:
    def __init__(self, password):
        self.DB_CONFIG = {
            "host": "localhost",
            "user": "root",
            "passwd": password,
            "charset": "utf8mb4",
            "port": 3306,
            "database": "smartlock_db",
            "autocommit": True  # 自动提交事务
        }
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            return pymysql.connect(**self.DB_CONFIG)
        except Error as e:
            print(f"数据库连接错误: {e}")
            raise

    # 以字典形式返回所有查询结果
    def fetch_all(self, sql, args=None):
        connection = self._get_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except Error as e:
            print(f"查询错误: {e}")
            return []
        finally:
            connection.close()

    # 以字典形式返回一条查询结果
    def fetch_one(self, sql, args=None):
        connection = self._get_connection()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                result = cursor.fetchone()
                return result
        except Error as e:
            print(f"查询错误: {e}")
            return None
        finally:
            connection.close()
    
    # 插入数据
    def insert_data(self, sql, args=None):
        connection = self._get_connection()
        try:
            with connection.cursor() as cursor:
                if args:
                    cursor.execute(sql, args)
                else:
                    cursor.execute(sql)
                connection.commit()
                return cursor.lastrowid  # 返回插入的ID
        except Error as e:
            connection.rollback()
            print(f"插入数据错误: {e}")
            return None
        finally:
            connection.close()