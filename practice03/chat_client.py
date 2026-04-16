"""
Practice 03: 终端界面聊天客户端（带聊天记录总结和压缩功能）
功能：
1. 支持终端界面输入聊天内容
2. 支持流式输出
3. 支持历史聊天记录自动添加到上下文
4. 当聊天超过5轮或上下文长度超过3k时，自动触发聊天记录总结和压缩
5. 对于前70%左右的内容进行压缩，最后30%左右的内容保留原文
6. 直到用户ctrl+c退出终端，否则一直循环
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


def call_llm_api(base_url, api_key, model, messages, temperature=0.7, max_tokens=1000):
    """
    使用 http.client 调用 OpenAI 兼容 API (非流式输出)
    用于生成聊天记录总结
    
    Returns:
        content: 生成的完整内容
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
    
    conn = None
    
    try:
        if scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=120)
        else:
            conn = http.client.HTTPConnection(host, timeout=120)
        
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        
        response_data = json.loads(response.read().decode("utf-8"))
        content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        return content
    
    finally:
        if conn:
            conn.close()


def summarize_chat_history(messages, base_url, api_key, model):
    """
    总结聊天历史记录
    """
    # 准备总结请求
    summary_prompt = [
        {
            "role": "system",
            "content": "你是一个聊天记录总结助手。请对以下聊天记录进行简洁的总结，保留重要信息和关键对话内容。"
        },
        {
            "role": "user",
            "content": "请总结以下聊天记录：\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        }
    ]
    
    print("\n正在生成聊天记录总结...")
    summary = call_llm_api(base_url, api_key, model, summary_prompt, temperature=0.3, max_tokens=500)
    print("聊天记录总结完成！\n")
    
    return summary


def should_compress_chat_history(messages, max_rounds=5, max_length=3000):
    """
    判断是否需要压缩聊天历史
    """
    # 计算完整的对话轮数（用户消息和助手消息交替出现）
    user_messages = [msg for msg in messages if msg['role'] == 'user']
    assistant_messages = [msg for msg in messages if msg['role'] == 'assistant']
    # 对话轮数取用户消息和助手消息数量的最小值
    round_count = min(len(user_messages), len(assistant_messages))
    
    # 计算聊天上下文长度
    total_length = sum(len(msg['content']) for msg in messages)
    
    return round_count > max_rounds or total_length > max_length


def compress_chat_history(messages, base_url, api_key, model):
    """
    压缩聊天历史记录
    前70%左右的内容进行压缩，最后30%左右的内容保留原文
    """
    # 移除系统消息，只处理用户和助手的消息
    user_assistant_messages = [msg for msg in messages if msg['role'] in ['user', 'assistant']]
    
    # 计算分割点（70%）
    split_point = int(len(user_assistant_messages) * 0.7)
    
    # 前70%的消息进行总结
    messages_to_summarize = user_assistant_messages[:split_point]
    # 最后30%的消息保留原文
    messages_to_keep = user_assistant_messages[split_point:]
    
    # 生成总结
    summary = summarize_chat_history(messages_to_summarize, base_url, api_key, model)
    
    # 构建新的消息列表
    new_messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
        {
            "role": "assistant", 
            "content": f"[聊天记录总结]\n{summary}\n\n[最近对话]"
        }
    ]
    
    # 添加保留的原文消息
    new_messages.extend(messages_to_keep)
    
    return new_messages


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


def extract_key_information(messages, base_url, api_key, model):
    """
    从聊天记录中提取关键信息，按照5W规则
    """
    # 准备提取关键信息的请求
    extract_prompt = [
        {
            "role": "system",
            "content": "你是一个信息提取助手。请从以下聊天记录中提取关键信息，按照5W规则（谁who、做了什么事what、什么时候when（可选）、在何处where（可选）、为什么要做这个事why（可选））进行提取。每条关键信息请单独列出。"
        },
        {
            "role": "user",
            "content": "请从以下聊天记录中提取关键信息，按照5W规则：\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        }
    ]
    
    print("\n正在提取关键信息...")
    key_info = call_llm_api(base_url, api_key, model, extract_prompt, temperature=0.3, max_tokens=1000)
    print("关键信息提取完成！\n")
    
    return key_info


def record_key_information(key_info):
    """
    记录关键信息到本地文件
    """
    # 使用用户主目录存储日志文件，提高跨平台兼容性
    log_dir = os.path.join(os.path.expanduser("~"), "chat-log")
    log_file = os.path.join(log_dir, "log.txt")
    
    # 确保目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 增量写入关键信息
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"记录时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n")
        f.write(key_info + "\n\n")
    
    print(f"关键信息已记录到: {log_file}\n")


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
    
    # 初始化聊天轮数计数器
    chat_rounds = 0
    
    print(f"\n欢迎使用终端聊天客户端！")
    print(f"输入消息后按回车发送，按 Ctrl+C 退出。")
    print(f"当聊天超过5轮或上下文长度超过3k时，系统会自动总结和压缩聊天记录。")
    print(f"每五次聊天，系统会自动提取关键信息并记录到本地文件。\n")
    
    try:
        while True:
            # 检查是否需要压缩聊天历史
            if should_compress_chat_history(messages):
                messages = compress_chat_history(messages, base_url, api_key, model)
                print("\n聊天记录已压缩，继续对话...\n")
            
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
            
            # 增加聊天轮数
            chat_rounds += 1
            
            # 每五次聊天提取一次关键信息
            if chat_rounds % 5 == 0:
                # 提取关键信息
                key_info = extract_key_information(messages, base_url, api_key, model)
                # 记录关键信息
                record_key_information(key_info)
            
            # 打印统计信息
            print_stream_statistics(stats, content)
            print()
    
    except KeyboardInterrupt:
        print("\n\n聊天已结束，再见！")


if __name__ == "__main__":
    main()