import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from routers import memory, stats
from db.sqlite import init_db

logger = logging.getLogger(__name__)

app = FastAPI(title="HomeRAG", version="0.1.0")

# 性能监控中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.2f}"
    logger.info(f"Request: {request.url.path} - Time: {process_time:.2f}s")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memory.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.on_event("startup")
async def startup():
    # 初始化 SQLite 表结构
    init_db()
