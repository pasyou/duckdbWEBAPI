import asyncio
import aiohttp
import json
import time

async def test_async_modification():
    print("=== 测试异步增删改操作 ===")
    
    base_url = "http://localhost:8000/api/v1"
    
    # 测试1: 异步创建用户
    print("\n测试1: 异步创建用户")
    user_data = {
        "name": "异步测试用户",
        "email": "async_test@example.com"
    }
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/users/async", json=user_data) as response:
            status = response.status
            result = await response.json()
    
    elapsed = time.time() - start_time
    print(f"状态码: {status}")
    print(f"耗时: {elapsed:.3f}秒")
    print(f"用户ID: {result.get('user_id')}")
    print(f"状态: {result.get('status')}")
    
    # 测试2: 异步创建产品
    print("\n测试2: 异步创建产品")
    product_data = {
        "name": "异步测试产品",
        "price": 999.99,
        "stock": 50
    }
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/products/async", json=product_data) as response:
            status = response.status
            result = await response.json()
    
    elapsed = time.time() - start_time
    print(f"状态码: {status}")
    print(f"耗时: {elapsed:.3f}秒")
    print(f"产品ID: {result.get('product_id')}")
    print(f"状态: {result.get('status')}")
    
    # 测试3: 异步更新数据
    print("\n测试3: 异步更新产品")
    update_data = {
        "query": "UPDATE products SET price = ?, stock = ? WHERE name = ?",
        "params": [1299.99, 30, "异步测试产品"]
    }
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=update_data) as response:
            status = response.status
            result = await response.json()
    
    elapsed = time.time() - start_time
    print(f"状态码: {status}")
    print(f"耗时: {elapsed:.3f}秒")
    print(f"影响行数: {result.get('affected_rows')}")
    print(f"状态: {result.get('status')}")
    
    # 测试4: 异步删除数据
    print("\n测试4: 异步删除用户")
    delete_data = {
        "query": "DELETE FROM users WHERE email = ?",
        "params": ["async_test@example.com"]
    }
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=delete_data) as response:
            status = response.status
            result = await response.json()
    
    elapsed = time.time() - start_time
    print(f"状态码: {status}")
    print(f"耗时: {elapsed:.3f}秒")
    print(f"影响行数: {result.get('affected_rows')}")
    print(f"状态: {result.get('status')}")
    
    # 测试5: 并发执行增删改操作
    print("\n测试5: 并发执行10次增删改操作")
    
    async def execute_concurrent_operation():
        async with aiohttp.ClientSession() as session:
            # 创建临时用户
            user_data = {
                "name": f"并发用户_{int(time.time() * 1000)}",
                "email": f"concurrent_{int(time.time() * 1000)}@example.com"
            }
            
            # 创建用户
            async with session.post(f"{base_url}/users/async", json=user_data) as response:
                create_result = await response.json()
            
            # 删除用户
            if create_result.get('user_id'):
                delete_data = {
                    "query": "DELETE FROM users WHERE id = ?",
                    "params": [create_result['user_id']]
                }
                async with session.post(f"{base_url}/modify/async", json=delete_data) as response:
                    await response.json()
            
            return create_result
    
    start_time = time.time()
    tasks = [execute_concurrent_operation() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start_time
    
    print(f"并发执行10次操作，总耗时: {elapsed:.3f}秒")
    print(f"平均每次操作耗时: {elapsed/10:.3f}秒")
    print(f"成功操作数: {sum(1 for r in results if r.get('status') == 'success')}")

async def main():
    print("开始测试异步增删改操作")
    print("=" * 60)
    
    try:
        await test_async_modification()
    except Exception as e:
        print(f"测试失败: {e}")
    
    print("=" * 60)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(main())
