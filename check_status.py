import duckdb

# 连接到主节点数据库
conn = duckdb.connect('data/node_0.db')

try:
    # 检查序列当前值
    try:
        seq_value = conn.execute("SELECT currval('change_log_seq')").fetchone()
        if seq_value:
            print('序列当前值:', seq_value[0])
        else:
            print('序列当前值: 未初始化')
    except Exception as e:
        print('获取序列当前值失败:', e)
    
    # 检查变更日志最大ID
    max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM _change_log").fetchone()
    if max_id:
        print('变更日志最大ID:', max_id[0])
    else:
        print('变更日志最大ID: 0')
    
    # 检查users表的最大ID
    users_max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM users").fetchone()
    if users_max_id:
        print('users表最大ID:', users_max_id[0])
    else:
        print('users表最大ID: 0')
    
    # 检查users表中的数据
    print('\nusers表中的数据:')
    users_data = conn.execute("SELECT id, name, email FROM users ORDER BY id DESC LIMIT 5").fetchall()
    for row in users_data:
        print(row)
    
finally:
    conn.close()