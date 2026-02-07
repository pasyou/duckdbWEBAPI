import asyncio
import aiohttp
import json
import time

async def test_sync_after_modification():
    print("=== 测试异步修改后的数据同步 ===")
    
    base_url = "http://localhost:8000/api/v1"
    
    # 测试1: 创建测试数据
    print("\n测试1: 创建测试用户")
    user_data = {
        "name": "同步测试用户",
        "email": "sync_test@example.com"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/users/async", json=user_data) as response:
            result = await response.json()
            user_id = result.get('user_id')
            print(f"用户ID: {user_id}")
    
    # 等待同步
    await asyncio.sleep(1)
    
    # 测试2: 通过 /api/v1/modify/async 更新用户
    print("\n测试2: 通过 /api/v1/modify/async 更新用户")
    update_data = {
        "query": "UPDATE users SET name = ?, email = ? WHERE id = ?",
        "params": ["同步测试用户_已更新", "sync_test_updated@example.com", user_id]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=update_data) as response:
            result = await response.json()
            print(f"更新结果: {result}")
    
    # 等待同步完成
    print("\n等待同步完成...")
    await asyncio.sleep(2)
    
    # 测试3: 检查变更日志
    print("\n测试3: 检查变更日志")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/sync/status") as response:
            sync_status = await response.json()
            print(f"同步状态: {json.dumps(sync_status, indent=2, ensure_ascii=False)}")
    
    # 测试4: 查询所有节点验证数据同步
    print("\n测试4: 查询所有节点验证数据同步")
    query_data = {
        "query": "SELECT * FROM users WHERE id = ?",
        "params": [user_id]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/query/async", json=query_data) as response:
            result = await response.json()
            
            if result.get('status') == 'success':
                print(f"查询结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # 检查所有节点的数据是否一致
                results = result.get('results', [])
                successful_nodes = [r for r in results if r.get('success')]
                
                print(f"\n成功查询的节点数: {len(successful_nodes)}/{len(results)}")
                
                if len(successful_nodes) > 1:
                    # 比较所有节点的数据
                    first_data = successful_nodes[0]['data']['rows']
                    all_match = True
                    
                    for node_result in successful_nodes[1:]:
                        if node_result['data']['rows'] != first_data:
                            all_match = False
                            break
                    
                    if all_match:
                        print("✓ 所有节点的数据一致！")
                    else:
                        print("✗ 节点数据不一致！")
                else:
                    print("✗ 查询节点数不足，无法验证同步")
            else:
                print(f"查询失败: {result}")
    
    # 测试5: 测试删除操作
    print("\n测试5: 测试删除操作")
    delete_data = {
        "query": "DELETE FROM users WHERE id = ?",
        "params": [user_id]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=delete_data) as response:
            result = await response.json()
            print(f"删除结果: {result}")
    
    # 等待同步
    await asyncio.sleep(2)
    
    # 测试6: 验证删除后所有节点都查不到数据
    print("\n测试6: 验证删除后所有节点都查不到数据")
    query_data = {
        "query": "SELECT * FROM users WHERE id = ?",
        "params": [user_id]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/query/async", json=query_data) as response:
            result = await response.json()
            
            if result.get('status') == 'success':
                results = result.get('results', [])
                all_empty = True
                
                for node_result in results:
                    if node_result.get('success') and node_result['data']['count'] > 0:
                        all_empty = False
                        print(f"✗ 节点 {node_result['node_id']} 仍然存在数据")
                
                if all_empty:
                    print("✓ 所有节点都已删除数据！")
            else:
                print(f"查询失败: {result}")
    
    print("\n=== 测试完成 ===")

async def main():
    try:
        await test_sync_after_modification()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())