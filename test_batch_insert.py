import urllib.request
import urllib.parse
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def make_request(method, endpoint, data=None, params=None):
    url = BASE_URL + endpoint
    
    if params:
        query_string = urllib.parse.urlencode(params)
        url += f"?{query_string}"
    
    if method == "GET":
        req = urllib.request.Request(url)
    else:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP Error {e.code}", "status_code": e.code}
    except urllib.error.URLError as e:
        return {"error": f"URL Error: {e.reason}", "status_code": 0}
    except Exception as e:
        return {"error": str(e), "status_code": 0}

def test_batch_insert():
    print("=== 测试批量插入功能 ===\n")
    
    # 测试1: 单条插入（对比基准）
    print("1. 单条插入（对比基准）")
    start_time = time.time()
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO users (name, email) VALUES (?, ?)",
        "params": ["单条用户", "single@example.com"]
    })
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    print(f"响应: {response}")
    print(f"执行时间: {elapsed_time:.2f}ms\n")
    
    # 等待同步完成
    time.sleep(0.5)
    
    # 测试2: 批量插入5条用户
    print("2. 批量插入5条用户")
    start_time = time.time()
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO users (name, email) VALUES (?, ?)",
        "is_batch": True,
        "batch_params": [
            ["批量用户1", "batch1@example.com"],
            ["批量用户2", "batch2@example.com"],
            ["批量用户3", "batch3@example.com"],
            ["批量用户4", "batch4@example.com"],
            ["批量用户5", "batch5@example.com"]
        ]
    })
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    print(f"执行时间: {elapsed_time:.2f}ms")
    print(f"总操作数: {response.get('total_operations', 0)}")
    print(f"成功操作数: {response.get('successful_operations', 0)}")
    print(f"失败操作数: {response.get('failed_operations', 0)}\n")
    
    # 等待同步完成
    time.sleep(0.5)
    
    # 测试3: 批量插入10条产品
    print("3. 批量插入10条产品")
    start_time = time.time()
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        "is_batch": True,
        "batch_params": [
            ["产品1", 99.99, 100],
            ["产品2", 199.99, 50],
            ["产品3", 299.99, 30],
            ["产品4", 399.99, 20],
            ["产品5", 499.99, 10],
            ["产品6", 599.99, 5],
            ["产品7", 699.99, 8],
            ["产品8", 799.99, 15],
            ["产品9", 899.99, 12],
            ["产品10", 999.99, 25]
        ]
    })
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    print(f"执行时间: {elapsed_time:.2f}ms")
    print(f"总操作数: {response.get('total_operations', 0)}")
    print(f"成功操作数: {response.get('successful_operations', 0)}")
    print(f"失败操作数: {response.get('failed_operations', 0)}\n")
    
    # 等待同步完成
    time.sleep(0.5)
    
    # 测试4: 批量插入到指定月份
    print("4. 批量插入到指定月份（2026-01）")
    start_time = time.time()
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO users (name, email) VALUES (?, ?)",
        "is_batch": True,
        "month": "2026-01",
        "batch_params": [
            ["历史用户1", "history1@example.com"],
            ["历史用户2", "history2@example.com"],
            ["历史用户3", "history3@example.com"]
        ]
    })
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    print(f"执行时间: {elapsed_time:.2f}ms")
    print(f"总操作数: {response.get('total_operations', 0)}")
    print(f"成功操作数: {response.get('successful_operations', 0)}")
    print(f"失败操作数: {response.get('failed_operations', 0)}\n")
    
    # 等待同步完成
    time.sleep(0.5)
    
    # 测试5: 批量插入订单数据
    print("5. 批量插入订单数据")
    start_time = time.time()
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO orders (customer_id, total_amount, status) VALUES (?, ?, ?)",
        "is_batch": True,
        "batch_params": [
            [1, 199.99, "pending"],
            [2, 299.99, "shipped"],
            [3, 399.99, "delivered"],
            [4, 499.99, "pending"],
            [5, 599.99, "shipped"]
        ]
    })
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    print(f"执行时间: {elapsed_time:.2f}ms")
    print(f"总操作数: {response.get('total_operations', 0)}")
    print(f"成功操作数: {response.get('successful_operations', 0)}")
    print(f"失败操作数: {response.get('failed_operations', 0)}\n")
    
    # 等待同步完成
    time.sleep(0.5)
    
    # 测试6: 验证批量插入的数据
    print("6. 验证批量插入的数据")
    response = make_request("POST", "/api/v1/query/async", {
        "query": "SELECT COUNT(*) as user_count FROM users"
    })
    if 'results' in response and len(response['results']) > 0:
        data = response['results'][0].get('data', {})
        rows = data.get('rows', [])
        if rows and len(rows) > 0:
            count = rows[0][0]
            print(f"当前月份的用户总数: {count}")
    
    # 测试7: 大批量插入（20条）
    print("7. 大批量插入（20条）")
    start_time = time.time()
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        "is_batch": True,
        "batch_params": [[f"产品{i}", i * 100 + 99.99, i * 10 + 5] for i in range(1, 21)]
    })
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    print(f"执行时间: {elapsed_time:.2f}ms")
    print(f"总操作数: {response.get('total_operations', 0)}")
    print(f"成功操作数: {response.get('successful_operations', 0)}")
    print(f"失败操作数: {response.get('failed_operations', 0)}")
    print(f"平均每条耗时: {elapsed_time / 20:.2f}ms\n")
    
    # 等待同步完成
    time.sleep(0.5)
    
    # 测试8: 性能对比
    print("8. 性能对比：单条插入 vs 批量插入")
    
    # 单条插入10次
    single_insert_times = []
    for i in range(1, 6):
        start_time = time.time()
        response = make_request("POST", "/api/v1/modify/async", {
            "query": "INSERT INTO users (name, email) VALUES (?, ?)",
            "params": [f"性能对比用户{i}", f"perf{i}@example.com"]
        })
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        single_insert_times.append(elapsed_time)
        time.sleep(0.1)
    
    avg_single_time = sum(single_insert_times) / len(single_insert_times)
    print(f"单条插入5次，平均耗时: {avg_single_time:.2f}ms")
    
    # 批量插入5条
    start_time = time.time()
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO users (name, email) VALUES (?, ?)",
        "is_batch": True,
        "batch_params": [[f"批量对比用户{i}", f"batch_perf{i}@example.com"] for i in range(1, 6)]
    })
    end_time = time.time()
    batch_insert_time = (end_time - start_time) * 1000
    print(f"批量插入5条，总耗时: {batch_insert_time:.2f}ms")
    print(f"批量插入平均每条耗时: {batch_insert_time / 5:.2f}ms")
    print(f"性能提升: {(avg_single_time * 5 - batch_insert_time) / (avg_single_time * 5) * 100:.1f}%\n")
    
    # 测试9: 容错性测试
    print("9. 容错性测试：部分参数错误")
    response = make_request("POST", "/api/v1/modify/async", {
        "query": "INSERT INTO users (name, email) VALUES (?, ?)",
        "is_batch": True,
        "batch_params": [
            ["容错用户1", "error1@example.com"],
            ["容错用户2", "error2@example.com"],
            ["容错用户3", "error3@example.com"],
            ["容错用户4", "error4@example.com"],
            ["容错用户5", "error5@example.com"]
        ]
    })
    print(f"响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
    print(f"状态: {response.get('status', 'unknown')}")
    print(f"成功操作数: {response.get('successful_operations', 0)}")
    print(f"失败操作数: {response.get('failed_operations', 0)}")
    if response.get('errors'):
        print(f"错误信息: {response['errors']}\n")
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    try:
        test_batch_insert()
    except Exception as e:
        print(f"测试出错: {e}")
        import traceback
        traceback.print_exc()