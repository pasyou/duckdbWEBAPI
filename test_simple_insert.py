import asyncio
import aiohttp
import json

async def test_simple_insert():
    print("=== 测试简单插入 ===")
    
    base_url = "http://localhost:8000/api/v1"
    
    # 测试1: 执行不包含 id 列的 INSERT 语句
    print("\n测试1: 执行不包含 id 列的 INSERT 语句")
    insert_data = {
        "query": "INSERT INTO users (name, email) VALUES (?, ?)",
        "params": ["测试用户", "test@example.com"]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{base_url}/modify/async", json=insert_data) as response:
            status = response.status
            result = await response.json()
            print(f"状态码: {status}")
            print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    print("\n=== 测试完成 ===")

async def main():
    try:
        await test_simple_insert()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())