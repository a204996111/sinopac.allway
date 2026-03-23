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
    link = ACCOUNT_LINKS[counter % 2]
    counter += 1
    return RedirectResponse(url=link)

# ======== Markdown 文章讀取系統 ========
def get_market_posts():
    posts_dir = os.path.join(BASE_DIR, "posts")
    if not os.path.exists(posts_dir):
        return []

    posts = []
    # 自動讀取 posts 裡面所有的 .md 檔案，並依檔名倒序排列
    for filename in sorted(os.listdir(posts_dir), reverse=True):
        if filename.endswith(".md"):
            date_title = filename.replace(".md", "")
            # 列表頁不需要讀取完整內容，只要標題(日期)就好
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
    return templates.TemplateResponse("index.html", {"request": request})

# 1. 這是「市場消息」的列表頁
@app.get("/market", response_class=HTMLResponse)
async def market_list(request: Request):
    posts = get_market_posts()
    return templates.TemplateResponse("market.html", {"request": request, "posts": posts})

# 2. 這是「點擊特定日期後」的文章內容頁
@app.get("/market/{date_str}", response_class=HTMLResponse)
async def market_detail(request: Request, date_str: str):
    post = get_single_post(date_str)
    if not post:
        raise HTTPException(status_code=404, detail="找不到該日期的簡報")
    return templates.TemplateResponse("post.html", {"request": request, "post": post})

@app.get("/why_sinopac", response_class=HTMLResponse)
async def why_sinopac(request: Request):
    return templates.TemplateResponse("why_sinopac.html", {"request": request})

@app.get("/strategy", response_class=HTMLResponse)
async def strategy(request: Request):
    return templates.TemplateResponse("strategy.html", {"request": request})

@app.get("/tools", response_class=HTMLResponse)
async def tools(request: Request):
    return templates.TemplateResponse("tools.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)