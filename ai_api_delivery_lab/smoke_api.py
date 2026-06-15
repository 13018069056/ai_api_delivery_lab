import json
import sys
import urllib.error
import urllib.request


def request_json(url: str, method: str = "GET", token: str | None = None, body: dict | None = None) -> tuple[int, str]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    token = sys.argv[2] if len(sys.argv) > 2 else "dev-local-token"

    health_status, health_body = request_json(f"{base_url}/health")
    no_token_status, _ = request_json(f"{base_url}/api/ask", method="POST", body={"question": "RAG 是什么？"})
    ok_status, ok_body = request_json(
        f"{base_url}/api/ask",
        method="POST",
        token=token,
        body={"question": "RAG 是什么？"},
    )

    print("health", health_status, health_body)
    print("no_token", no_token_status)
    print("with_token", ok_status, ok_body)

    assert health_status == 200
    assert no_token_status == 401
    assert ok_status == 200


if __name__ == "__main__":
    main()