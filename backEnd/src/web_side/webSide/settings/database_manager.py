"""
数据库管理API
提供类似Navicat的数据库管理功能
"""
from flask import Blueprint, request, jsonify, send_file
from src.log import Log
import sqlite3
import os
import sys
import csv
import json
import io
from datetime import datetime

database_manager_bp = Blueprint('database_manager', __name__, url_prefix='/database')

# 数据库路径
# 支持PyInstaller打包后的路径
def get_base_path():
    """获取应用程序的基础路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

DB_PATH = os.path.join(get_base_path(), 'csweaponmanager.db')

print("✅ 数据库管理蓝图已加载")
print(f"📁 数据库路径: {DB_PATH}")
print(f"🔧 运行模式: {'打包exe' if getattr(sys, 'frozen', False) else '开发环境'}")


def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        Log().write_log(f"数据库连接失败: {str(e)}", 'ERROR')
        raise


def get_db_size():
    """获取数据库文件大小"""
    try:
        if os.path.exists(DB_PATH):
            size_bytes = os.path.getsize(DB_PATH)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
        return "0 B"
    except Exception as e:
        Log().write_log(f"获取数据库大小失败: {str(e)}", 'ERROR')
        return "未知"


@database_manager_bp.route('/tables', methods=['GET'])
def get_tables():
    """获取所有表列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = []
        for row in cursor.fetchall():
            table_name = row['name']
            try:
                # 获取表的行数
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                count = cursor.fetchone()['count']
            except:
                count = 0
            
            tables.append({
                'name': table_name,
                'rowCount': count
            })
        
        conn.close()
        Log().write_log(f"获取表列表成功，共 {len(tables)} 个表", 'INFO')
        return jsonify(tables)
    
    except Exception as e:
        Log().write_log(f"获取表列表失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/data', methods=['GET'])
def get_table_data(table_name):
    """获取表数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取表数据
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()
        
        # 获取列名
        columns = [{'name': description[0]} for description in cursor.description]
        
        # 转换为字典列表
        data = []
        for row in rows:
            row_dict = {}
            for key in row.keys():
                value = row[key]
                # 处理特殊类型
                if value is None:
                    row_dict[key] = None
                elif isinstance(value, bytes):
                    row_dict[key] = value.decode('utf-8', errors='ignore')
                else:
                    row_dict[key] = value
            data.append(row_dict)
        
        conn.close()
        
        Log().write_log(f"获取表 {table_name} 数据成功，共 {len(data)} 行", 'INFO')
        return jsonify({
            'columns': columns,
            'rows': data
        })
    
    except Exception as e:
        Log().write_log(f"获取表数据失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/structure', methods=['GET'])
def get_table_structure(table_name):
    """获取表结构"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        structure = []
        for row in cursor.fetchall():
            structure.append(dict(row))
        
        # 获取建表语句
        cursor.execute(f"""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name='{table_name}'
        """)
        sql_result = cursor.fetchone()
        create_sql = sql_result['sql'] if sql_result else ''
        
        # 获取表信息
        cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
        row_count = cursor.fetchone()['count']
        
        conn.close()
        
        Log().write_log(f"获取表 {table_name} 结构成功", 'INFO')
        return jsonify({
            'structure': structure,
            'sql': create_sql,
            'info': {
                'createTime': '-',
                'rowCount': row_count
            }
        })
    
    except Exception as e:
        Log().write_log(f"获取表结构失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/row', methods=['POST'])
def add_row(table_name):
    """新增数据行"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': '数据不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 过滤掉空值的字段
        filtered_data = {k: v for k, v in data.items() if v is not None and v != ''}
        
        if not filtered_data:
            return jsonify({'error': '没有有效的数据'}), 400
        
        # 构建INSERT语句
        columns = ', '.join([f'`{k}`' for k in filtered_data.keys()])
        placeholders = ', '.join(['?' for _ in filtered_data.keys()])
        values = list(filtered_data.values())
        
        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        
        conn.commit()
        conn.close()
        
        Log().write_log(f"新增数据到表 {table_name} 成功", 'INFO')
        return jsonify({'success': True, 'message': '新增成功'})
    
    except Exception as e:
        Log().write_log(f"新增数据失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/row', methods=['PUT'])
def update_row(table_name):
    """更新数据行"""
    try:
        request_data = request.json
        data = request_data.get('data', {})
        
        if not data:
            return jsonify({'error': '数据不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取主键
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        primary_keys = []
        for row in cursor.fetchall():
            if row['pk'] > 0:
                primary_keys.append(row['name'])
        
        if not primary_keys:
            conn.close()
            return jsonify({'error': '表没有主键，无法更新'}), 400
        
        # 构建WHERE条件
        where_conditions = []
        where_values = []
        for pk in primary_keys:
            if pk in data:
                where_conditions.append(f"`{pk}` = ?")
                where_values.append(data[pk])
        
        if not where_conditions:
            conn.close()
            return jsonify({'error': '缺少主键值'}), 400
        
        # 构建UPDATE语句
        update_fields = [k for k in data.keys() if k not in primary_keys]
        if not update_fields:
            conn.close()
            return jsonify({'error': '没有要更新的字段'}), 400
        
        set_clause = ', '.join([f"`{k}` = ?" for k in update_fields])
        set_values = [data[k] for k in update_fields]
        
        where_clause = ' AND '.join(where_conditions)
        
        sql = f"UPDATE `{table_name}` SET {set_clause} WHERE {where_clause}"
        cursor.execute(sql, set_values + where_values)
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        Log().write_log(f"更新表 {table_name} 数据成功，影响 {affected_rows} 行", 'INFO')
        return jsonify({'success': True, 'message': f'更新成功，影响 {affected_rows} 行'})
    
    except Exception as e:
        Log().write_log(f"更新数据失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/row', methods=['DELETE'])
def delete_row(table_name):
    """删除数据行"""
    try:
        request_data = request.json
        row = request_data.get('row', {})
        
        if not row:
            return jsonify({'error': '数据不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取主键
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        primary_keys = []
        for r in cursor.fetchall():
            if r['pk'] > 0:
                primary_keys.append(r['name'])
        
        if not primary_keys:
            conn.close()
            return jsonify({'error': '表没有主键，无法删除'}), 400
        
        # 构建WHERE条件
        where_conditions = []
        where_values = []
        for pk in primary_keys:
            if pk in row:
                where_conditions.append(f"`{pk}` = ?")
                where_values.append(row[pk])
        
        if not where_conditions:
            conn.close()
            return jsonify({'error': '缺少主键值'}), 400
        
        where_clause = ' AND '.join(where_conditions)
        
        # 删除数据
        sql = f"DELETE FROM `{table_name}` WHERE {where_clause}"
        cursor.execute(sql, where_values)
        
        conn.commit()
        affected_rows = cursor.rowcount
        conn.close()
        
        Log().write_log(f"删除表 {table_name} 数据成功，影响 {affected_rows} 行", 'INFO')
        return jsonify({'success': True, 'message': f'删除成功，影响 {affected_rows} 行'})
    
    except Exception as e:
        Log().write_log(f"删除数据失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/delete-batch', methods=['POST'])
def delete_batch(table_name):
    """批量删除数据"""
    try:
        request_data = request.json
        rows = request_data.get('rows', [])
        
        if not rows:
            return jsonify({'error': '没有选择要删除的数据'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取主键
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        primary_keys = []
        for r in cursor.fetchall():
            if r['pk'] > 0:
                primary_keys.append(r['name'])
        
        if not primary_keys:
            conn.close()
            return jsonify({'error': '表没有主键，无法删除'}), 400
        
        # 批量删除
        deleted_count = 0
        for row in rows:
            where_conditions = []
            where_values = []
            for pk in primary_keys:
                if pk in row:
                    where_conditions.append(f"`{pk}` = ?")
                    where_values.append(row[pk])
            
            if where_conditions:
                where_clause = ' AND '.join(where_conditions)
                sql = f"DELETE FROM `{table_name}` WHERE {where_clause}"
                cursor.execute(sql, where_values)
                deleted_count += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        Log().write_log(f"批量删除表 {table_name} 数据成功，删除 {deleted_count} 行", 'INFO')
        return jsonify({'success': True, 'message': f'成功删除 {deleted_count} 条数据'})
    
    except Exception as e:
        Log().write_log(f"批量删除失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/export', methods=['GET'])
def export_table(table_name):
    """导出表数据"""
    try:
        export_format = request.args.get('format', 'csv')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取数据
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        conn.close()
        
        if export_format == 'csv':
            # 导出为CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(columns)
            for row in rows:
                writer.writerow([str(v) if v is not None else '' for v in row])
            
            output.seek(0)
            
            Log().write_log(f"导出表 {table_name} 为CSV成功", 'INFO')
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'{table_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        
        elif export_format == 'json':
            # 导出为JSON
            data = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                data.append(row_dict)
            
            Log().write_log(f"导出表 {table_name} 为JSON成功", 'INFO')
            return send_file(
                io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'{table_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
        
        else:
            return jsonify({'error': '不支持的导出格式'}), 400
    
    except Exception as e:
        Log().write_log(f"导出表数据失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/query', methods=['POST'])
def execute_query():
    """执行SQL查询（支持多条语句）"""
    try:
        request_data = request.json
        sql = request_data.get('sql', '').strip()
        
        if not sql:
            return jsonify({'error': 'SQL语句不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 分割多条SQL语句（按分号分割）
        statements = []
        current_statement = ''
        in_string = False
        string_char = None
        
        for char in sql:
            if char in ("'", '"') and (not current_statement or current_statement[-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                current_statement += char
            elif char == ';' and not in_string:
                stmt = current_statement.strip()
                if stmt:
                    statements.append(stmt)
                current_statement = ''
            else:
                current_statement += char
        
        # 处理最后一条语句（可能没有分号结尾）
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # 过滤空语句
        statements = [stmt for stmt in statements if stmt and stmt.strip()]
        
        if not statements:
            conn.close()
            return jsonify({'error': '没有有效的SQL语句'}), 400
        
        # 执行多条语句
        total_affected_rows = 0
        results = []
        last_select_result = None
        last_select_columns = []
        execution_details = []
        
        for i, statement in enumerate(statements, 1):
            try:
                statement_upper = statement.upper().strip()
                
                # 执行语句
                cursor.execute(statement)
                
                # 如果是SELECT查询，保存结果
                if statement_upper.startswith('SELECT'):
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    data = []
                    for row in rows:
                        row_dict = {}
                        for key in row.keys():
                            value = row[key]
                            if value is None:
                                row_dict[key] = None
                            elif isinstance(value, bytes):
                                row_dict[key] = value.decode('utf-8', errors='ignore')
                            else:
                                row_dict[key] = value
                        data.append(row_dict)
                    
                    last_select_result = data
                    last_select_columns = columns
                    execution_details.append({
                        'statement': statement[:100] + ('...' if len(statement) > 100 else ''),
                        'type': 'SELECT',
                        'rows': len(data),
                        'success': True
                    })
                else:
                    # 其他语句（INSERT, UPDATE, DELETE等）
                    affected_rows = cursor.rowcount
                    total_affected_rows += affected_rows
                    execution_details.append({
                        'statement': statement[:100] + ('...' if len(statement) > 100 else ''),
                        'type': statement_upper.split()[0] if statement_upper.split() else 'UNKNOWN',
                        'affected_rows': affected_rows,
                        'success': True
                    })
                    
            except Exception as e:
                conn.rollback()
                conn.close()
                error_msg = f"执行第 {i} 条语句时出错: {str(e)}"
                Log().write_log(f"执行SQL失败: {error_msg}\n语句: {statement[:200]}", 'ERROR')
                return jsonify({
                    'error': error_msg,
                    'statement_index': i,
                    'statement': statement[:200],
                    'execution_details': execution_details
                }), 500
        
        # 提交事务
        conn.commit()
        conn.close()
        
        # 构建返回结果
        if last_select_result is not None:
            # 如果有SELECT查询，返回最后一条SELECT的结果
            Log().write_log(f"执行 {len(statements)} 条SQL语句成功，最后一条SELECT返回 {len(last_select_result)} 行", 'INFO')
            return jsonify({
                'rows': last_select_result,
                'columns': last_select_columns,
                'message': f'成功执行 {len(statements)} 条语句，最后一条SELECT返回 {len(last_select_result)} 行',
                'execution_details': execution_details,
                'total_statements': len(statements)
            })
        else:
            # 只有非SELECT语句
            Log().write_log(f"执行 {len(statements)} 条SQL语句成功，总共影响 {total_affected_rows} 行", 'INFO')
            return jsonify({
                'rows': [],
                'columns': [],
                'message': f'成功执行 {len(statements)} 条语句，总共影响 {total_affected_rows} 行',
                'execution_details': execution_details,
                'total_statements': len(statements),
                'total_affected_rows': total_affected_rows
            })
    
    except Exception as e:
        Log().write_log(f"执行SQL失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/query/saved', methods=['GET'])
def get_saved_queries():
    """获取已保存的查询"""
    try:
        # TODO: 从数据库或配置文件中读取已保存的查询
        # 暂时返回空列表
        return jsonify([])
    
    except Exception as e:
        Log().write_log(f"获取已保存查询失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/query/save', methods=['POST'])
def save_query():
    """保存查询"""
    try:
        request_data = request.json
        name = request_data.get('name', '')
        sql = request_data.get('sql', '')
        
        if not name or not sql:
            return jsonify({'error': '查询名称和SQL不能为空'}), 400
        
        # TODO: 将查询保存到数据库或配置文件
        # 暂时只返回成功
        Log().write_log(f"保存查询 {name} 成功", 'INFO')
        return jsonify({'success': True, 'message': '查询已保存'})
    
    except Exception as e:
        Log().write_log(f"保存查询失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/stats', methods=['GET'])
def get_database_stats():
    """获取数据库统计信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取表数量
        cursor.execute("""
            SELECT COUNT(*) as count FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        table_count = cursor.fetchone()['count']
        
        # 获取总记录数
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        total_records = 0
        for row in cursor.fetchall():
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM `{row['name']}`")
                total_records += cursor.fetchone()['count']
            except:
                pass
        
        conn.close()
        
        # 获取数据库大小
        db_size = get_db_size()
        
        # 获取最后修改时间
        if os.path.exists(DB_PATH):
            last_update = datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_update = '-'
        
        Log().write_log("获取数据库统计信息成功", 'INFO')
        return jsonify({
            'size': db_size,
            'tables': table_count,
            'records': total_records,
            'lastUpdate': last_update
        })
    
    except Exception as e:
        Log().write_log(f"获取数据库统计失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/info', methods=['GET'])
def get_database_info():
    """获取数据库详细信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取表数量和总行数
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_count = len(tables)
        
        total_rows = 0
        for row in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM `{row['name']}`")
                total_rows += cursor.fetchone()['count']
            except:
                pass
        
        conn.close()
        
        # 获取文件信息
        file_size = 0
        create_time = 'N/A'
        modify_time = 'N/A'
        
        if os.path.exists(DB_PATH):
            file_size = os.path.getsize(DB_PATH)
            create_time = datetime.fromtimestamp(os.path.getctime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')
            modify_time = datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')
        
        Log().write_log("获取数据库信息成功", 'INFO')
        return jsonify({
            'name': os.path.basename(DB_PATH),
            'path': DB_PATH,
            'size': file_size,
            'totalRows': total_rows,
            'createTime': create_time,
            'modifyTime': modify_time
        })
    
    except Exception as e:
        Log().write_log(f"获取数据库信息失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/backup', methods=['POST'])
def backup_database():
    """备份数据库到服务器目录"""
    try:
        if not os.path.exists(DB_PATH):
            return jsonify({'error': '数据库文件不存在'}), 404
        
        # 创建备份文件
        import shutil
        backup_filename = f'csweaponmanager_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        backup_path = os.path.join(os.path.dirname(DB_PATH), backup_filename)
        
        shutil.copy2(DB_PATH, backup_path)
        
        Log().write_log(f"数据库备份成功: {backup_path}", 'INFO')
        return jsonify({
            'message': f'数据库已备份到: {backup_filename}',
            'path': backup_path
        })
    
    except Exception as e:
        Log().write_log(f"备份数据库失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/download', methods=['GET'])
def download_database():
    """下载数据库文件"""
    try:
        if not os.path.exists(DB_PATH):
            return jsonify({'error': '数据库文件不存在'}), 404
        
        Log().write_log("开始下载数据库", 'INFO')
        return send_file(
            DB_PATH,
            as_attachment=True,
            download_name=f'csweaponmanager_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db',
            mimetype='application/x-sqlite3'
        )
    
    except Exception as e:
        Log().write_log(f"下载数据库失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/restore', methods=['POST'])
def restore_database():
    """恢复数据库"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 验证文件扩展名
        allowed_extensions = {'.db', '.sqlite', '.sqlite3'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': '不支持的文件格式'}), 400
        
        # 备份当前数据库
        backup_path = DB_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        if os.path.exists(DB_PATH):
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            Log().write_log(f"当前数据库已备份到: {backup_path}", 'INFO')
        
        # 保存上传的文件
        file.save(DB_PATH)
        
        Log().write_log("数据库恢复成功", 'INFO')
        return jsonify({'message': '数据库恢复成功'})
    
    except Exception as e:
        Log().write_log(f"恢复数据库失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/optimize', methods=['POST'])
def optimize_database():
    """优化数据库
    
    执行以下操作：
    1. ANALYZE - 收集统计信息，优化查询计划
    2. REINDEX - 重建所有索引，提高索引效率
    3. 检查数据库完整性
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        operations = []
        
        # 1. 执行ANALYZE命令 - 收集统计信息
        cursor.execute('ANALYZE')
        operations.append('✓ 已收集数据库统计信息')
        
        # 2. 重建索引 - 提高索引效率
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
        indexes = cursor.fetchall()
        for idx in indexes:
            try:
                cursor.execute(f'REINDEX `{idx[0]}`')
                operations.append(f'✓ 已重建索引: {idx[0]}')
            except Exception as e:
                operations.append(f'✗ 重建索引失败 {idx[0]}: {str(e)}')
        
        # 3. 检查数据库完整性
        cursor.execute('PRAGMA integrity_check')
        integrity_result = cursor.fetchone()[0]
        if integrity_result == 'ok':
            operations.append('✓ 数据库完整性检查通过')
        else:
            operations.append(f'⚠ 数据库完整性检查: {integrity_result}')
        
        conn.commit()
        conn.close()
        
        Log().write_log(f"数据库优化成功: {', '.join(operations)}", 'INFO')
        return jsonify({
            'message': '数据库优化成功',
            'operations': operations
        })
    
    except Exception as e:
        Log().write_log(f"优化数据库失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/vacuum', methods=['POST'])
def vacuum_database():
    """清理数据库（VACUUM）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行VACUUM命令
        cursor.execute('VACUUM')
        conn.commit()
        conn.close()
        
        Log().write_log("数据库清理成功", 'INFO')
        return jsonify({'message': '数据库清理成功'})
    
    except Exception as e:
        Log().write_log(f"清理数据库失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/truncate', methods=['POST'])
def truncate_table():
    """清空表（删除所有数据但保留表结构）"""
    try:
        data = request.get_json()
        table_name = data.get('tableName')
        
        if not table_name:
            return jsonify({'error': '缺少表名参数'}), 400
        
        # 验证表名是否存在
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': f'表 {table_name} 不存在'}), 404
        
        # 清空表数据
        cursor.execute(f'DELETE FROM "{table_name}"')
        conn.commit()
        
        # 重置自增ID（如果存在sqlite_sequence表）
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sqlite_sequence'
        """)
        if cursor.fetchone():
            cursor.execute('DELETE FROM sqlite_sequence WHERE name=?', (table_name,))
            conn.commit()
        
        conn.close()
        
        Log().write_log(f"清空表成功: {table_name}", 'INFO')
        return jsonify({'message': f'表 {table_name} 已清空'})
    
    except Exception as e:
        Log().write_log(f"清空表失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/drop', methods=['POST'])
def drop_table():
    """删除表（永久删除表及其所有数据）"""
    try:
        data = request.get_json()
        table_name = data.get('tableName')
        
        if not table_name:
            return jsonify({'error': '缺少表名参数'}), 400
        
        # 验证表名是否存在
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': f'表 {table_name} 不存在'}), 404
        
        # 删除表
        cursor.execute(f'DROP TABLE "{table_name}"')
        conn.commit()
        conn.close()
        
        Log().write_log(f"删除表成功: {table_name}", 'INFO')
        return jsonify({'message': f'表 {table_name} 已删除'})
    
    except Exception as e:
        Log().write_log(f"删除表失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500

