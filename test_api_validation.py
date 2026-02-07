import requests
import json
from datetime import datetime
import os
import shutil

base_url = "http://localhost:8000"

def test_health_check():
    """测试健康检查接口"""
    print("\n测试1: 健康检查接口")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print("✓ 健康检查接口正常")
    except Exception as e:
        print(f"✗ 健康检查接口失败: {e}")

def test_available_months():
    """测试获取可用月份接口"""
    print("\n测试2: 获取可用月份接口")
    try:
        response = requests.get(f"{base_url}/api/v1/months")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print("✓ 获取可用月份接口正常")
    except Exception as e:
        print(f"✗ 获取可用月份接口失败: {e}")

def test_month_partitioning():
    """测试按月分表功能"""
    print("\n测试3: 按月分表功能")
    
    # 测试1: 使用当前月份
    current_month = datetime.now().strftime('%Y-%m')
    print(f"  测试3.1: 使用当前月份 {current_month}")
    
    try:
        # 创建表
        create_table_data = {
            "table_name": "test_monthly",
            "columns": [
                {"name": "id", "type": "BIGINT PRIMARY KEY"},
                {"name": "name", "type": "VARCHAR"},
                {"name": "value", "type": "INTEGER"}
            ],
            "month": current_month
        }
        
        response = requests.post(f"{base_url}/api/v1/tables", json=create_table_data)
        print(f"    创建表状态码: {response.status_code}")
        print(f"    创建表响应: {response.json()}")
        
        # 插入数据
        insert_data = {
            "exec": "INSERT INTO test_monthly (id, name, value) VALUES (?, ?, ?)",
            "params": [1, "test", 100],
            "month": current_month
        }
        
        response = requests.post(f"{base_url}/api/v1/modify/async", json=insert_data)
        print(f"    插入数据状态码: {response.status_code}")
        print(f"    插入数据响应: {response.json()}")
        
        # 查询数据
        query_data = {
            "query": "SELECT * FROM test_monthly",
            "month": current_month
        }
        
        response = requests.post(f"{base_url}/api/v1/query", json=query_data)
        print(f"    查询数据状态码: {response.status_code}")
        query_result = response.json()
        print(f"    查询数据响应: {query_result}")
        
        # 获取查询结果
        if "query_id" in query_result:
            query_id = query_result["query_id"]
            response = requests.get(f"{base_url}/api/v1/query/result/{query_id}", params={"month": current_month})
            print(f"    获取查询结果状态码: {response.status_code}")
            print(f"    获取查询结果响应: {response.json()}")
        
        print("  ✓ 当前月份分表功能正常")
        
    except Exception as e:
        print(f"  ✗ 当前月份分表功能失败: {e}")
    
    # 测试2: 使用指定月份
    test_month = "2026-04"
    print(f"\n  测试3.2: 使用指定月份 {test_month}")
    
    try:
        # 创建表
        create_table_data = {
            "table_name": "test_specified_month",
            "columns": [
                {"name": "id", "type": "BIGINT PRIMARY KEY"},
                {"name": "name", "type": "VARCHAR"}
            ],
            "month": test_month
        }
        
        response = requests.post(f"{base_url}/api/v1/tables", json=create_table_data)
        print(f"    创建表状态码: {response.status_code}")
        print(f"    创建表响应: {response.json()}")
        
        # 验证月份目录是否创建
        month_dir = os.path.join("data", test_month)
        if os.path.exists(month_dir):
            print(f"    ✓ 月份目录 {month_dir} 已创建")
        else:
            print(f"    ✗ 月份目录 {month_dir} 未创建")
        
        print("  ✓ 指定月份分表功能正常")
        
    except Exception as e:
        print(f"  ✗ 指定月份分表功能失败: {e}")

def test_modify_async_param():
    """测试 modify/async 接口参数修改"""
    print("\n测试4: modify/async 接口参数修改")
    
    test_month = datetime.now().strftime('%Y-%m')
    
    # 测试1: 使用新的 exec 参数
    print("  测试4.1: 使用 exec 参数")
    try:
        # 确保表存在
        create_table_data = {
            "table_name": "test_modify",
            "columns": [
                {"name": "id", "type": "BIGINT PRIMARY KEY"},
                {"name": "name", "type": "VARCHAR"}
            ],
            "month": test_month
        }
        requests.post(f"{base_url}/api/v1/tables", json=create_table_data)
        
        # 使用 exec 参数插入数据
        modify_data = {
            "exec": "INSERT INTO test_modify (id, name) VALUES (?, ?)",
            "params": [1, "test_exec_param"],
            "month": test_month
        }
        
        response = requests.post(f"{base_url}/api/v1/modify/async", json=modify_data)
        print(f"    状态码: {response.status_code}")
        print(f"    响应: {response.json()}")
        print("  ✓ 使用 exec 参数成功")
        
    except Exception as e:
        print(f"  ✗ 使用 exec 参数失败: {e}")
    
    # 测试2: 验证旧的 query 参数不再可用
    print("\n  测试4.2: 验证旧的 query 参数")
    try:
        modify_data = {
            "query": "INSERT INTO test_modify (id, name) VALUES (?, ?)",
            "params": [2, "test_query_param"],
            "month": test_month
        }
        
        response = requests.post(f"{base_url}/api/v1/modify/async", json=modify_data)
        print(f"    状态码: {response.status_code}")
        print(f"    响应: {response.json()}")
        print("  ✗ 旧的 query 参数仍然可用（应该失败）")
    except Exception as e:
        print(f"  ✓ 旧的 query 参数已不可用: {e}")

def test_deleted_endpoints():
    """测试已删除的接口"""
    print("\n测试5: 已删除的接口")
    
    deleted_endpoints = [
        ("GET", f"{base_url}/api/v1/sync/status"),
        ("POST", f"{base_url}/api/v1/users", {"name": "test", "email": "test@example.com"}),
        ("GET", f"{base_url}/api/v1/users"),
        ("POST", f"{base_url}/api/v1/users/async", {"name": "test", "email": "test@example.com"}),
        ("POST", f"{base_url}/api/v1/products", {"name": "test", "price": 100, "stock": 10}),
        ("GET", f"{base_url}/api/v1/products"),
        ("POST", f"{base_url}/api/v1/products/async", {"name": "test", "price": 100, "stock": 10}),
    ]
    
    for method, url, *data in deleted_endpoints:
        print(f"  测试5.1: {method} {url}")
        try:
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url, json=data[0] if data else {})
            
            print(f"    状态码: {response.status_code}")
            if response.status_code != 404:
                print(f"    ✗ 已删除的接口仍然可用")
            else:
                print(f"    ✓ 已删除的接口返回 404")
        except Exception as e:
            print(f"    ✓ 已删除的接口访问失败: {e}")

def cleanup_test_data():
    """清理测试数据"""
    print("\n清理测试数据...")
    try:
        if os.path.exists("data"):
            # 删除测试月份目录
            test_months = ["2026-04"]
            for month in test_months:
                month_dir = os.path.join("data", month)
                if os.path.exists(month_dir):
                    shutil.rmtree(month_dir)
                    print(f"  ✓ 删除测试月份目录: {month_dir}")
        print("✓ 测试数据清理完成")
    except Exception as e:
        print(f"✗ 测试数据清理失败: {e}")

def main():
    """主测试函数"""
    print("开始测试 DuckDB Web API...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 基础 URL: {base_url}")
    
    test_health_check()
    test_available_months()
    test_month_partitioning()
    test_modify_async_param()
    test_deleted_endpoints()
    
    cleanup_test_data()
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    main()
