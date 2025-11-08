"""
数据库管理API
提供类似Navicat的数据库管理功能
"""
from flask import Blueprint, request, jsonify, send_file
from src.log import Log
import sqlite3
import os
import csv
import json
import io
from datetime import datetime

database_manager_bp = Blueprint('database_manager', __name__, url_prefix='/api/database')

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'csweaponmanager.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db_size():
    """获取数据库文件大小"""
    if os.path.exists(DB_PATH):
        size_bytes = os.path.getsize(DB_PATH)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    return "0 B"


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
            # 获取表的行数
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            
            tables.append({
                'name': table_name,
                'rowCount': count
            })
        
        conn.close()
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
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 获取列名
        columns = [{'name': description[0]} for description in cursor.description]
        
        # 转换为字典列表
        data = []
        for row in rows:
            data.append(dict(row))
        
        conn.close()
        
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
        cursor.execute(f"PRAGMA table_info({table_name})")
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
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        row_count = cursor.fetchone()['count']
        
        conn.close()
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建INSERT语句
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.keys()])
        values = list(data.values())
        
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        
        conn.commit()
        conn.close()
        
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
        index = request_data.get('index', -1)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取主键
        cursor.execute(f"PRAGMA table_info({table_name})")
        primary_key = None
        for row in cursor.fetchall():
            if row['pk'] == 1:
                primary_key = row['name']
                break
        
        if not primary_key:
            return jsonify({'error': '表没有主键，无法更新'}), 400
        
        # 构建UPDATE语句
        set_clause = ', '.join([f"{k} = ?" for k in data.keys() if k != primary_key])
        values = [v for k, v in data.items() if k != primary_key]
        values.append(data[primary_key])
        
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"
        cursor.execute(sql, values)
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '更新成功'})
    
    except Exception as e:
        Log().write_log(f"更新数据失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/table/<table_name>/row', methods=['DELETE'])
def delete_row(table_name):
    """删除数据行"""
    try:
        request_data = request.json
        row = request_data.get('row', {})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取主键
        cursor.execute(f"PRAGMA table_info({table_name})")
        primary_key = None
        for r in cursor.fetchall():
            if r['pk'] == 1:
                primary_key = r['name']
                break
        
        if not primary_key:
            return jsonify({'error': '表没有主键，无法删除'}), 400
        
        # 删除数据
        sql = f"DELETE FROM {table_name} WHERE {primary_key} = ?"
        cursor.execute(sql, [row[primary_key]])
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '删除成功'})
    
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
        cursor.execute(f"PRAGMA table_info({table_name})")
        primary_key = None
        for r in cursor.fetchall():
            if r['pk'] == 1:
                primary_key = r['name']
                break
        
        if not primary_key:
            return jsonify({'error': '表没有主键，无法删除'}), 400
        
        # 批量删除
        for row in rows:
            sql = f"DELETE FROM {table_name} WHERE {primary_key} = ?"
            cursor.execute(sql, [row[primary_key]])
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'成功删除 {len(rows)} 条数据'})
    
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
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        conn.close()
        
        if export_format == 'csv':
            # 导出为CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(columns)
            for row in rows:
                writer.writerow(row)
            
            output.seek(0)
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
                data.append(dict(row))
            
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
    """执行SQL查询"""
    try:
        request_data = request.json
        sql = request_data.get('sql', '').strip()
        
        if not sql:
            return jsonify({'error': 'SQL语句不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行查询
        cursor.execute(sql)
        
        # 如果是SELECT查询，返回结果
        if sql.upper().startswith('SELECT'):
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            data = []
            for row in rows:
                data.append(dict(row))
            
            conn.close()
            
            return jsonify({
                'rows': data,
                'columns': columns
            })
        else:
            # 其他语句（INSERT, UPDATE, DELETE等）
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            
            return jsonify({
                'rows': [],
                'columns': [],
                'message': f'执行成功，影响 {affected_rows} 行'
            })
    
    except Exception as e:
        Log().write_log(f"执行SQL失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500


@database_manager_bp.route('/query/saved', methods=['GET'])
def get_saved_queries():
    """获取已保存的查询"""
    try:
        # 这里可以从数据库或文件中读取已保存的查询
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
        
        # 这里可以将查询保存到数据库或文件
        # 暂时只返回成功
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
            cursor.execute(f"SELECT COUNT(*) as count FROM {row['name']}")
            total_records += cursor.fetchone()['count']
        
        conn.close()
        
        # 获取数据库大小
        db_size = get_db_size()
        
        # 获取最后修改时间
        if os.path.exists(DB_PATH):
            last_update = datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_update = '-'
        
        return jsonify({
            'size': db_size,
            'tables': table_count,
            'records': total_records,
            'lastUpdate': last_update
        })
    
    except Exception as e:
        Log().write_log(f"获取数据库统计失败: {str(e)}", 'ERROR')
        return jsonify({'error': str(e)}), 500

