#2025-11-27
v1.2.5 --   爬取改名中的 steam市场类型添加搜素参数
#2025-11-28 
v1.2.6 --   1、auto-manager自动化管理页面添加 启动全部 停止全部按钮
            2、修改csfloat的订单查询状态限制
            3、添加使用yyyp的URL进行ICON的下载 脱离在线图片库的依赖

#2025-11-29
v1.2.7 --   1、表 buy sell  steam_stockComponents  steam_inventory steam_buy steam_sell 新增字段 steam_hash_name
            2、steam库存表添加 详细信息的获取
            3、修改steam库存、sell、buy页面的显示样式 
            4、修改yyyp 获取商品详情的时候 添加获取贴纸信息 挂件信息
            5、更新执行语句 
            DELETE FROM "main"."sell" WHERE "from" = 'yyyp';
            DELETE FROM "main"."buy" WHERE "from" = 'yyyp';
            DELETE FROM yyyp_sell;
            DELETE FROM yyyp_buy;

#2025-11-30
v1.2.8 --   1、添加sell buy列表的贴纸、挂件、改名的显示     
            2、完成csfloat 饰品 印花 挂件获取

            DELETE FROM "main"."sell" WHERE "from" = 'buff';
            DELETE FROM "main"."buy" WHERE "from" = 'buff';
            DELETE FROM buff_sell;
            DELETE FROM buff_buy;
            
            DELETE FROM "main"."sell" WHERE "from" = 'csfloat';
            DELETE FROM "main"."buy" WHERE "from" = 'csfloat';
            DELETE FROM csfloat_sell;
            DELETE FROM csfloat_buy;