import os
import time
import uuid
import logging
from dotenv import load_dotenv  # 加分4：读取.env配置文件

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from workflow import run_ai_workflow, logger

# 加载.env环境变量（加分4）
load_dotenv()
API_TOKEN_ENV = "COURSE_API_TOKEN"

app = FastAPI(title="Modern Software AI API", version="0.3.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "null"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# 全局请求日志中间件，自动生成/透传request_id
@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.req_id = req_id
    start = time.perf_counter()
    logger.info(f"[{req_id}] 收到请求 {request.method} {request.url.path}")
    response = await call_next(request)
    elapsed = int((time.perf_counter() - start) * 1000)
    response.headers["X-Request-ID"] = req_id
    logger.info(f"[{req_id}] 请求完成 状态码:{response.status_code} 耗时:{elapsed}ms")
    return response

# 请求/响应模型
class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500, description="用户提问，1~500字符")

class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    ok: bool
    request_id: str
    elapsed_ms: int
    model: str  # 新增字段，区分本地规则/DeepSeek模型

# Token校验逻辑
def expected_token() -> str:
    token = os.getenv(API_TOKEN_ENV)
    if not token:
        raise HTTPException(status_code=500, detail=f"{API_TOKEN_ENV} 未在.env中配置")
    return token

def check_token(authorization: str | None, req_id: str) -> None:
    expected = f"Bearer {expected_token()}"
    if authorization != expected:
        logger.warning(f"[{req_id}] Token校验失败")
        raise HTTPException(status_code=401, detail="invalid token")

# 接口
@app.get("/health")
def health(request: Request) -> dict:
    return {"status": "ok", "request_id": request.state.req_id}

@app.post("/api/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    request: Request,
    authorization: str | None = Header(default=None)
) -> dict:
    req_id = request.state.req_id
    check_token(authorization, req_id)
    start = time.perf_counter()
    workflow_res = run_ai_workflow(payload.question, req_id)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return {
        **workflow_res,
        "request_id": req_id,
        "elapsed_ms": elapsed_ms,
    }
