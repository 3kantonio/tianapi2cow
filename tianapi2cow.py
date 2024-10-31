import os
import json
import requests
from common.log import logger
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from plugins import *
import config

@plugins.register(name="Tianapi2cow",
                  desc="获取AI、科技和科学探索相关的最新资讯",
                  version="alpha 1.0",
                  author="Antonio",
                  desire_priority=100)
class Tianapi2cow(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] initialized")

    def get_help_text(self, **kwargs):
        return "输入“人工智能|行业资讯｜科学探索”等关键字获取最新的相关资讯。"

    def on_handle_context(self, e_context):
        if e_context['context'].type == ContextType.TEXT:
            content = e_context["context"].content.strip()
            if content.startswith("人工智能"):
                logger.info(f"[{__class__.__name__}] 收到AI简讯请求: {content}")
                self.fetch_ai_news(e_context)
            elif content.startswith("科技简讯"):
                logger.info(f"[{__class__.__name__}] 收到科技简讯请求: {content}")
                self.fetch_tech_news(e_context)
            elif content.startswith("科学探索"):
                logger.info(f"[{__class__.__name__}] 收到科学探索请求: {content}")
                self.fetch_science_news(e_context)

    def fetch_ai_news(self, e_context):
        self.fetch_news(e_context, "ai", "最新AI资讯如下：")

    def fetch_tech_news(self, e_context):
        self.fetch_news(e_context, "it", "最新科技新闻如下：")

    def fetch_science_news(self, e_context):
        self.fetch_news(e_context, "science", "最新科学探索资讯如下：")

    def fetch_news(self, e_context, category, header_text):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if not os.path.exists(config_path):
            logger.error(f"请先配置{config_path}文件")
            return

        with open(config_path, 'r') as file:
            api_key = json.load(file).get('TIAN_API_KEY', '')
        
        if not api_key:
            logger.error("API key is missing in config.json")
            return

        url = f"https://apis.tianapi.com/{category}/index?key={api_key}&num=10"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            # 检查API返回的内容
            if data.get('code') == 200:
			   current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if 'result' in data and 'newslist' in data['result']:
                    self.construct_reply(data['result']['newslist'], e_context, header_text)
                else:
                    logger.error(f"API返回格式不正确: {data}")
                    self.send_error_reply(e_context, "获取资讯失败，返回数据格式不正确。")
            else:
                logger.error(f"API error: {data.get('msg', '未知错误')}")
                self.send_error_reply(e_context, f"获取资讯失败: {data.get('msg', '未知错误')}。")
        except Exception as e:
            logger.error(f"接口抛出异常: {e}")
            self.send_error_reply(e_context, "请求失败，请稍后再试。")

    def construct_reply(self, newslist, e_context, header_text):
        reply = Reply()
        reply.type = ReplyType.TEXT
        reply.content = f"📢 {header_text}\n"
		reply.content = f"📢 {user_input}最新资讯如下：{current_datetime}\n"
        
        for i, news in enumerate(news_list, start=1):
            output_text += (
                f"\n{i}. {news.get('ctime')} - {news.get('title')} - {news.get('description')}\n"
            )

        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS

    def send_error_reply(self, e_context, message):
        reply = Reply()
        reply.type = ReplyType.TEXT
        reply.content = message
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS
