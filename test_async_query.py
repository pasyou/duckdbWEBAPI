import asyncio
import aiohttp
import json
import time

async def test_async_query():
    print("=== 测试异步查询接口 ===")
    
    url = "http://localhost:8000/api/v1/query/async"
    
    # 测试1: 查询用户列表
    print("\n测试1: 查询用户列表")
    query = "SELECT * FROM users ORDER BY id DESC LIMIT 10"
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query}) as response:
            status = response.status
            result = await response.json()
    
    elapsed = time.time() - start_time
    print(f"状态码: {status}")
    print(f"耗时: {elapsed:.3f}秒")
    print(f"成功节点数: {sum(1 for r in result.get('results', []) if r['success'])}")
    print(f"总节点数: {len(result.get('results', []))}")
    
    if result.get('results'):
        first_node_result = next((r for r in result['results'] if r['success']), None)
        if first_node_result:
            print(f"返回记录数: {first_node_result['data']['count']}")
    
    # 测试2: 查询产品列表
    print("\n测试2: 查询产品列表")
    query = "SELECT * FROM products WHERE price > ?"
    params = [1000]
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query, "params": params}) as response:
            status = response.status
            result = await response.json()
    
    elapsed = time.time() - start_time
    print(f"状态码: {status}")
    print(f"耗时: {elapsed:.3f}秒")
    print(f"成功节点数: {sum(1 for r in result.get('results', []) if r['success'])}")
    
    # 测试3: 并发查询
    print("\n测试3: 并发执行10次查询")
    
    async def execute_concurrent_query():
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"query": "SELECT COUNT(*) FROM users"}) as response:
                return await response.json()
    
    start_time = time.time()
    tasks = [execute_concurrent_query() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start_time
    
    print(f"并发执行10次查询，总耗时: {elapsed:.3f}秒")
    print(f"平均每次查询耗时: {elapsed/10:.3f}秒")
    print(f"成功查询数: {sum(1 for r in results if r.get('completed'))}")
    
    # 测试4: 错误查询
    print("\n测试4: 错误查询")
    query = "SELECT * FROM non_existent_table"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query}) as response:
            status = response.status
            result = await response.json()
    
    print(f"状态码: {status}")
    print(f"错误信息: {result.get('error', '无')}")

async def main():
    print("开始测试异步查询接口")
    print("=" * 60)
    
    try:
        await test_async_query()
    except Exception as e:
        print(f"测试失败: {e}")
    
    print("=" * 60)
    print("测试完成")

if __name__ == "__main__":
    asyncio.run(main())
