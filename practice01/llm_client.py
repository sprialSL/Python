"""
Practice 01: 使用 Python 标准库调用 OpenAI 兼容 API
功能：
1. 读取 .env 配置文件
2. 使用 http.client 调用 LLM API
3. 支持流式输出（Streaming）
4. 统计 token 消耗、时间、首token延迟和速度
"""

import http.client
import json
import os
import time
from urllib.parse import urlparse


def load_env(env_path=".env"):
    """手动解析 .env 文件"""
    env_vars = {}
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"配置文件不存在: {env_path}")
    
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def build_request_path(base_url):
    """构建API请求路径"""
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    base_path = parsed_url.path.rstrip("/")
    
    if base_path.endswith("/chat/completions"):
        path = base_path
    elif base_path.endswith("/v1"):
        path = base_path + "/chat/completions"
    elif base_path == "":
        path = "/v1/chat/completions"
    else:
        path = base_path + "/chat/completions"
    
    return host, path, parsed_url.scheme


def call_llm_api_stream(base_url, api_key, model, messages, temperature=0.7, max_tokens=1000):
    """
    使用 http.client 调用 OpenAI 兼容 API (流式输出)
    
    Returns:
        content: 生成的完整内容
        stats: 统计信息字典
    """
    host, path, scheme = build_request_path(base_url)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    print(f"  - 请求路径: {path}")
    print(f"  - 请求主机: {host}")
    print(f"\n正在生成响应 (流式输出):\n" + "-" * 40)
    
    conn = None
    start_time = time.time()
    first_token_time = None
    content_chunks = []
    token_count = 0
    
    try:
        if scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=120)
        else:
            conn = http.client.HTTPConnection(host, timeout=120)
        
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        
        buffer = b""
        while True:
            chunk = response.read(1024)
            if not chunk:
                break
            
            buffer += chunk
            
            try:
                text = buffer.decode("utf-8")
                buffer = b""
            except UnicodeDecodeError:
                continue
            
            lines = text.split("\n")
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                if line.startswith("data: "):
                    data = line[6:]
                    
                    if data == "[DONE]":
                        break
                    
                    try:
                        chunk_data = json.loads(data)
                        choices = chunk_data.get("choices", [])
                        
                        if choices:
                            delta = choices[0].get("delta", {})
                            text_content = delta.get("content", "")
                            
                            if text_content:
                                if first_token_time is None:
                                    first_token_time = time.time()
                                
                                content_chunks.append(text_content)
                                token_count += 1
                                
                                print(text_content, end="", flush=True)
                    except json.JSONDecodeError:
                        continue
        
        end_time = time.time()
        total_time = end_time - start_time
        first_token_delay = first_token_time - start_time if first_token_time else 0
        generation_time = end_time - first_token_time if first_token_time else 0
        
        print("\n" + "-" * 40)
        
        stats = {
            "total_time": total_time,
            "first_token_delay": first_token_delay,
            "generation_time": generation_time,
            "estimated_tokens": token_count,
            "tokens_per_second": token_count / generation_time if generation_time > 0 else 0
        }
        
        return "".join(content_chunks), stats
    
    finally:
        if conn:
            conn.close()


def call_llm_api_normal(base_url, api_key, model, messages, temperature=0.7, max_tokens=1000):
    """
    使用 http.client 调用 OpenAI 兼容 API (非流式)
    
    Returns:
        response_data: 响应数据
        elapsed_time: 请求耗时
    """
    host, path, scheme = build_request_path(base_url)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    print(f"  - 请求路径: {path}")
    print(f"  - 请求主机: {host}")
    
    conn = None
    start_time = time.time()
    
    try:
        if scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=120)
        else:
            conn = http.client.HTTPConnection(host, timeout=120)
        
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        response_data = response.read().decode("utf-8")
        elapsed_time = time.time() - start_time
        
        return json.loads(response_data), elapsed_time
    
    finally:
        if conn:
            conn.close()


def print_stream_statistics(stats, content):
    """打印流式输出统计信息"""
    print("\n" + "=" * 60)
    print("LLM API 调用统计报告 (流式输出)")
    print("=" * 60)
    
    print(f"\n时间统计:")
    print(f"  - 首Token延迟: {stats['first_token_delay']:.2f} 秒")
    print(f"  - 生成时间: {stats['generation_time']:.2f} 秒")
    print(f"  - 总耗时: {stats['total_time']:.2f} 秒")
    
    print(f"\nToken 统计:")
    print(f"  - 估算Token数: {stats['estimated_tokens']}")
    
    if stats['tokens_per_second'] > 0:
        print(f"\n速度统计:")
        print(f"  - 生成速度: {stats['tokens_per_second']:.2f} tokens/秒")
    
    print(f"\n响应内容长度: {len(content)} 字符")
    print("=" * 60)


def print_normal_statistics(response, elapsed_time):
    """打印非流式输出统计信息"""
    print("\n" + "=" * 60)
    print("LLM API 调用统计报告 (非流式)")
    print("=" * 60)
    
    if "error" in response:
        print(f"\n错误信息: {response['error']}")
        return
    
    usage = response.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)
    
    print(f"\nToken 消耗统计:")
    print(f"  - Prompt Tokens: {prompt_tokens}")
    print(f"  - Completion Tokens: {completion_tokens}")
    print(f"  - Total Tokens: {total_tokens}")
    
    print(f"\n时间统计:")
    print(f"  - 请求耗时: {elapsed_time:.2f} 秒")
    
    if completion_tokens > 0 and elapsed_time > 0:
        tokens_per_second = completion_tokens / elapsed_time
        print(f"\n速度统计:")
        print(f"  - 生成速度: {tokens_per_second:.2f} tokens/秒")
    
    choices = response.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content", "")
        role = message.get("role", "unknown")
        
        print(f"\n响应内容:")
        print(f"  - 角色: {role}")
        if len(content) > 200:
            print(f"  - 内容: {content[:200]}...")
        else:
            print(f"  - 内容: {content}")
    
    print("=" * 60)


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, ".env")
    
    print(f"正在加载配置文件: {env_path}")
    env = load_env(env_path)
    
    base_url = env.get("OPENAI_BASE_URL")
    api_key = env.get("OPENAI_API_KEY")
    model = env.get("OPENAI_MODEL")
    temperature = float(env.get("TEMPERATURE", 0.7))
    max_tokens = int(env.get("MAX_TOKENS", 1000))
    use_stream = env.get("USE_STREAM", "true").lower() == "true"
    
    print(f"\n配置信息:")
    print(f"  - Base URL: {base_url}")
    print(f"  - Model: {model}")
    print(f"  - Temperature: {temperature}")
    print(f"  - Max Tokens: {max_tokens}")
    print(f"  - Stream Mode: {use_stream}")
    
    messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
        {"role": "user", "content": "请用一句话介绍什么是人工智能。"}
    ]
    
    print(f"\n正在调用 LLM API...")
    
    try:
        if use_stream:
            content, stats = call_llm_api_stream(
                base_url=base_url,
                api_key=api_key,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            print_stream_statistics(stats, content)
        else:
            response, elapsed_time = call_llm_api_normal(
                base_url=base_url,
                api_key=api_key,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            print_normal_statistics(response, elapsed_time)
        
    except Exception as e:
        print(f"\n调用失败: {str(e)}")


if __name__ == "__main__":
    main()
