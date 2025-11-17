# =================================================================================================
#  pip install pymysql cryptography -i https://pypi.tuna.tsinghua.edu.cn/simple
# =================================================================================================
import pymysql as db
import  configparser

# ==========================从ini文件导入数据库密码=======================
# 创建配置解析器
config = configparser.ConfigParser()
config.read('.config.ini', encoding='utf-8')
# 从ini文件的mysql节中获取DataBase_Password的值
password = config.get('mysql', 'DataBase_Password')
# ====================================================================

def main():
    global password
    # 连接数据库服务器（不指定具体数据库）
    connection = db.connect(
        host="localhost",
        user="root",
        passwd=password,
        charset="utf8mb4"
    )
    
    cursor = connection.cursor()
    
    try:
        # 创建数据库
        create_db_sql = "CREATE DATABASE IF NOT EXISTS face_recognition_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        cursor.execute(create_db_sql)
        print("数据库创建成功")
        
        # 选择数据库
        cursor.execute("USE face_recognition_db")
        
        # 创建人脸编码数据表  
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS face_encodings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            face_encoding JSON NOT NULL,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        cursor.execute(create_table_sql)
        print("数据表创建成功")
        
        # 提交更改
        connection.commit()
        print("数据库和表结构创建完成！")
        
    except db.Error as e:
        print(f"创建失败: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    main()


