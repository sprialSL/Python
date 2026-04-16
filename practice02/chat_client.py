"""
Practice 02: 终端界面聊天客户端
功能：
1. 支持终端界面输入聊天内容
2. 支持流式输出
3. 支持历史聊天记录自动添加到上下文
4. 直到用户ctrl+c退出终端，否则一直循环
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
    
    print(f"\n配置信息:")
    print(f"  - Base URL: {base_url}")
    print(f"  - Model: {model}")
    print(f"  - Temperature: {temperature}")
    print(f"  - Max Tokens: {max_tokens}")
    
    # 初始化聊天历史
    messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。"}
    ]
    
    print(f"\n欢迎使用终端聊天客户端！")
    print(f"输入消息后按回车发送，按 Ctrl+C 退出。\n")
    
    try:
        while True:
            # 获取用户输入
            user_input = input("你: ")
            
            # 添加用户消息到聊天历史
            messages.append({"role": "user", "content": user_input})
            
            print("AI: ", end="", flush=True)
            
            # 调用API获取响应
            content, stats = call_llm_api_stream(
                base_url=base_url,
                api_key=api_key,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 添加AI响应到聊天历史
            messages.append({"role": "assistant", "content": content})
            
            # 打印统计信息
            print_stream_statistics(stats, content)
            print()
    
    except KeyboardInterrupt:
        print("\n\n聊天已结束，再见！")


if __name__ == "__main__":
    main()
