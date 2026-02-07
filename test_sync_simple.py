import asyncio
import aiohttp
import json
import time

async def test_sync_with_insert():
    print("=== 测试 INSERT 操作的数据同步 ===")
    
    base_url = "http://localhost:8000/api/v1"
    
    # 测试1: 使用 INSERT 语句创建用户
    print("\n测试1: 使用 INSERT 语句创建用户")
    insert_data = {
        "query": "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        "params": [99999, "同步测试用户", "sync_test@example.com"]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=insert_data) as response:
            result = await response.json()
            print(f"插入结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 等待同步完成
    print("\n等待同步完成...")
    await asyncio.sleep(3)
    
    # 测试2: 检查变更日志
    print("\n测试2: 检查变更日志")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/sync/status") as response:
            sync_status = await response.json()
            print(f"同步状态: {json.dumps(sync_status, indent=2, ensure_ascii=False)}")
    
    # 测试3: 查询所有节点验证数据同步
    print("\n测试3: 查询所有节点验证数据同步")
    query_data = {
        "query": "SELECT * FROM users WHERE id = ?",
        "params": [99999]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/query/async", json=query_data) as response:
            result = await response.json()
            
            if 'results' in result:
                print(f"查询结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # 检查所有节点的数据是否一致
                results = result['results']
                successful_nodes = [r for r in results if r.get('success')]
                
                print(f"\n成功查询的节点数: {len(successful_nodes)}/{len(results)}")
                
                if len(successful_nodes) > 0:
                    # 检查有多少节点有数据
                    nodes_with_data = [r for r in successful_nodes if r['data']['count'] > 0]
                    print(f"有数据的节点数: {len(nodes_with_data)}")
                    
                    if len(nodes_with_data) > 0:
                        print(f"节点数据示例: {nodes_with_data[0]['data']['rows']}")
                    
                    if len(nodes_with_data) == len(successful_nodes):
                        print("✓ 所有节点都已同步数据！")
                    else:
                        print(f"✗ 只有 {len(nodes_with_data)}/{len(successful_nodes)} 个节点有数据")
                else:
                    print("✗ 没有节点成功查询")
            else:
                print(f"查询失败: {result}")
    
    # 测试4: 测试 UPDATE 操作
    print("\n测试4: 测试 UPDATE 操作")
    update_data = {
        "query": "UPDATE users SET name = ?, email = ? WHERE id = ?",
        "params": ["同步测试用户_已更新", "sync_test_updated@example.com", 99999]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=update_data) as response:
            result = await response.json()
            print(f"更新结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 等待同步
    print("\n等待同步完成...")
    await asyncio.sleep(3)
    
    # 测试5: 验证 UPDATE 后的数据
    print("\n测试5: 验证 UPDATE 后的数据")
    query_data = {
        "query": "SELECT * FROM users WHERE id = ?",
        "params": [99999]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/query/async", json=query_data) as response:
            result = await response.json()
            
            if 'results' in result:
                results = result['results']
                successful_nodes = [r for r in results if r.get('success')]
                nodes_with_data = [r for r in successful_nodes if r['data']['count'] > 0]
                
                if len(nodes_with_data) > 0:
                    print(f"节点数据: {nodes_with_data[0]['data']['rows']}")
                    
                    # 检查是否所有节点都有更新后的数据
                    all_updated = all(
                        len(r['data']['rows']) > 0 and 
                        r['data']['rows'][0][1] == "同步测试用户_已更新"
                        for r in nodes_with_data
                    )
                    
                    if all_updated:
                        print("✓ 所有节点都已更新数据！")
                    else:
                        print("✗ 部分节点数据未更新")
    
    # 测试6: 测试 DELETE 操作
    print("\n测试6: 测试 DELETE 操作")
    delete_data = {
        "query": "DELETE FROM users WHERE id = ?",
        "params": [99999]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=delete_data) as response:
            result = await response.json()
            print(f"删除结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 等待同步
    print("\n等待同步完成...")
    await asyncio.sleep(3)
    
    # 测试7: 验证删除后所有节点都查不到数据
    print("\n测试7: 验证删除后所有节点都查不到数据")
    query_data = {
        "query": "SELECT * FROM users WHERE id = ?",
        "params": [99999]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/query/async", json=query_data) as response:
            result = await response.json()
            
            if 'results' in result:
                results = result['results']
                successful_nodes = [r for r in results if r.get('success')]
                nodes_with_data = [r for r in successful_nodes if r['data']['count'] > 0]
                
                if len(nodes_with_data) == 0:
                    print("✓ 所有节点都已删除数据！")
                else:
                    print(f"✗ 还有 {len(nodes_with_data)} 个节点存在数据")
    
    print("\n=== 测试完成 ===")

async def main():
    try:
        await test_sync_with_insert()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())