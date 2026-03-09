# -*- coding: utf-8 -*-
"""
use_spider/csqaq 聚合
"""
from flask import Blueprint
from .stock_components.API import csqaq_stock_components_blueprint

csqaq_spider_blueprint = Blueprint("csqaq_spider", __name__)
csqaq_spider_blueprint.register_blueprint(csqaq_stock_components_blueprint)
