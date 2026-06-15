\---

name: course-qa-api

description: 通过本地 FastAPI 服务回答现代软件开发技术课程相关问题。适用于查询 RAG、Harness、Agent、TDD、CI/CD 等课程概念；调用前必须确认 API 服务已启动，并通过环境变量或本地配置提供 Token。

\---



\# Course QA API



\## 能力范围



\- 接收一个课程相关问题。

\- 调用 `POST /api/ask`。

\- 返回 `answer`、`sources`、`ok`、`request\_id`、`elapsed\_ms` 字段。



\## 接口约定



\- URL: `http://127.0.0.1:8000/api/ask`

\- Method: `POST`

\- Header: `Authorization: Bearer <LOCAL\_TEST\_TOKEN>`

\- Body:



```json

{

&#x20; "question": "RAG 是什么？"

}

```



\## 失败处理



\- `401`：检查 Token 是否与 `COURSE\_API\_TOKEN` 一致。

\- `422`：检查请求体字段和问题长度。

\- `500`：检查服务端是否设置 `COURSE\_API\_TOKEN`。

\- `ok=false`：说明当前示例工作流没有足够资料回答。

