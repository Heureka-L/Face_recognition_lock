#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 FaceRecognitionDB.py 模块的功能
"""

import os
import sys
import json

# 将模块路径添加到系统路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.FaceRecognitionDB import DataBaseManager

def test_database_connection():
    """测试数据库连接"""
    print("开始测试数据库连接...")
    try:
        db = DataBaseManager()
        print("✓ 数据库连接成功")
        return db
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return None

def test_insert_admin_user(db):
    """测试插入管理员用户"""
    print("\n开始测试插入管理员用户...")
    sql = "INSERT INTO admin_users (username, password) VALUES (?, ?)"
    user_id = db.insert_data(sql, ("test_admin", "test_password"))
    if user_id:
        print(f"✓ 管理员用户插入成功，ID: {user_id}")
        return user_id
    else:
        print("✗ 管理员用户插入失败")
        return None

def test_insert_face_feature(db):
    """测试插入人脸特征"""
    print("\n开始测试插入人脸特征...")
    # 模拟人脸编码数据（JSON格式）
    face_encoding = json.dumps([0.1, 0.2, 0.3, 0.4, 0.5] * 26)  # 130维特征向量
    sql = "INSERT INTO face_features (username, face_encoding) VALUES (?, ?)"
    face_id = db.insert_data(sql, ("test_user", face_encoding))
    if face_id:
        print(f"✓ 人脸特征插入成功，ID: {face_id}")
        return face_id
    else:
        print("✗ 人脸特征插入失败")
        return None

def test_fetch_admin_user(db):
    """测试获取管理员用户"""
    print("\n开始测试获取管理员用户...")
    sql = "SELECT * FROM admin_users WHERE username = ?"
    result = db.fetch_one(sql, ("test_admin",))
    if result:
        print(f"✓ 获取管理员用户成功: {result}")
        return result
    else:
        print("✗ 获取管理员用户失败")
        return None

def test_fetch_face_feature(db):
    """测试获取人脸特征"""
    print("\n开始测试获取人脸特征...")
    sql = "SELECT * FROM face_features WHERE username = ?"
    result = db.fetch_one(sql, ("test_user",))
    if result:
        print(f"✓ 获取人脸特征成功: {result['id']}, {result['username']}")
        return result
    else:
        print("✗ 获取人脸特征失败")
        return None

def test_fetch_all_admin_users(db):
    """测试获取所有管理员用户"""
    print("\n开始测试获取所有管理员用户...")
    sql = "SELECT * FROM admin_users"
    results = db.fetch_all(sql)
    print(f"✓ 获取到 {len(results)} 个管理员用户")
    for user in results:
        print(f"  - ID: {user['id']}, Username: {user['username']}")
    return results

def test_fetch_all_face_features(db):
    """测试获取所有人脸特征"""
    print("\n开始测试获取所有人脸特征...")
    sql = "SELECT * FROM face_features"
    results = db.fetch_all(sql)
    print(f"✓ 获取到 {len(results)} 个人脸特征记录")
    for feature in results:
        print(f"  - ID: {feature['id']}, Username: {feature['username']}")
    return results

def test_update_admin_user(db):
    """测试更新管理员用户"""
    print("\n开始测试更新管理员用户...")
    sql = "UPDATE admin_users SET password = ? WHERE username = ?"
    result = db.insert_data(sql, ("new_password", "test_admin"))  # 使用insert_data执行更新
    # 实际上，更新操作不会返回新行ID，所以更好的方式是执行SQL然后检查影响的行数
    # 重新查询以确认更新
    updated_user = db.fetch_one("SELECT * FROM admin_users WHERE username = ?", ("test_admin",))
    if updated_user and updated_user['password'] == 'new_password':
        print("✓ 管理员用户更新成功")
        return True
    else:
        print("✗ 管理员用户更新失败")
        return False

def cleanup_test_data(db):
    """清理测试数据"""
    print("\n开始清理测试数据...")
    try:
        # 删除测试用户
        db.insert_data("DELETE FROM admin_users WHERE username = ?", ("test_admin",))
        # 删除测试人脸特征
        db.insert_data("DELETE FROM face_features WHERE username = ?", ("test_user",))
        print("✓ 测试数据清理完成")
        return True
    except Exception as e:
        print(f"✗ 测试数据清理失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试 FaceRecognitionDB 模块")
    print("=" * 50)
    
    # 测试数据库连接
    db = test_database_connection()
    if not db:
        print("数据库连接失败，无法继续测试")
        return False
    
    # 依次运行各项测试
    tests_results = []
    
    # 插入测试数据
    admin_id = test_insert_admin_user(db)
    tests_results.append(("插入管理员用户", admin_id is not None))
    
    face_id = test_insert_face_feature(db)
    tests_results.append(("插入人脸特征", face_id is not None))
    
    # 查询测试
    admin_user = test_fetch_admin_user(db)
    tests_results.append(("获取管理员用户", admin_user is not None))
    
    face_feature = test_fetch_face_feature(db)
    tests_results.append(("获取人脸特征", face_feature is not None))
    
    all_admins = test_fetch_all_admin_users(db)
    tests_results.append(("获取所有管理员用户", all_admins is not None))
    
    all_faces = test_fetch_all_face_features(db)
    tests_results.append(("获取所有人脸特征", all_faces is not None))
    
    update_result = test_update_admin_user(db)
    tests_results.append(("更新管理员用户", update_result))
    
    # 清理测试数据
    cleanup_result = cleanup_test_data(db)
    tests_results.append(("清理测试数据", cleanup_result))
    
    # 输出测试结果总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print("=" * 50)
    
    passed = 0
    total = len(tests_results)
    
    for test_name, result in tests_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试均通过！")
    else:
        print(f"⚠️  {total - passed} 项测试未通过")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n数据库模块测试完成，一切正常！")
    else:
        print("\n数据库模块测试发现问题，请检查代码。")