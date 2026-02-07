import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from DuckDBIncrementalSync import DuckDBIncrementalSync
from concurrent_query_processor import ConcurrentQueryProcessor

async def test_basic_operations():
    print("=== 测试基本操作 ===")
    sync_manager = DuckDBIncrementalSync(num_nodes=4, data_dir='test_data', max_workers=2)
    
    print("创建用户...")
    user_id = sync_manager.insert_user("张三", "zhangsan@example.com")
    print(f"用户创建成功，ID: {user_id}")
    
    print("创建产品...")
    product_id = sync_manager.insert_product("笔记本电脑", 5999.99, 100)
    print(f"产品创建成功，ID: {product_id}")
    
    time.sleep(2)
    
    print("\n同步状态:")
    status = sync_manager.get_sync_status()
    print(f"最后同步时间: {status['last_sync']}")
    print(f"活跃节点数: {sum(1 for node in status['nodes'] if node['status'] == 'active')}")
    
    sync_manager.close()
    print("基本操作测试完成\n")

async def test_concurrent_query():
    print("=== 测试并发查询 ===")
    sync_manager = DuckDBIncrementalSync(num_nodes=4, data_dir='test_data', max_workers=2)
    processor = ConcurrentQueryProcessor(max_workers=4, timeout=30)
    
    def query_node(conn, query, params):
        try:
            result = conn.execute(query, params).fetchall()
            columns = [desc[0] for desc in conn.description]
            return {
                'columns': columns,
                'rows': result,
                'count': len(result)
            }
        except Exception as e:
            raise Exception(f"查询失败: {e}")
    
    print("准备测试数据...")
    for i in range(10):
        sync_manager.insert_user(f"用户{i}", f"user{i}@example.com")
    
    time.sleep(2)
    
    print("查询用户1...")
    query_id = sync_manager.execute_query("SELECT * FROM users WHERE name = ?", ["用户1"])
    print(f"查询ID: {query_id}")
    
    print("获取查询结果...")
    result = sync_manager.get_query_result(query_id)
    print(f"查询结果: {result}")







    print("执行并发查询...")
    params_list = []
    for node_id in range(4):
        params_list.append((sync_manager.nodes[node_id], "SELECT * FROM users", []))
    
    result = await processor.execute_concurrent_query(
        lambda conn, q, p: query_node(conn, q, p),
        params_list,
        "test_query_1"
    )
    
    print(f"查询完成，耗时: {result['execution_time']:.2f}秒")
    print(f"成功节点数: {result['successful_nodes']}")
    print(f"失败节点数: {result['failed_nodes']}")
    
    for node_result in result['results']:
        print(f"节点{node_result['node_id']}: 返回{node_result['data']['count']}条记录")
    
    print("\n查询统计:")
    stats = processor.get_stats()
    print(f"总查询数: {stats['total_queries']}")
    print(f"成功查询数: {stats['successful_queries']}")
    print(f"平均执行时间: {stats['avg_execution_time']:.2f}秒")
    
    sync_manager.close()
    processor.shutdown()
    print("并发查询测试完成\n")

async def test_concurrent_insert():
    print("=== 测试并发插入 ===")
    sync_manager = DuckDBIncrementalSync(num_nodes=4, data_dir='test_data', max_workers=2)
    
    print("并发创建100个用户...")
    start_time = time.time()
    
    tasks = []
    for i in range(100):
        user_id = sync_manager.insert_user(f"并发用户{i}", f"concurrent{i}@example.com")
        tasks.append(user_id)
    
    end_time = time.time()
    print(f"插入完成，耗时: {end_time - start_time:.2f}秒")
    print(f"平均每条记录: {(end_time - start_time) / 100:.4f}秒")
    
    time.sleep(3)
    
    print("\n同步状态:")
    status = sync_manager.get_sync_status()
    print(f"最后同步时间: {status['last_sync']}")
    print(f"待处理变更: {status['pending_changes']}")
    
    sync_manager.close()
    print("并发插入测试完成\n")

async def test_query_performance():
    print("=== 测试查询性能 ===")
    sync_manager = DuckDBIncrementalSync(num_nodes=4, data_dir='test_data', max_workers=2)
    processor = ConcurrentQueryProcessor(max_workers=4, timeout=30)
    
    print("准备大量测试数据...")
    for i in range(50):
        sync_manager.insert_product(f"产品{i}", i * 100 + 99.99, i * 10)
    
    time.sleep(3)
    
    def query_node(conn, query, params):
        try:
            result = conn.execute(query, params).fetchall()
            columns = [desc[0] for desc in conn.description]
            return {
                'columns': columns,
                'rows': result,
                'count': len(result)
            }
        except Exception as e:
            raise Exception(f"查询失败: {e}")
    
    print("执行10次并发查询...")
    total_time = 0
    
    for i in range(10):
        params_list = []
        for node_id in range(4):
            params_list.append((sync_manager.nodes[node_id], "SELECT * FROM products WHERE price > ?", [1000]))
        
        start = time.time()
        result = await processor.execute_concurrent_query(
            lambda conn, q, p: query_node(conn, q, p),
            params_list,
            f"perf_query_{i}"
        )
        elapsed = time.time() - start
        total_time += elapsed
        print(f"查询{i+1}: {elapsed:.3f}秒, 返回{result['successful_nodes']}个成功结果")
    
    avg_time = total_time / 10
    print(f"\n平均查询时间: {avg_time:.3f}秒")
    print(f"每秒查询数: {1/avg_time:.2f}")
    
    sync_manager.close()
    processor.shutdown()
    print("查询性能测试完成\n")

async def main():
    print("DuckDB并发Web API测试套件\n")
    print("=" * 50)
    
    try:
        await test_basic_operations()
        await test_concurrent_query()
        await test_concurrent_insert()
        await test_query_performance()
        
        print("=" * 50)
        print("所有测试完成!")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":

    sync_manager = DuckDBIncrementalSync(num_nodes=4, data_dir='test_data', max_workers=2)
    
    query_id = sync_manager.execute_query("SELECT * FROM users WHERE name = ?", ["用户1"])
    print(f"查询ID: {query_id}")
    

    pass
    #asyncio.run(main())
