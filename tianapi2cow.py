import requests
import json
from datetime import datetime
import plugins
from common.log import logger
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from plugins import *
import config


 @plugins.register(name="Tianapi2cow",
                  desc="获取天聚数行的API相关信息资讯",
                  version="alpha 1.0 ",
                  author="Antonio",
                  desire_priority=100)

class TianapiFetcher(Plugin):
   	def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] initialized")
		
	def get_help_text(self, **kwargs):
        return "输入“人工智能|行业资讯｜科技新闻｜科学探索｜互联网资讯”等关键字获取最新的相关资讯。"
		
	def on_handle_context(self, e_context):
        if e_context['context'].type == ContextType.TEXT:
            content = e_context["context"].content.strip()
            # if content.startswith("人工智能"):
			if content == "人工智能"
                logger.info(f"[{__class__.__name__}] 收到消息: {content}")
                self.fetch_and_parse_data(e_context)
				

    def __init__(self, config_path="config.json"):
        self.api_key = self.load_api_key(config_path)

    def load_api_key(self, filename="config.json"):
        try:
            with open(filename, 'r') as file:
                config = json.load(file)
                return config.get("api_key")
        except FileNotFoundError:
            raise FileNotFoundError("配置文件未找到，请确保 config.json 存在。")
        except json.JSONDecodeError:
            raise ValueError("配置文件格式不正确，请检查 JSON 格式。")

    def get_api_url(self, category):
        url_map = {
            "行业资讯": f"https://apis.tianapi.com/it/index?key={self.api_key}&num=10",
            "科技新闻": f"https://apis.tianapi.com/keji/index?key={self.api_key}&num=10",
            "人工智能": f"https://apis.tianapi.com/ai/index?key={self.api_key}&num=10",
            "科学探索": f"https://apis.tianapi.com/sicprobe/index?key={self.api_key}&num=10",
            "互联网资讯": f"https://apis.tianapi.com/internet/index?key={self.api_key}&num=10"
        }

        if category not in url_map:
            raise ValueError("无效的输入，请选择有效的资讯分类：行业资讯、科技新闻、人工智能、科学探索、互联网资讯。")

        return url_map[category]

    def fetch_and_parse_data(self, api_url):
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API 请求失败: {e}")

        try:
            data = response.json()
        except ValueError:
            raise ValueError("响应不是有效的 JSON 格式。")

        if data.get("code") != 200:
            raise RuntimeError(f"API 请求返回错误信息: {data.get('msg', '未知错误')}")
        
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = data.get("result", {})
        curpage = result.get("curpage", 1)
        allnum = result.get("allnum", 0)
        news_list = result.get("newslist", [])
        
        return output_text

    def get_news_by_category(self, category):
        try:
            api_url = self.get_api_url(category)
            return self.fetch_and_parse_data(api_url)
        except Exception as e:
            return str(e)
	
	def construct_reply(self, newslist, e_context):
        reply = Reply()
        reply.type = ReplyType.TEXT
        
        # 构造回复内容
        reply.content = f"📢 {user_input}最新资讯如下：{current_datetime}\n"
        for i, news in enumerate(news_list, start=1):
            output_text += (
                f"\n{i}. {news.get('ctime')} - {news.get('title')} - {news.get('description')}\n"
            )
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS

if __name__ == "__main__":
    fetcher = TianapiFetcher()
    user_input = input("请输入要查询的内容（行业资讯/科技新闻/人工智能/科学探索/互联网资讯）：").strip()
    print(fetcher.get_news_by_category(user_input))
