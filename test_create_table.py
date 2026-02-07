import asyncio
import aiohttp
import json

async def test_create_table():
    url = "http://localhost:8000/api/v1/tables"
    
    # 测试创建基本表
    test_cases = [
        {
            "name": "创建基本用户表",
            "payload": {
                "table_name": "employees",
                "columns": [
                    {"name": "id", "type": "BIGINT PRIMARY KEY"},
                    {"name": "name", "type": "VARCHAR"},
                    {"name": "position", "type": "VARCHAR"},
                    {"name": "salary", "type": "DECIMAL(10,2)"},
                    {"name": "hire_date", "type": "TIMESTAMP"}
                ]
            }
        },
        {
            "name": "创建订单表",
            "payload": {
                "table_name": "orders",
                "columns": [
                    {"name": "order_id", "type": "BIGINT PRIMARY KEY"},
                    {"name": "customer_id", "type": "BIGINT"},
                    {"name": "total_amount", "type": "DECIMAL(10,2)"},
                    {"name": "order_date", "type": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "status", "type": "VARCHAR"}
                ]
            }
        },
        {
            "name": "创建简单表",
            "payload": {
                "table_name": "simple_table",
                "columns": [
                    {"name": "id", "type": "INTEGER PRIMARY KEY"},
                    {"name": "value", "type": "VARCHAR"}
                ]
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print(f"\n测试: {test_case['name']}")
            print(f"创建表: {test_case['payload']['table_name']}")
            
            try:
                async with session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(test_case['payload'])
                ) as response:
                    status = response.status
                    data = await response.json()
                    
                    print(f"状态码: {status}")
                    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if status == 200 and data.get('status') == 'success':
                        print("✓ 测试通过")
                    else:
                        print("✗ 测试失败")
                        
            except Exception as e:
                print(f"✗ 测试失败: {str(e)}")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    asyncio.run(test_create_table())
