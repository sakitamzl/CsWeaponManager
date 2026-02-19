#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 AES API V2 路由
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Spider'))

from src.API import src_blueprint

def print_routes(blueprint, prefix=''):
    """递归打印蓝图的所有路由"""

    # 打印当前蓝图的路由
    if hasattr(blueprint, '_blueprints'):
        for bp_name, bp in blueprint._blueprints.items():
            print(f"\n=== Blueprint: {bp_name} ===")
            print_routes(bp, prefix)

    # 打印路由规则
    if hasattr(blueprint, 'deferred_functions'):
        print(f"\nRoutes in {blueprint.name}:")
        for func in blueprint.deferred_functions:
            print(f"  {func}")

if __name__ == '__main__':
    print("测试 AES API V2 路由结构\n")
    print("=" * 60)

    # 打印 src_blueprint 的结构
    print(f"\n顶层 Blueprint: {src_blueprint.name}")
    print(f"URL 前缀: /spiderApiV2")

    # 检查是否有子蓝图
    if hasattr(src_blueprint, '_blueprints'):
        print(f"\n子蓝图数量: {len(src_blueprint._blueprints)}")
        for bp_name in src_blueprint._blueprints:
            print(f"  - {bp_name}")

    print("\n" + "=" * 60)
    print("\n预期的 API 路径:")
    print("  - POST /spiderApiV2/youping/units/settings/dev_tools/aesDecrypt")
    print("  - GET  /spiderApiV2/youping/units/settings/dev_tools/aesCheckLicense")
    print("  - GET  /spiderApiV2/youping/units/settings/dev_tools/aesHealth")
    print("\n" + "=" * 60)
