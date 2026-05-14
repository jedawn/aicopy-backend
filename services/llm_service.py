from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import LLMChain
from typing import List, Dict
import os
import json

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key or self.api_key == "your-dashscope-api-key":
            raise ValueError("DASHSCOPE_API_KEY environment variable not set")
        
        self.llm = ChatTongyi(
            dashscope_api_key=self.api_key,
            model_name="qwen-turbo",
            temperature=0.7,
            max_tokens=4096
        )
    
    def generate_titles(self, topic: str, industry: str, style: str) -> List[str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的短视频标题生成器。请根据用户提供的信息生成吸引人的短视频标题。"),
            ("human", """请根据以下信息生成20个吸引人的短视频标题：

主题：{topic}
行业：{industry}
风格：{style}

要求：
1. 每个标题不超过20字
2. 包含话题关键词
3. 使用吸引眼球的词汇
4. 标题要简洁有力
5. 输出格式为JSON数组，只包含标题字符串，不要其他内容

示例输出：
["标题1", "标题2", "标题3"]""")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(topic=topic, industry=industry, style=style)
        
        try:
            return json.loads(result)
        except:
            titles = [t.strip() for t in result.split("\n") if t.strip() and not t.startswith("#")]
            return titles[:20]
    
    def generate_script(self, topic: str, type: str, duration: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的短视频脚本创作专家。请根据用户提供的信息创作完整的短视频脚本。"),
            ("human", """请根据以下信息创作一个完整的短视频脚本：

主题：{topic}
类型：{type}
时长：{duration}

脚本结构要求：
1. 开场Hook（吸引人的开头）
2. 正文内容（详细讲解）
3. 结尾引导（点赞、关注、评论）

要求：
- 语言口语化，符合短视频风格
- 内容充实，有干货
- 结构清晰，有逻辑
- 结尾要有引导互动

输出格式：
直接输出脚本内容，不要其他格式。""")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(topic=topic, type=type, duration=duration)
    
    def generate_product_copy(self, name: str, features: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的电商文案撰写专家。请根据用户提供的产品信息生成营销文案。"),
            ("human", """请根据以下产品信息生成营销文案：

产品名称：{name}
产品特点：{features}

请生成：
1. 5个产品卖点（selling_points）
2. 一条完整的电商广告文案（ad_copy）
3. 一条SEO描述（seo_description）

输出格式为JSON：
{{
    "selling_points": ["卖点1", "卖点2", "卖点3", "卖点4", "卖点5"],
    "ad_copy": "广告文案内容",
    "seo_description": "SEO描述内容"
}}

要求：
- 卖点简洁有力，突出产品优势
- 广告文案要有吸引力，能促进转化
- SEO描述包含关键词，适合搜索引擎优化""")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(name=name, features=features)
        
        try:
            return json.loads(result)
        except:
            return {
                "selling_points": [f"{name}品质之选", features, f"{name}让生活更美好", "匠心打造", "值得拥有"],
                "ad_copy": f"🔥 {name}重磅来袭！\n\n{features}\n\n立即选购！",
                "seo_description": f"{name}，{features}。高品质选择！"
            }
