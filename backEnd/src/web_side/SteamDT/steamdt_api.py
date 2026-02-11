# -*- coding: utf-8 -*-
"""
SteamDT API路由
"""

from flask import Blueprint, request, jsonify
import requests
from lxml import etree

steamdtApiV1 = Blueprint('steamdtApiV1', __name__)


@steamdtApiV1.route('/api/steamdt/config', methods=['GET'])
def get_steamdt_config():
    """
    获取SteamDT配置

    注意：SteamDT API不需要token认证，此接口仅为保持架构一致性
    """
    try:
        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'needAuth': False,
                'message': 'SteamDT API不需要认证'
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'code': 500,
            'message': f'获取配置失败: {str(e)}'
        }), 500


@steamdtApiV1.route('/api/steamdt/homepage-data', methods=['GET'])
def get_homepage_data():
    """
    获取SteamDT首页饰品成交额数据
    通过解析HTML页面获取
    """
    try:
        # 请求首页
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        response = requests.get('https://steamdt.com/', headers=headers, timeout=10)
        response.raise_for_status()

        # 解析HTML
        html = etree.HTML(response.text)

        # 提取饰品成交额数据
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[1]/div[2]/span/span[1]
        turnover_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[1]/div[2]/span/span[1]')
        turnover = None
        if turnover_element and len(turnover_element) > 0:
            turnover = turnover_element[0].text.strip() if turnover_element[0].text else None

        # 提取昨日数据
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[1]/div[3]/span[2]
        yesterday_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[1]/div[3]/span[2]')
        yesterday = None
        if yesterday_element and len(yesterday_element) > 0:
            yesterday = yesterday_element[0].text.strip() if yesterday_element[0].text else None

        # 提取环比数据（成交额）
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[1]/div[1]/div/span[2]/span
        ratio_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[1]/div[1]/div/span[2]/span')
        ratio = None
        if ratio_element and len(ratio_element) > 0:
            ratio = ratio_element[0].text.strip() if ratio_element[0].text else None

        # 提取成交量环比
        # XPath: //*[@id="__nuxt"]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/span/span
        volume_ratio_element = html.xpath('//*[@id="__nuxt"]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[1]/span/span')
        volume_ratio = None
        if volume_ratio_element and len(volume_ratio_element) > 0:
            volume_ratio = volume_ratio_element[0].text.strip() if volume_ratio_element[0].text else None

        # 提取成交量
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/span/span[1]
        volume_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[2]/span/span[1]')
        volume = None
        if volume_element and len(volume_element) > 0:
            volume = volume_element[0].text.strip() if volume_element[0].text else None

        # 提取昨日成交量
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[3]/span/text()
        yesterday_volume_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[1]/div/div[2]/div[3]/span/text()')
        yesterday_volume = None
        if yesterday_volume_element and len(yesterday_volume_element) > 0:
            yesterday_volume = yesterday_volume_element[0].strip() if yesterday_volume_element[0] else None

        # 提取饰品新增额
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[1]/div[2]/span/span[1]
        add_valuation_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[1]/div[2]/span/span[1]')
        add_valuation = None
        if add_valuation_element and len(add_valuation_element) > 0:
            add_valuation = add_valuation_element[0].text.strip() if add_valuation_element[0].text else None

        # 提取新增额昨日数据
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[1]/div[3]/span[2]/span[1]
        yesterday_add_valuation_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[1]/div[3]/span[2]/span[1]')
        yesterday_add_valuation = None
        if yesterday_add_valuation_element and len(yesterday_add_valuation_element) > 0:
            yesterday_add_valuation = yesterday_add_valuation_element[0].text.strip() if yesterday_add_valuation_element[0].text else None

        # 提取新增额环比
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[1]/div[1]/div/span[2]/span
        add_valuation_ratio_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[1]/div[1]/div/span[2]/span')
        add_valuation_ratio = None
        if add_valuation_ratio_element and len(add_valuation_ratio_element) > 0:
            add_valuation_ratio = add_valuation_ratio_element[0].text.strip() if add_valuation_ratio_element[0].text else None

        # 提取饰品新增量
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[2]/div[2]/span/span[1]
        add_num_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[2]/div[2]/span/span[1]')
        add_num = None
        if add_num_element and len(add_num_element) > 0:
            add_num = add_num_element[0].text.strip() if add_num_element[0].text else None

        # 提取新增量昨日数据
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[2]/div[3]/span[2]/span[1]
        yesterday_add_num_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[2]/div[3]/span[2]/span[1]')
        yesterday_add_num = None
        if yesterday_add_num_element and len(yesterday_add_num_element) > 0:
            yesterday_add_num = yesterday_add_num_element[0].text.strip() if yesterday_add_num_element[0].text else None

        # 提取新增量环比
        # XPath: /html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[2]/div[1]/span/span
        add_num_ratio_element = html.xpath('/html/body/div[2]/div/div[3]/div/div/div[1]/div[2]/div[3]/div/div[2]/div[1]/span/span')
        add_num_ratio = None
        if add_num_ratio_element and len(add_num_ratio_element) > 0:
            add_num_ratio = add_num_ratio_element[0].text.strip() if add_num_ratio_element[0].text else None

        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'turnover': turnover,                          # 饰品成交额
                'yesterday': yesterday,                        # 昨日成交额
                'ratio': ratio,                                # 成交额环比
                'volume': volume,                              # 成交量
                'volume_ratio': volume_ratio,                  # 成交量环比
                'yesterday_volume': yesterday_volume,          # 昨日成交量
                'add_valuation': add_valuation,                # 饰品新增额
                'yesterday_add_valuation': yesterday_add_valuation,  # 昨日新增额
                'add_valuation_ratio': add_valuation_ratio,    # 新增额环比
                'add_num': add_num,                            # 饰品新增量
                'yesterday_add_num': yesterday_add_num,        # 昨日新增量
                'add_num_ratio': add_num_ratio                 # 新增量环比
            }
        }), 200

    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'code': 504,
            'message': '请求超时'
        }), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'code': 500,
            'message': f'网络请求失败: {str(e)}'
        }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500
