"""
Practice 02: 工具调用客户端
功能：
1. 列出某个目录下有哪些文件（包括文件的基本属性、大小等信息）
2. 修改某个目录下某个文件的名字
3. 删除某个目录下的某个文件
4. 在某个目录下新建1个文件，并且写入内容
5. 读取某个目录下的某个文件的内容
6. 将这些工具调用的能力作为系统提示词发送给LLM，实现工具调用
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


def list_files(directory):
    """
    列出某个目录下有哪些文件（包括文件的基本属性、大小等信息）
    
    Args:
        directory: 目录路径
    
    Returns:
        包含文件信息的列表
    """
    if not os.path.exists(directory):
        return f"错误：目录 {directory} 不存在"
    
    if not os.path.isdir(directory):
        return f"错误：{directory} 不是一个目录"
    
    files = []
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "name": filename,
                    "size": stat.st_size,  # 字节
                    "mtime": time.ctime(stat.st_mtime),  # 修改时间
                    "is_file": True
                })
            else:
                files.append({
                    "name": filename,
                    "is_file": False
                })
        return files
    except Exception as e:
        return f"错误：{str(e)}"


def rename_file(directory, old_name, new_name):
    """
    修改某个目录下某个文件的名字
    
    Args:
        directory: 目录路径
        old_name: 原文件名
        new_name: 新文件名
    
    Returns:
        操作结果
    """
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)
    
    if not os.path.exists(old_path):
        return f"错误：文件 {old_path} 不存在"
    
    if os.path.exists(new_path):
        return f"错误：文件 {new_path} 已存在"
    
    try:
        os.rename(old_path, new_path)
        return f"成功：文件已重命名为 {new_name}"
    except Exception as e:
        return f"错误：{str(e)}"


def delete_file(directory, filename):
    """
    删除某个目录下的某个文件
    
    Args:
        directory: 目录路径
        filename: 文件名
    
    Returns:
        操作结果
    """
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        return f"错误：文件 {file_path} 不存在"
    
    if not os.path.isfile(file_path):
        return f"错误：{file_path} 不是一个文件"
    
    try:
        os.remove(file_path)
        return f"成功：文件已删除"
    except Exception as e:
        return f"错误：{str(e)}"


def create_file(directory, filename, content):
    """
    在某个目录下新建1个文件，并且写入内容
    
    Args:
        directory: 目录路径
        filename: 文件名
        content: 文件内容
    
    Returns:
        操作结果
    """
    if not os.path.exists(directory):
        return f"错误：目录 {directory} 不存在"
    
    if not os.path.isdir(directory):
        return f"错误：{directory} 不是一个目录"
    
    file_path = os.path.join(directory, filename)
    
    if os.path.exists(file_path):
        return f"错误：文件 {file_path} 已存在"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功：文件已创建"
    except Exception as e:
        return f"错误：{str(e)}"


def read_file(directory, filename):
    """
    读取某个目录下的某个文件的内容
    
    Args:
        directory: 目录路径
        filename: 文件名
    
    Returns:
        文件内容
    """
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        return f"错误：文件 {file_path} 不存在"
    
    if not os.path.isfile(file_path):
        return f"错误：{file_path} 不是一个文件"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"错误：{str(e)}"


def curl(url):
    """
    通过curl访问网页并返回网页内容
    
    Args:
        url: http//wttr.in/
    
    Returns:
        网页内容
    """
    from urllib.parse import urlparse
    
    try:
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path
        if not path:
            path = "/"
        if parsed_url.query:
            path += f"?{parsed_url.query}"
        
        scheme = parsed_url.scheme
        if scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=30)
        else:
            conn = http.client.HTTPConnection(host, timeout=30)
        
        conn.request("GET", path)
        response = conn.getresponse()
        
        if response.status == 200:
            content = response.read().decode("utf-8", errors="ignore")
            conn.close()
            return content
        else:
            conn.close()
            return f"错误：HTTP请求失败，状态码：{response.status}"
    except Exception as e:
        return f"错误：{str(e)}"


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


def execute_tool_call(tool_call):
    """
    执行工具调用
    
    Args:
        tool_call: 工具调用信息，包含 function 和 arguments
    
    Returns:
        工具执行结果
    """
    function_name = tool_call.get("function")
    arguments = tool_call.get("arguments", {})
    
    if function_name == "list_files":
        directory = arguments.get("directory")
        return list_files(directory)
    elif function_name == "rename_file":
        directory = arguments.get("directory")
        old_name = arguments.get("old_name")
        new_name = arguments.get("new_name")
        return rename_file(directory, old_name, new_name)
    elif function_name == "delete_file":
        directory = arguments.get("directory")
        filename = arguments.get("filename")
        return delete_file(directory, filename)
    elif function_name == "create_file":
        directory = arguments.get("directory")
        filename = arguments.get("filename")
        content = arguments.get("content")
        return create_file(directory, filename, content)
    elif function_name == "read_file":
        directory = arguments.get("directory")
        filename = arguments.get("filename")
        return read_file(directory, filename)
    elif function_name == "curl":
        url = arguments.get("url")
        return curl(url)
    else:
        return f"错误：未知的工具函数 {function_name}"


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
    
    # 系统提示词，包含工具调用能力
    system_prompt = """你是一个有帮助的AI助手，并且可以使用以下工具来执行文件操作和网络访问：

