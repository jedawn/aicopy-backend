from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AiCopy API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = "aicopy.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            input TEXT,
            output TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_request(log_type: str, input_data: dict, output_data: dict):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO logs (type, input, output) VALUES (?, ?, ?)',
            (log_type, json.dumps(input_data), json.dumps(output_data))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to log: {e}")

init_db()

class TitleRequest(BaseModel):
    topic: str
    industry: str
    style: str

class ScriptRequest(BaseModel):
    topic: str
    type: str
    duration: str

class ProductRequest(BaseModel):
    name: str
    features: str

def generate_title_mock(topic: str, industry: str, style: str) -> List[str]:
    titles = [
        f"{style}！{topic}这样做，效果惊人",
        f"被问爆的{topic}秘诀，{industry}人都在用",
        f"{topic}天花板！这才是{industry}正确打开方式",
        f"终于找到{topic}的正确姿势，{style}来袭",
        f"{topic}干货分享，{industry}人必看",
        f"全网都在找的{topic}方法，{style}版来了",
        f"{topic}居然这么简单？{industry}小白也能上手",
        f"揭秘{topic}背后的秘密，{style}分享",
        f"{topic}必看！{industry}达人私藏技巧",
        f"从0到1学会{topic}，{style}教程来啦",
        f"{topic}太香了！{industry}人都在学",
        f"亲测有效！{topic}的正确打开方式",
        f"{topic}干货｜{industry}人必收藏",
        f"手把手教你{topic}，{style}分享",
        f"{topic}保姆级教程，{industry}小白速进",
        f"{topic}黑科技！{style}带你飞",
        f"{topic}避坑指南，{industry}人必看",
        f"震惊！{topic}居然可以这样",
        f"{topic}干货满满，{style}不容错过",
        f"{topic}终极指南，{industry}人手一份"
    ]
    return titles

def generate_script_mock(topic: str, type: str, duration: str) -> str:
    return f"""【开场Hook】
家人们！今天给大家分享一个超级干货——{topic}！相信很多朋友都有这方面的困扰，今天我就来帮你们彻底解决！

【正文内容】
首先，我们要明确一点，{topic}其实并不难，关键在于方法。今天我给大家整理了几个核心要点：

第一点，就是要找准方向。很多人一开始就走错路，导致事倍功半。我建议大家先明确自己的目标，这样才能事半功倍。

第二点，工具很重要。好的工具能让你事半功倍。我个人常用的几个工具分享给大家，你们可以试试看。

第三点，坚持！{topic}不是一蹴而就的，需要长期坚持。但是只要方法正确，你会发现进步其实很快。

【结尾引导】
好了，今天的分享就到这里！如果觉得对你有帮助，记得点赞关注哦！有什么问题欢迎在评论区留言，我会一一回复的！"""

def generate_product_mock(name: str, features: str) -> Dict:
    return {
        "selling_points": [
            f"{name}，品质之选",
            f"核心优势：{features}",
            f"{name}，让生活更美好",
            f"匠心打造，细节满满",
            f"{name}，值得拥有"
        ],
        "ad_copy": f"🔥 {name}重磅来袭！\n\n{features}\n\n无论是品质还是体验，都能满足你的期待！\n\n现在下单，享受专属优惠！\n\n#好物推荐 #品质生活",
        "seo_description": f"{name}，{features}。高品质{name}，让您的生活更美好。立即选购，享受优惠！"
    }

llm_service = None
try:
    from services.llm_service import LLMService
    llm_service = LLMService()
    print("LLM Service initialized with Tongyi Qwen")
except Exception as e:
    print(f"LLM Service not initialized: {e}")
    print("Using mock data instead")

@app.post("/api/title")
async def generate_title(request: TitleRequest):
    try:
        if llm_service:
            titles = llm_service.generate_titles(request.topic, request.industry, request.style)
        else:
            titles = generate_title_mock(request.topic, request.industry, request.style)
        result = {"success": True, "data": titles}
        log_request("title", request.dict(), result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/script")
async def generate_script(request: ScriptRequest):
    try:
        if llm_service:
            script = llm_service.generate_script(request.topic, request.type, request.duration)
        else:
            script = generate_script_mock(request.topic, request.type, request.duration)
        result = {"success": True, "data": script}
        log_request("script", request.dict(), result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/product")
async def generate_product(request: ProductRequest):
    try:
        if llm_service:
            product = llm_service.generate_product_copy(request.name, request.features)
        else:
            product = generate_product_mock(request.name, request.features)
        result = {"success": True, "data": product}
        log_request("product", request.dict(), result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AiCopy API is running", "llm_enabled": llm_service is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)