import os
import markdown
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

ACCOUNT_LINKS = [
    "https://www.sinotrade.com.tw/openact?strProd=0072&strWeb=0098&s=013448", # 陳巍
    "https://www.sinotrade.com.tw/openact?strProd=0072&strWeb=0098&s=013324"  # 呈偉
]

counter = 0

@app.get("/open_account")
async def open_account():
    global counter
    link = ACCOUNT_LINKS[counter % len(ACCOUNT_LINKS)]
    counter += 1
    return RedirectResponse(url=link)

# ======== Markdown 文章讀取系統 ========
def get_market_posts():
    posts_dir = os.path.join(BASE_DIR, "posts")
    if not os.path.exists(posts_dir):
        return []
    posts = []
    for filename in sorted(os.listdir(posts_dir), reverse=True):
        if filename.endswith(".md"):
            date_title = filename.replace(".md", "")
            posts.append({"title": date_title})
    return posts

def get_single_post(date_str):
    filepath = os.path.join(BASE_DIR, "posts", f"{date_str}.md")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        html_content = markdown.markdown(text)
        return {"title": date_str, "content": html_content}
# =======================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/market", response_class=HTMLResponse)
async def market_list(request: Request):
    posts = get_market_posts()
    return templates.TemplateResponse(request=request, name="market.html", context={"posts": posts})

@app.get("/market/{date_str}", response_class=HTMLResponse)
async def market_detail(request: Request, date_str: str):
    post = get_single_post(date_str)
    if not post:
        raise HTTPException(status_code=404, detail="找不到該日期的簡報")
    return templates.TemplateResponse(request=request, name="post.html", context={"post": post})

@app.get("/why_sinopac", response_class=HTMLResponse)
async def why_sinopac(request: Request):
    return templates.TemplateResponse(request=request, name="why_sinopac.html")

@app.get("/strategy", response_class=HTMLResponse)
async def strategy(request: Request):
    return templates.TemplateResponse(request=request, name="strategy.html")

@app.get("/tools", response_class=HTMLResponse)
async def tools(request: Request):
    return templates.TemplateResponse(request=request, name="tools.html")

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(request=request, name="about.html")

@app.get("/taitung", response_class=HTMLResponse)
async def taitung(request: Request):
    return templates.TemplateResponse(request=request, name="taitung.html")

# 🚀 新增的「最新消息」路由
@app.get("/news", response_class=HTMLResponse)
async def news(request: Request):
    return templates.TemplateResponse(request=request, name="news.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
