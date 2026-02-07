import asyncio
import aiohttp
import json

async def test_delete_insert_query():
    print("=== 测试删除、插入和查询操作 ===")
    
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        # 1. 执行删除所有用户的操作
        print("\n1. 执行删除所有用户的操作")
        delete_data = {
            "query": "DELETE FROM users"
        }
        
        try:
            async with session.post(f"{base_url}/modify/async", json=delete_data) as response:
                status = response.status
                result = await response.json()
                print(f"状态码: {status}")
                print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"删除操作失败: {e}")
        
        # 2. 执行插入新用户的操作
        print("\n2. 执行插入新用户的操作")
        insert_data = {
            "query": "INSERT INTO users (name, email) VALUES (?, ?)",
            "params": ["同步测试888用户", "sync_test@example.com"]
        }
        
        try:
            async with session.post(f"{base_url}/modify/async", json=insert_data) as response:
                status = response.status
                result = await response.json()
                print(f"状态码: {status}")
                print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"插入操作失败: {e}")
        
        # 3. 执行查询所有用户的操作
        print("\n3. 执行查询所有用户的操作")
        query_data = {
            "query": "SELECT * FROM users"
        }
        
        try:
            async with session.post(f"{base_url}/query/async", json=query_data) as response:
                status = response.status
                result = await response.json()
                print(f"状态码: {status}")
                print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"查询操作失败: {e}")

async def main():
    await test_delete_insert_query()

if __name__ == "__main__":
    asyncio.run(main())