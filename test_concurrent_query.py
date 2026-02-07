import asyncio
import aiohttp
import time

async def execute_query(session, query_id):
    """执行单个查询请求"""
    url = "http://localhost:8000/api/v1/query/async"
    payload = {
        "query": "SELECT * FROM users"
    }
    
    start_time = time.time()
    try:
        async with session.post(url, json=payload, timeout=10) as response:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if response.status == 200:
                result = await response.json()
                node_id = result['results'][0]['node_id'] if result.get('results') else None
                success = True
            else:
                result = None
                node_id = None
                success = False
            
            return {
                'query_id': query_id,
                'status_code': response.status,
                'response_time': response_time,
                'node_id': node_id,
                'success': success
            }
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return {
            'query_id': query_id,
            'status_code': 0,
            'response_time': response_time,
            'error': str(e),
            'success': False
        }

async def test_concurrent_queries(concurrent_count=10):
    """测试并发查询"""
    print(f"=== 测试并发查询: {concurrent_count} 个并发请求 ===")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 配置连接池，限制并发连接数
    connector = aiohttp.TCPConnector(
        limit=min(concurrent_count, 50),  # 最大连接数
        limit_per_host=min(concurrent_count, 20),  # 每个主机最大连接数
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # 分批执行任务，每批最多50个
        batch_size = 50
        all_results = []
        
        for batch_start in range(0, concurrent_count, batch_size):
            batch_end = min(batch_start + batch_size, concurrent_count)
            batch_tasks = []
            
            print(f"\n执行批次: {batch_start + 1}-{batch_end}")
            
            for i in range(batch_start, batch_end):
                task = execute_query(session, i + 1)
                batch_tasks.append(task)
            
            # 执行当前批次的任务
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
            
            # 等待一小段时间，避免系统过载
            if batch_end < concurrent_count:
                await asyncio.sleep(0.5)
        
        # 计算总执行时间
        total_time = sum(result['response_time'] for result in all_results) / len(all_results) * len(all_results) / 1000 * 1000
    
    # 分析结果
    successful = 0
    failed = 0
    total_response_time = 0
    node_distribution = {}
    
    for result in all_results:
        if result['success']:
            successful += 1
            total_response_time += result['response_time']
            # 统计节点分布
            node_id = result['node_id']
            if node_id:
                node_distribution[node_id] = node_distribution.get(node_id, 0) + 1
        else:
            failed += 1
        
        # 打印每个查询的结果
        status = "成功" if result['success'] else "失败"
        node_info = f"节点: {result['node_id']}" if result.get('node_id') else ""
        error_info = f" 错误: {result.get('error')}" if not result['success'] else ""
        print(f"查询 {result['query_id']}: {status} | 响应时间: {result['response_time']:.2f}ms | {node_info}{error_info}")
    
    # 打印统计信息
    print("\n=== 测试结果统计 ===")
    print(f"总请求数: {concurrent_count}")
    print(f"成功数: {successful}")
    print(f"失败数: {failed}")
    print(f"总执行时间: {total_time:.2f}ms")
    print(f"平均响应时间: {total_response_time / successful:.2f}ms" if successful > 0 else "无成功响应")
    print(f"并发查询吞吐量: {concurrent_count / (total_time / 1000):.2f} 查询/秒")
    
    if node_distribution:
        print("\n=== 节点分布 ===")
        for node_id, count in sorted(node_distribution.items()):
            print(f"节点 {node_id}: {count} 次查询")
    
    print(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """主函数"""
    for i in range(50000000):
        await test_concurrent_queries(50)
        await asyncio.sleep(1)
    # 测试不同并发数，避免过高的并发导致系统过载
    concurrent_counts = [5, 10, 20, 50,100]
    
    for count in concurrent_counts:
        print("\n" + "="*60)
        await test_concurrent_queries(count)
        print("="*60 + "\n")
        # 等待一秒，避免系统过载
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
