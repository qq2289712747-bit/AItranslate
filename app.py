from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_FILE = BASE_DIR / "templates" / "index.html"

app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Cloudflare Tunnel connected successfully!"}

app.mount("/static", StaticFiles(directory="static"), name="static")


def translate_to_japanese(text):
    prompt = f"""
请将以下内容翻译成自然、地道的日语。
不要添加解释，只输出翻译结果。

{text}
"""
    payload = {"model": MODEL, "prompt": prompt}

    response = requests.post(OLLAMA_URL, json=payload, stream=True)

    result = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            result += data.get("response", "")

    return result


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(TEMPLATE_FILE.read_text(encoding="utf-8"))


@app.post("/translate")
async def translate(request: Request):
    data = await request.json()
    text = data.get("text", "")
    result = translate_to_japanese(text)
    return {"translated": result}
