# =================================================================================================
#  pip install sqlite3 -i https://pypi.tuna.tsinghua.edu.cn/simple
# =================================================================================================
import sqlite3
import os

def main():
    # 确保database目录存在
    db_path = os.path.join('database', 'smartlock.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接数据库
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    try:
        # 创建管理员用户表
        create_table1_sql = """
        CREATE TABLE IF NOT EXISTS admin_users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # 创建人脸特征数据表
        create_table2_sql = """
        CREATE TABLE IF NOT EXISTS face_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            face_encoding TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table1_sql)
        cursor.execute(create_table2_sql)
        print("数据表创建成功")
        
        # 提交更改
        connection.commit()
        print("数据库和表结构创建完成！")
        
    except sqlite3.Error as e:
        print(f"创建失败: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    main()


