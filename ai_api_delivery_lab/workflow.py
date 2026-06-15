import os
import httpx
import time
import logging

# 日志初始化（配套加分2日志功能）
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s | %(message)s")
logger = logging.getLogger("ai-workflow")

def run_ai_workflow(question: str, req_id: str) -> dict:
    """
    集成DeepSeek大模型API + 本地课程知识库双逻辑
    req_id：外部传入全局请求ID，实现全链路日志串联（加分2）
    """
    start_time = time.perf_counter()
    question = question.strip()
    logger.info(f"[{req_id}] 收到用户提问：{question}")

    # 空输入校验
    if not question:
        logger.warning(f"[{req_id}] 问题为空，返回校验失败")
        return {
            "answer": "问题不能为空。",
            "sources": [],
            "ok": False,
            "model": "local_rule"
        }

    # 读取DeepSeek密钥（从.env文件，加分4）
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    use_local_rule = False
    answer = ""
    sources = []

    # 本地规则知识库优先匹配课程关键词
    if "RAG" in question or "检索" in question:
        answer = "RAG 通过检索外部资料增强回答，可以降低幻觉风险。"
        sources = ["course_notes:rag"]
        use_local_rule = True
    elif "Harness" in question or "护栏" in question:
        answer = "Harness 工程通过代码级护栏限制 Agent 的工具调用范围。"
        sources = ["course_notes:harness"]
        use_local_rule = True
    elif "Agent" in question or "状态机" in question:
        answer = "Agent 工作流可以用目标契约、状态机、检查点和测试结果来约束。"
        sources = ["course_notes:agent_workflow"]
        use_local_rule = True

    # 无本地匹配、且存在密钥时调用DeepSeek真实API
    if not use_local_rule and deepseek_key:
        logger.info(f"[{req_id}] 调用DeepSeek大模型API")
        headers = {
            "Authorization": f"Bearer {deepseek_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.7
        }
        try:
            resp = httpx.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=1000
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            sources = ["deepseek-chat"]
            logger.info(f"[{req_id}] DeepSeek接口调用成功")
        except Exception as e:
            logger.error(f"[{req_id}] DeepSeek调用失败: {str(e)}")
            answer = f"大模型接口调用异常，本地兜底：{str(e)}"
            sources = []
    elif not use_local_rule and not deepseek_key:
        answer = "未配置DeepSeek密钥，仅本地规则库可识别RAG/Harness/Agent相关问题。"
        sources = []

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"[{req_id}] 工作流执行完成，耗时{elapsed_ms}ms")
    return {
        "answer": answer,
        "sources": sources,
        "ok": bool(sources),
        "model": "local_rule" if use_local_rule else "deepseek-chat" if deepseek_key else "fallback_local"
    }
