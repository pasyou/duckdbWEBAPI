import asyncio
import aiohttp
import json

async def test_table_schema():
    url = "http://localhost:8000/api/v1/tables"
    
    # 测试用例
    test_cases = [
        {
            "name": "查询users表结构",
            "table_name": "users",
            "expected_status": 200
        },
        {
            "name": "查询products表结构",
            "table_name": "products",
            "expected_status": 200
        },
        {
            "name": "查询employees表结构（如果存在）",
            "table_name": "employees",
            "expected_status": 200
        },
        {
            "name": "查询不存在的表",
            "table_name": "non_existent_table",
            "expected_status": 200
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print(f"\n测试: {test_case['name']}")
            print(f"表名: {test_case['table_name']}")
            
            try:
                async with session.get(
                    f"{url}/{test_case['table_name']}/schema"
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    print(f"状态码: {status}")
                    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if status == test_case['expected_status']:
                        print("✓ 测试通过")
                    else:
                        print("✗ 测试失败")
                        
            except Exception as e:
                print(f"✗ 测试失败: {str(e)}")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    asyncio.run(test_table_schema())