工具列表：
1. list_files(directory): 列出某个目录下有哪些文件（包括文件的基本属性、大小等信息）
   参数：
   - directory: 目录路径

2. rename_file(directory, old_name, new_name): 修改某个目录下某个文件的名字
   参数：
   - directory: 目录路径
   - old_name: 原文件名
   - new_name: 新文件名

3. delete_file(directory, filename): 删除某个目录下的某个文件
   参数：
   - directory: 目录路径
   - filename: 文件名

4. create_file(directory, filename, content): 在某个目录下新建1个文件，并且写入内容
   参数：
   - directory: 目录路径
   - filename: 文件名
   - content: 文件内容

5. read_file(directory, filename): 读取某个目录下的某个文件的内容
   参数：
   - directory: 目录路径
   - filename: 文件名

6. curl(url): 通过curl访问网页并返回网页内容
   参数：
   - url: 网页URL

当你需要执行文件操作或网络访问时，请使用以下格式输出工具调用：

```tool_call
{
  "function": "工具函数名",
  "arguments": {
    "参数1": "值1",
    "参数2": "值2"
  }
}
```

我会执行该工具并返回结果，然后你可以根据结果继续与我交互。"""
    
    # 初始化聊天历史
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    print(f"\n欢迎使用工具调用客户端！")
    print(f"输入消息后按回车发送，按 Ctrl+C 退出。\n")
    print(f"你可以使用以下工具：")
    print(f"1. list_files(directory) - 列出目录下的文件")
    print(f"2. rename_file(directory, old_name, new_name) - 修改文件名")
    print(f"3. delete_file(directory, filename) - 删除文件")
    print(f"4. create_file(directory, filename, content) - 创建文件并写入内容")
    print(f"5. read_file(directory, filename) - 读取文件内容")
    print(f"6. curl(url) - 通过curl访问网页并返回网页内容")
    print()
    
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
            
            # 检查是否包含工具调用
            if content.strip().startswith("```tool_call") and content.strip().endswith("```"):
                # 提取工具调用信息
                tool_call_str = content.strip().replace("```tool_call", "").replace("```", "").strip()
                try:
                    tool_call = json.loads(tool_call_str)
                    print("\n执行工具调用...")
                    # 执行工具调用
                    tool_result = execute_tool_call(tool_call)
                    print(f"工具执行结果: {tool_result}")
                    # 添加工具执行结果到聊天历史
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": f"工具执行结果: {tool_result}"})
                except json.JSONDecodeError:
                    print("\n错误：工具调用格式不正确")
                    messages.append({"role": "assistant", "content": content})
            else:
                # 普通响应，添加到聊天历史
                messages.append({"role": "assistant", "content": content})
            
            # 打印统计信息
            print_stream_statistics(stats, content)
            print()
    
    except KeyboardInterrupt:
        print("\n\n聊天已结束，再见！")


def test_curl():
    """
    测试curl工具访问https://wttr.in/
    """
    print("测试curl工具访问https://wttr.in/")
    result = curl("https://wttr.in/")
    print("\n访问结果:")
    print(result[:1000])  # 只打印前1000个字符，避免输出过多


def direct_curl():
    """
    直接使用curl工具，不依赖LLM API
    """
    print("直接使用curl工具访问网页")
    print("请输入要访问的URL (默认: https://wttr.in/):")
    url = input("URL: ").strip()
    if not url:
        url = "https://wttr.in/"
    print(f"\n正在访问: {url}")
    result = curl(url)
    print("\n访问结果:")
    print(result[:1000])  # 只打印前1000个字符，避免输出过多


import sys

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--curl":
        # 直接使用curl工具访问https://wttr.in/
        print("直接使用curl工具访问https://wttr.in/")
        result = curl("https://wttr.in/")
        print("\n访问结果:")
        print(result[:1000])  # 只打印前1000个字符，避免输出过多
    else:
        # 运行主程序
        main()
