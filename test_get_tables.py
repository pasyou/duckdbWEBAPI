import asyncio
import aiohttp
import json

async def test_get_tables():
    url = "http://localhost:8000/api/v1/tables"
    
    print("测试: 查询库中所有表")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                status = response.status
                data = await response.json()
                
                print(f"状态码: {status}")
                print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if status == 200:
                    if data.get('status') == 'success':
                        print(f"✓ 测试通过，找到 {data.get('count', 0)} 个表")
                        for table in data.get('tables', []):
                            print(f"  - {table['name']}")
                    else:
                        print("✗ 测试失败: API返回错误状态")
                else:
                    print("✗ 测试失败: HTTP状态码错误")
                    
        except Exception as e:
            print(f"✗ 测试失败: {str(e)}")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    asyncio.run(test_get_tables())
