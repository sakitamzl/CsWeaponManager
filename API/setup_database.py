#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于首次运行时创建数据库和表结构
支持完整的数据库初始化流程
"""

import pymysql
import configparser
import os
import sys
import io


# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class DatabaseSetup:
    """数据库初始化类"""
    
    def __init__(self, log_enabled=True):
        self.config = self._load_config()
        self.log_enabled = log_enabled
        self.db_name = 'cs_weapon_manager'  # 固定数据库名称
        
    def _load_config(self):
        """加载配置文件"""
        try:
            config = configparser.ConfigParser()
            config.read('conf.ini', encoding='utf-8')
            return config
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            sys.exit(1)
            
    def _get_db_config(self):
        """获取数据库配置"""
        try:
            return {
                'host': self.config.get('database', 'host'),
                'port': int(self.config.get('database', 'port')),
                'user': self.config.get('database', 'user'),
                'password': self.config.get('database', 'password'),
                'database_name': self.config.get('database', 'database_name'),
            }
        except Exception as e:
            print(f"读取数据库配置失败: {e}")
            sys.exit(1)
    
    def _log(self, message, level='info'):
        """简单日志记录"""
        if self.log_enabled:
            timestamp = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {level.upper()}: {message}")
    
    def _connect_server(self):
        """连接MySQL服务器（不指定数据库）"""
        db_config = self._get_db_config()
        try:
            connection = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                charset='utf8mb4',
                autocommit=False
            )
            return connection
        except Exception as e:
            self._log(f"连接MySQL服务器失败: {e}", 'error')
            return None
    
    def _connect_database(self):
        """连接指定的数据库"""
        db_config = self._get_db_config()
        try:
            connection = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database_name'],
                charset='utf8mb4',
                autocommit=False
            )
            return connection
        except Exception as e:
            self._log(f"连接数据库失败: {e}", 'error')
            return None
    
    def check_server_connection(self):
        """检查MySQL服务器连接"""
        print("检查MySQL服务器连接...")
        connection = self._connect_server()
        if connection:
            connection.close()
            print("✓ MySQL服务器连接正常")
            return True
        else:
            print("✗ MySQL服务器连接失败")
            return False
    
    def database_exists(self):
        """检查数据库是否存在"""
        connection = self._connect_server()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES LIKE %s", (self.db_name,))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result is not None
            
        except Exception as e:
            self._log(f"检查数据库存在性失败: {e}", 'error')
            return False
    
    def create_database(self):
        """创建数据库"""
        print(f"创建数据库 '{self.db_name}'...")
        connection = self._connect_server()
        if not connection:
            return False
            
        try:
            cursor = connection.cursor()
            
            # 创建数据库
            create_db_sql = f"""
            CREATE DATABASE IF NOT EXISTS `{self.db_name}` 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_0900_ai_ci
            """
            
            cursor.execute(create_db_sql)
            connection.commit()
            cursor.close()
            connection.close()
            
            print(f"✓ 数据库 '{self.db_name}' 创建成功")
            self._log(f"数据库 '{self.db_name}' 创建成功")
            return True
            
        except Exception as e:
            print(f"✗ 创建数据库失败: {e}")
            self._log(f"创建数据库失败: {e}", 'error')
            return False
    
    def _read_sql_file(self, file_path='DB.sql'):
        """读取SQL文件内容"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL文件不存在: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"读取SQL文件失败: {e}")
    
    def _parse_sql_statements(self, sql_content):
        """解析SQL语句"""
        # 移除注释和空行
        lines = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('#'):
                lines.append(line)
        
        # 重新组合并按分号分割
        full_sql = ' '.join(lines)
        statements = []
        
        # SQL语句分割（处理CREATE TABLE等复杂语句）
        current_statement = ""
        paren_count = 0
        in_string = False
        string_char = None
        
        i = 0
        while i < len(full_sql):
            char = full_sql[i]
            
            # 处理字符串
            if char in ('"', "'", '`') and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            
            # 在字符串外才计算括号
            if not in_string:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == ';' and paren_count == 0:
                    statement = current_statement.strip()
                    if statement:
                        statements.append(statement)
                    current_statement = ""
                    i += 1
                    continue
            
            current_statement += char
            i += 1
        
        # 添加最后一个语句（如果存在）
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return [stmt for stmt in statements if stmt and len(stmt.strip()) > 0]
    
    def create_tables(self):
        """创建表结构"""
        print("创建数据库表结构...")
        
        try:
            # 读取SQL文件
            sql_content = self._read_sql_file()
            
            # 连接数据库
            connection = self._connect_database()
            if not connection:
                return False
            
            # 解析SQL语句
            statements = self._parse_sql_statements(sql_content)
            
            if not statements:
                print("没有找到有效的SQL语句")
                return False
            
            cursor = connection.cursor()
            success_count = 0
            skip_count = 0
            
            for i, statement in enumerate(statements):
                try:
                    cursor.execute(statement)
                    connection.commit()
                    success_count += 1
                    
                    # 提取表名用于显示
                    if 'CREATE TABLE' in statement.upper():
                        # 尝试提取表名
                        parts = statement.split('`')
                        if len(parts) >= 2:
                            table_name = parts[1]
                        else:
                            # 备用方法
                            table_part = statement.upper().split('CREATE TABLE')[1].split('(')[0].strip()
                            table_name = table_part.replace('`', '').strip()
                        
                        print(f"  ✓ 表 '{table_name}' 创建成功")
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    if "already exists" in error_msg or "table exists" in error_msg:
                        skip_count += 1
                        print(f"  - 表已存在，跳过")
                    else:
                        print(f"  ✗ 执行SQL语句失败: {e}")
                        self._log(f"执行SQL语句失败: {statement[:100]}... 错误: {e}", 'error')
            
            cursor.close()
            connection.close()
            
            print(f"表结构处理完成：成功 {success_count}，跳过 {skip_count}")
            self._log(f"成功执行 {success_count} 条SQL语句")
            return success_count > 0 or skip_count > 0
                
        except FileNotFoundError as e:
            print(f"✗ 错误: {e}")
            self._log(str(e), 'error')
            return False
        except Exception as e:
            print(f"✗ 创建表结构失败: {e}")
            self._log(f"创建表结构失败: {e}", 'error')
            return False
    
    def test_database_connection(self):
        """测试数据库连接和基本功能"""
        print("测试数据库连接...")
        
        try:
            connection = self._connect_database()
            if not connection:
                return False
            
            cursor = connection.cursor()
            
            # 测试基本查询
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            # 测试表列表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            if result and result[0] == 1:
                print("✓ 数据库连接测试成功")
                if tables:
                    print(f"✓ 数据库包含 {len(tables)} 个表")
                self._log("数据库连接测试成功")
                return True
            else:
                print("✗ 数据库连接测试失败")
                return False
                
        except Exception as e:
            print(f"✗ 数据库连接测试失败: {e}")
            self._log(f"数据库连接测试失败: {e}", 'error')
            return False
    
    def show_database_info(self):
        """显示数据库信息"""
        try:
            connection = self._connect_database()
            if not connection:
                return
            
            cursor = connection.cursor()
            
            # 获取表信息
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"\n数据库 '{self.db_name}' 信息:")
            print(f"  - 表数量: {len(tables)}")
            
            if tables:
                print("  - 表列表:")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    count = cursor.fetchone()[0]
                    print(f"    * {table_name} ({count} 条记录)")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"获取数据库信息失败: {e}")
    
    def run_full_setup(self):
        """执行完整的数据库初始化流程"""
        print("=" * 50)
        print("数据库初始化开始")
        print("=" * 50)
        
        try:
            # 检查必需文件
            if not os.path.exists('conf.ini'):
                print("✗ 错误: 配置文件 conf.ini 不存在")
                return False
                
            if not os.path.exists('DB.sql'):
                print("✗ 错误: SQL文件 DB.sql 不存在")
                return False
            
            # 1. 检查MySQL服务器连接
            if not self.check_server_connection():
                print("请检查MySQL服务器是否运行，以及配置文件中的连接参数")
                return False
            
            # 2. 检查数据库是否存在
            print(f"\n检查数据库 '{self.db_name}' 是否存在...")
            if self.database_exists():
                print(f"✓ 数据库 '{self.db_name}' 已存在")
            else:
                print(f"数据库 '{self.db_name}' 不存在，开始创建...")
                if not self.create_database():
                    print("数据库创建失败，初始化终止")
                    return False
            
            # 3. 创建表结构
            print(f"\n初始化表结构...")
            if not self.create_tables():
                print("表结构创建失败，初始化终止")
                return False
            
            # 4. 测试数据库连接和功能
            print(f"\n最终测试...")
            if not self.test_database_connection():
                print("数据库连接测试失败")
                return False
            
            # 5. 显示数据库信息
            self.show_database_info()
            
            print("\n" + "=" * 50)
            print("数据库初始化成功完成!")
            print("=" * 50)
            return True
            
        except KeyboardInterrupt:
            print("\n\n用户中断操作")
            return False
        except Exception as e:
            print(f"\n初始化过程中发生错误: {e}")
            self._log(f"数据库初始化失败: {e}", 'error')
            return False


def main():
    """主函数"""
    print("CS武器管理系统 - 数据库初始化工具")
    print()
    
    try:
        # 创建初始化器
        setup = DatabaseSetup()
        
        # 运行完整初始化流程
        if setup.run_full_setup():
            print("\n数据库初始化成功！系统可以正常使用。")
            sys.exit(0)
        else:
            print("\n数据库初始化失败！请检查错误信息。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()