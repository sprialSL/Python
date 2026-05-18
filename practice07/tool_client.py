import os
import json
import http.client
import ssl
from urllib.parse import urlparse
import sys
import stat
import time
import subprocess
import yaml

# 读取.env文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        print(f"错误：{env_path} 文件不存在，请从 env.example 复制并填写正确参数")
        exit(1)
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

# 函数：读取技能列表
def list_available_skills():
    try:
        skills_dir = os.path.join(os.path.dirname(__file__), '.agents', 'skills')
        if not os.path.exists(skills_dir):
            return json.dumps({"status": "error", "message": "技能目录不存在"}, ensure_ascii=False)
        
        skills = []
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            if os.path.isdir(skill_path):
                skill_md_path = os.path.join(skill_path, 'SKILL.md')
                if os.path.exists(skill_md_path):
                    with open(skill_md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 解析 YAML front matter
                    if content.startswith('---'):
                        end_marker = content.find('---', 3)
                        if end_marker != -1:
                            yaml_content = content[3:end_marker]
                            try:
                                front_matter = yaml.safe_load(yaml_content)
                                skill_info = {
                                    "name": front_matter.get('name', skill_name),
                                    "description": front_matter.get('description', '')
                                }
                                skills.append(skill_info)
                            except yaml.YAMLError:
                                skills.append({
                                    "name": skill_name,
                                    "description": ''
                                })
        
        skills_json = json.dumps({"skills": skills}, ensure_ascii=False, indent=2)
        return json.dumps({"status": "success", "data": skills_json}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 函数：加载技能正文内容
def load_skill_content(skill_name):
    try:
        skills_dir = os.path.join(os.path.dirname(__file__), '.agents', 'skills')
        skill_path = os.path.join(skills_dir, skill_name)
        skill_md_path = os.path.join(skill_path, 'SKILL.md')
        
        if not os.path.exists(skill_md_path):
            return json.dumps({"status": "error", "message": f"技能 {skill_name} 不存在"}, ensure_ascii=False)
        
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 YAML front matter 之后的内容
        if content.startswith('---'):
            end_marker = content.find('---', 3)
            if end_marker != -1:
                skill_content = content[end_marker + 3:].strip()
            else:
                skill_content = content
        else:
            skill_content = content
        
        return json.dumps({"status": "success", "data": skill_content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数1：列出某个目录下的文件（包括基本属性、大小等信息）
def list_files(directory):
    try:
        files = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            stat_info = os.stat(item_path)
            files.append({
                "name": item,
                "path": item_path,
                "size": stat_info.st_size,
                "mode": stat.filemode(stat_info.st_mode),
                "mtime": stat_info.st_mtime
            })
        return json.dumps({"status": "success", "data": files}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数2：修改某个目录下某个文件的名字
def rename_file(directory, old_name, new_name):
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        return json.dumps({"status": "success", "message": f"文件已重命名为 {new_name}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数3：删除某个目录下的某个文件
def delete_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        os.remove(file_path)
        return json.dumps({"status": "success", "message": "文件已删除"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数4：在某个目录下新建1个文件，并且写入内容
def create_file(directory, file_name, content):
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return json.dumps({"status": "success", "message": "文件已创建"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数5：读取某个目录下的某个文件的内容
def read_file(directory, file_name):
    try:
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return json.dumps({"status": "success", "data": content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数6：访问网页并返回内容
def fetch_webpage(url):
    try:
        url = url.strip('`')
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        from urllib.parse import quote
        path = parsed_url.path if parsed_url.path else '/'
        path = quote(path, safe='/')
        if parsed_url.query:
            path += '?' + quote(parsed_url.query, safe='=&%+')
        protocol = parsed_url.scheme
        
        if protocol == 'https':
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            conn = http.client.HTTPSConnection(host, context=context)
        else:
            conn = http.client.HTTPConnection(host)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        conn.request('GET', path, headers=headers)
        response = conn.getresponse()
        content = response.read().decode('utf-8', errors='replace')
        
        max_content_length = 100000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n... (内容已截断)"
        
        return json.dumps({"status": "success", "data": content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数7：搜索聊天历史
def search_chat_history(query):
    try:
        log_path = os.getenv('LOG_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log.txt'))
        if not os.path.exists(log_path):
            return json.dumps({"status": "error", "message": "聊天历史文件不存在"}, ensure_ascii=False)
        
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        search_prompt = f"用户查询: {query}\n\n聊天历史记录:\n{content}\n\n请根据聊天历史回答用户的问题，重点关注与查询相关的信息。"
        
        return json.dumps({"status": "success", "data": search_prompt}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 工具函数8：访问AnythingLLM文档仓库
def anythingllm_query(message):
    try:
        api_key = os.getenv('ANYTHINGLLM_API_KEY')
        workspace_slug = os.getenv('ANYTHINGLLM_WORKSPACE_SLUG')
        
        if not api_key or not workspace_slug:
            return json.dumps({"status": "error", "message": "请在.env文件中配置ANYTHINGLLM_API_KEY和ANYTHINGLLM_WORKSPACE_SLUG"}, ensure_ascii=False)
        
        url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
        
        payload = json.dumps({
            "message": message
        })
        
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", f"Authorization: Bearer {api_key}",
            "-H", "Content-Type: application/json",
            "-d", payload
        ]
        
        timeout_sec = int(os.getenv('ANYTHINGLLM_TIMEOUT', '300'))
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=timeout_sec
        )
        
        if result.returncode != 0:
            return json.dumps({"status": "error", "message": f"curl命令执行失败: {result.stderr}"}, ensure_ascii=False)
        
        try:
            response_data = json.loads(result.stdout)
            return json.dumps({"status": "success", "data": response_data}, ensure_ascii=False)
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": f"响应解析失败: {result.stdout}"}, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        timeout_sec = int(os.getenv('ANYTHINGLLM_TIMEOUT', '300'))
        return json.dumps({
            "status": "error", 
            "message": f"请求超时（{timeout_sec}秒），请检查 AnythingLLM 服务是否正常运行"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)

# 调用LLM API（非流式，用于工具调用）
def call_llm(messages, tools=None):
    base_url = os.getenv('BASE_URL')
    model = os.getenv('MODEL')
    api_key = os.getenv('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误：请在.env文件中配置BASE_URL、MODEL和API_KEY")
        exit(1)
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    protocol = parsed_url.scheme
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv('TEMPERATURE', '0.7')),
        "max_tokens": int(os.getenv('MAX_TOKENS', '8192'))
    }
    
    if tools:
        data["tools"] = tools
        data["tool_choice"] = "auto"
    
    if protocol == 'https':
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = http.client.HTTPSConnection(host, context=context)
    else:
        conn = http.client.HTTPConnection(host)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', path, json.dumps(data), headers)
        response = conn.getresponse()
        response_content = response.read().decode()
        
        try:
            response_data = json.loads(response_content)
        except json.JSONDecodeError:
            if response.status == 200:
                return response_content
            else:
                print(f"API错误: {response_content}")
                return None
        
        if response.status == 200:
            return response_data
        else:
            if isinstance(response_data, dict):
                error_info = response_data.get('error', {})
                if isinstance(error_info, dict):
                    error_message = error_info.get('message', '未知错误')
                else:
                    error_message = str(error_info)
            else:
                error_message = str(response_data)
            print(f"API错误: {error_message}")
            return None
    finally:
        conn.close()

# 流式调用LLM API（用于普通对话）
def stream_llm(messages):
    base_url = os.getenv('BASE_URL')
    model = os.getenv('MODEL')
    api_key = os.getenv('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误：请在.env文件中配置BASE_URL、MODEL和API_KEY")
        exit(1)
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    protocol = parsed_url.scheme
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv('TEMPERATURE', '0.7')),
        "max_tokens": int(os.getenv('MAX_TOKENS', '8192')),
        "stream": True
    }
    
    if protocol == 'https':
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = http.client.HTTPSConnection(host, context=context)
    else:
        conn = http.client.HTTPConnection(host)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', path, json.dumps(data), headers)
        response = conn.getresponse()
        
        if response.status != 200:
            error_data = json.loads(response.read().decode())
            print(f"API错误: {error_data.get('error', {}).get('message', '未知错误')}")
            return None
        
        full_response = ""
        for line in response:
            line = line.decode().strip()
            if not line:
                continue
            if line.startswith('data: '):
                line = line[6:]
                if line == '[DONE]':
                    break
                try:
                    chunk = json.loads(line)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        if 'content' in delta:
                            content = delta['content']
                            if content is not None:
                                print(content, end='', flush=True)
                                full_response += content
                except json.JSONDecodeError:
                    pass
        print()
        return full_response
    finally:
        conn.close()

# 执行工具调用
def execute_tool_call(tool_call):
    if tool_call.get('type') == 'function':
        function = tool_call.get('function', {})
        tool_name = function.get('name')
        arguments = function.get('arguments', {})
        if isinstance(arguments, str):
            try:
                tool_args = json.loads(arguments)
            except json.JSONDecodeError:
                tool_args = {}
        else:
            tool_args = arguments
    else:
        tool_name = tool_call.get('name')
        tool_args = tool_call.get('arguments', {})
    
    print(f"执行工具: {tool_name}")
    print(f"参数: {tool_args}")
    
    if tool_name == "list_directory":
        path = tool_args.get('path')
        result = list_files(path)
    elif tool_name == "rename_file":
        directory = tool_args.get('directory')
        old_name = tool_args.get('old_name')
        new_name = tool_args.get('new_name')
        result = rename_file(directory, old_name, new_name)
    elif tool_name == "delete_file":
        directory = tool_args.get('directory')
        file_name = tool_args.get('file_name')
        result = delete_file(directory, file_name)
    elif tool_name == "create_file":
        directory = tool_args.get('directory')
        file_name = tool_args.get('file_name')
        content = tool_args.get('content')
        result = create_file(directory, file_name, content)
    elif tool_name == "read_file":
        directory = tool_args.get('directory')
        file_name = tool_args.get('file_name')
        result = read_file(directory, file_name)
    elif tool_name == "fetch_webpage":
        url = tool_args.get('url')
        result = fetch_webpage(url)
    elif tool_name == "search_chat_history":
        query = tool_args.get('query')
        result = search_chat_history(query)
    elif tool_name == "anythingllm_query":
        message = tool_args.get('message')
        result = anythingllm_query(message)
    elif tool_name == "list_available_skills":
        result = list_available_skills()
    elif tool_name == "load_skill_content":
        skill_name = tool_args.get('skill_name')
        result = load_skill_content(skill_name)
    else:
        result = json.dumps({"status": "error", "message": f"未知的工具 {tool_name}"}, ensure_ascii=False)
    
    print(f"工具执行结果: {result}")
    return result

# ==================== 链式工具调用实现 ====================

class ChainedCallContext:
    """链式调用上下文管理器，用于在多个工具调用之间传递数据和状态"""
    
    def __init__(self, max_iterations=10):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.call_history = []
        self.variables = {}
        self.final_answer = None
        self.is_completed = False
    
    def add_call(self, tool_name, arguments, result):
        """记录一次工具调用及其结果"""
        self.call_history.append({
            "iteration": self.current_iteration,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": time.time()
        })
    
    def set_variable(self, name, value):
        """设置上下文变量"""
        self.variables[name] = value
    
    def get_variable(self, name, default=None):
        """获取上下文变量"""
        return self.variables.get(name, default)
    
    def increment_iteration(self):
        """增加迭代次数"""
        self.current_iteration += 1
    
    def is_max_iterations_reached(self):
        """检查是否达到最大迭代次数"""
        return self.current_iteration >= self.max_iterations
    
    def mark_completed(self, answer):
        """标记任务完成"""
        self.is_completed = True
        self.final_answer = answer
    
    def get_summary(self):
        """获取调用历史摘要"""
        summary = []
        for call in self.call_history:
            summary.append(f"步骤 {call['iteration']+1}: 调用 {call['tool_name']} -> 成功")
        return "\n".join(summary)

def extract_json_from_response(response_text):
    """从LLM响应中提取JSON部分"""
    if not response_text:
        return None
    
    # 处理 markdown 代码块格式
    if '```json' in response_text:
        start_idx = response_text.find('```json') + 7
        end_idx = response_text.find('```', start_idx)
        if end_idx != -1:
            json_str = response_text[start_idx:end_idx].strip()
        else:
            json_str = response_text[start_idx:].strip()
    elif '```' in response_text:
        start_idx = response_text.find('```') + 3
        end_idx = response_text.find('```', start_idx)
        if end_idx != -1:
            json_str = response_text[start_idx:end_idx].strip()
        else:
            json_str = response_text[start_idx:].strip()
    else:
        json_str = response_text.strip()
    
    # 尝试解析JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def build_analysis_prompt(user_request, context):
    """构建链式调用分析提示词"""
    history_text = ""
    if context.call_history:
        history_text = "已执行的步骤：\n"
        for call in context.call_history:
            history_text += f"步骤 {call['iteration']+1}: 调用工具 '{call['tool_name']}'\n"
            history_text += f"  参数: {json.dumps(call['arguments'], ensure_ascii=False)}\n"
            history_text += f"  结果: {call['result'][:200]}...\n\n"
    
    variables_text = ""
    if context.variables:
        variables_text = "当前上下文变量：\n"
        for key, value in context.variables.items():
            variables_text += f"  {key} = {repr(value)[:50]}\n"
    
    prompt = f"""你是一个智能决策助手，需要根据用户请求和已执行的步骤历史，决定下一步操作。

用户请求：{user_request}

{history_text}

{variables_text}

决策规则：
1. 如果任务已经完成，或者已经获得足够的信息可以直接回答用户，请返回完成状态
2. 如果需要继续调用工具获取更多信息，请选择合适的工具并提供正确的参数
3. 可以使用上下文变量（如前一步的结果）作为当前工具调用的参数
4. 注意工具调用的顺序依赖关系，某些工具的输出可能需要作为其他工具的输入

可用工具列表：
- list_directory(path): 列出指定目录下的所有文件和目录
- read_file(directory, file_name): 读取指定目录下的文件内容
- create_file(directory, file_name, content): 在指定目录下创建新文件并写入内容
- fetch_webpage(url): 访问指定URL的网页并返回内容
- rename_file(directory, old_name, new_name): 修改指定目录下的文件名称
- delete_file(directory, file_name): 删除指定目录下的文件
- search_chat_history(query): 搜索聊天历史记录
- anythingllm_query(message): 访问AnythingLLM文档仓库
- list_available_skills(): 列出所有可用的技能列表
- load_skill_content(skill_name): 加载指定技能的详细内容

输出格式要求：
请严格按照以下JSON格式返回决策：

完成任务时：
{{"done": true, "answer": "最终回答内容"}}

继续调用工具时：
{{"done": false, "tool_call": {{"name": "工具名称", "arguments": {{"参数名": "参数值"}}}}}}

请确保你的响应是有效的JSON格式，不要包含其他内容。"""
    
    return prompt

def execute_chained_tool_call(user_request, tools, max_iterations=10):
    """执行链式工具调用的完整流程"""
    # 初始化上下文
    context = ChainedCallContext(max_iterations=max_iterations)
    
    # 系统提示词
    system_prompt = """你是一个具有链式工具调用能力的AI助手。你的任务是根据用户请求，通过多轮工具调用来完成任务。

链式调用规则：
1. 你可以将前一个工具的输出作为后一个工具的输入参数
2. 每一步调用后，你会收到工具执行结果，需要根据结果决定下一步操作
3. 你可以使用上下文中的变量来存储和传递中间结果
4. 如果任务完成或达到最大迭代次数，请给出最终总结

输出格式：
- 完成任务：{"done": true, "answer": "最终回答内容"}
- 继续调用：{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}"""
    
    for iteration in range(max_iterations):
        print(f"\n=== 链式调用迭代 {iteration + 1}/{max_iterations} ===")
        
        # 构建分析提示词
        analysis_prompt = build_analysis_prompt(user_request, context)
        
        # 调用LLM决定下一步操作
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]
        
        print("正在分析下一步操作...")
        response = call_llm(messages)
        
        if response is None:
            print("LLM响应为空，终止链式调用")
            return "链式调用失败：LLM无响应"
        
        # 解析响应
        try:
            if isinstance(response, dict):
                # 检查是否为工具调用格式
                choice = response.get('choices', [{}])[0]
                message = choice.get('message', {})
                
                # 尝试解析JSON内容
                content = message.get('content', '')
                if content:
                    decision = extract_json_from_response(content)
                else:
                    # 检查是否有tool_calls
                    tool_calls = message.get('tool_calls', [])
                    if tool_calls:
                        tool_call = tool_calls[0]
                        decision = {
                            "done": False,
                            "tool_call": {
                                "name": tool_call.get('function', {}).get('name'),
                                "arguments": tool_call.get('function', {}).get('arguments', {})
                            }
                        }
                    else:
                        decision = None
            else:
                # 响应是字符串，尝试解析为JSON
                decision = extract_json_from_response(response)
            
            if decision is None:
                print("无法解析LLM响应，终止链式调用")
                return "链式调用失败：无法解析LLM响应"
            
            print(f"解析结果: {json.dumps(decision, ensure_ascii=False)}")
            
            # 检查是否完成
            if decision.get('done'):
                answer = decision.get('answer', '')
                context.mark_completed(answer)
                print(f"任务完成！\n最终回答: {answer}")
                return answer
            
            # 继续调用工具
            tool_call = decision.get('tool_call', {})
            tool_name = tool_call.get('name')
            tool_args = tool_call.get('arguments', {})
            
            if not tool_name:
                print("工具名称为空，终止链式调用")
                return "链式调用失败：工具名称为空"
            
            # 执行工具
            result = execute_tool_call({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": tool_args
                }
            })
            
            # 记录到上下文
            context.add_call(tool_name, tool_args, result)
            context.increment_iteration()
            
            # 尝试从结果中提取有用信息存储到上下文变量
            try:
                result_data = json.loads(result)
                if result_data.get('status') == 'success':
                    context.set_variable(f"last_result_{tool_name}", result_data.get('data'))
            except json.JSONDecodeError:
                pass
            
        except Exception as e:
            print(f"执行过程中发生错误: {str(e)}")
            return f"链式调用失败：{str(e)}"
    
    # 达到最大迭代次数
    print(f"达到最大迭代次数 ({max_iterations})，终止链式调用")
    return f"链式调用已达到最大迭代次数({max_iterations})，当前完成的步骤：\n{context.get_summary()}"

def summarize_chat_history(chat_history):
    user_assistant_messages = [msg for msg in chat_history if msg['role'] in ['user', 'assistant']]
    
    if len(user_assistant_messages) <= 2:
        return chat_history
    
    split_point = int(len(user_assistant_messages) * 0.7)
    messages_to_summarize = user_assistant_messages[:split_point]
    messages_to_keep = user_assistant_messages[split_point:]
    
    summary_prompt = "请对以下聊天记录进行总结，提取关键信息和主要内容：\n\n"
    for msg in messages_to_summarize:
        role = "用户" if msg['role'] == 'user' else "助手"
        summary_prompt += f"{role}: {msg['content']}\n\n"
    
    summary_messages = [
        {"role": "system", "content": "你是一个聊天记录总结助手，需要对聊天内容进行简洁明了的总结。"},
        {"role": "user", "content": summary_prompt}
    ]
    
    summary_response = call_llm(summary_messages)
    if summary_response and isinstance(summary_response, dict):
        summary = summary_response.get('choices', [{}])[0].get('message', {}).get('content', '')
    else:
        if isinstance(summary_response, str):
            summary = summary_response
        else:
            summary = "聊天记录总结失败"
    
    new_chat_history = [chat_history[0]]
    new_chat_history.append({"role": "assistant", "content": f"【聊天记录总结】: {summary}"})
    new_chat_history.extend(messages_to_keep)
    
    return new_chat_history

def extract_key_info(chat_history):
    relevant_messages = [msg for msg in chat_history if msg['role'] in ['user', 'assistant'] and not msg.get('content', '').startswith('【聊天记录总结】')]
    
    extract_prompt = "请从以下聊天记录中提取关键信息，按照5W规则（谁Who、做了什么事What、什么时候When、在何处Where、为什么要做这个事Why）提取多条关键信息：\n\n"
    for msg in relevant_messages:
        role = "用户" if msg['role'] == 'user' else "助手"
        extract_prompt += f"{role}: {msg['content']}\n\n"
    
    extract_messages = [
        {"role": "system", "content": "你是一个信息提取助手，需要从聊天记录中按照5W规则提取关键信息。"},
        {"role": "user", "content": extract_prompt}
    ]
    
    extract_response = call_llm(extract_messages)
    if extract_response and isinstance(extract_response, dict):
        key_info = extract_response.get('choices', [{}])[0].get('message', {}).get('content', '')
    else:
        if isinstance(extract_response, str):
            key_info = extract_response
        else:
            key_info = "关键信息提取失败"
    
    log_path = os.getenv('LOG_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log.txt'))
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(key_info)
        f.write("\n")
    
    return key_info

def main():
    load_env()
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "列出指定目录下的所有文件和目录，包括基本属性",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "目录路径"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rename_file",
                "description": "修改指定目录下的文件名称",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "目录路径"
                        },
                        "old_name": {
                            "type": "string",
                            "description": "原文件名"
                        },
                        "new_name": {
                            "type": "string",
                            "description": "新文件名"
                        }
                    },
                    "required": ["directory", "old_name", "new_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_file",
                "description": "删除指定目录下的文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "目录路径"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "文件名"
                        }
                    },
                    "required": ["directory", "file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "在指定目录下创建新文件并写入内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "目录路径"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "文件名"
                        },
                        "content": {
                            "type": "string",
                            "description": "文件内容"
                        }
                    },
                    "required": ["directory", "file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取指定目录下的文件内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "目录路径"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "文件名"
                        }
                    },
                    "required": ["directory", "file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_webpage",
                "description": "访问指定URL的网页并返回内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "网页URL"
                        }
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_chat_history",
                "description": "搜索聊天历史记录，当用户输入以'/search'开头或表达'查找聊天历史'的意思时使用",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "anythingllm_query",
                "description": "访问AnythingLLM文档仓库，当用户提到'文档仓库'、'文件仓库'、'仓库'时使用",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "查询消息"
                        }
                    },
                    "required": ["message"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_available_skills",
                "description": "列出所有可用的技能列表，包括技能名称和描述",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "load_skill_content",
                "description": "加载指定技能的详细内容，当需要使用某个技能时调用此函数",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "技能名称"
                        }
                    },
                    "required": ["skill_name"]
                }
            }
        }
    ]
    
    skills_result = list_available_skills()
    skills_data = json.loads(skills_result)
    skills_info = ""
    if skills_data.get('status') == 'success':
        skills_info = f"\n\n可用技能列表：\n{skills_data.get('data', '')}"
    
    system_prompt = f"""你是一个具有文件操作、网络访问、聊天历史搜索、文档仓库访问、技能调用和链式工具调用能力的AI助手。

链式工具调用规则：
1. 你可以将前一个工具的输出作为后一个工具的输入参数
2. 每一步调用后，你会收到工具执行结果，需要根据结果决定下一步操作
3. 你可以使用上下文中的变量来存储和传递中间结果
4. 如果任务完成或达到最大迭代次数，请给出最终总结

链式调用示例：
- 用户请求："查找目录下的文件并读取内容"
- 第一步：调用 list_directory 获取文件列表
- 第二步：根据列表结果调用 read_file 读取指定文件
- 第三步：总结内容并返回最终答案

可用工具：
1. list_directory(path): 列出指定目录下的所有文件和目录
2. rename_file(directory, old_name, new_name): 修改指定目录下的文件名称
3. delete_file(directory, file_name): 删除指定目录下的文件
4. create_file(directory, file_name, content): 在指定目录下创建新文件并写入内容
5. read_file(directory, file_name): 读取指定目录下的文件内容
6. fetch_webpage(url): 访问指定URL的网页并返回内容
7. search_chat_history(query): 搜索聊天历史记录
8. anythingllm_query(message): 访问AnythingLLM文档仓库
9. list_available_skills(): 列出所有可用的技能列表
10. load_skill_content(skill_name): 加载指定技能的详细内容

当用户请求涉及多步骤操作时，请使用链式工具调用能力，逐步完成任务。{skills_info}

工具使用格式：
- 思考：分析用户需求，确定需要使用的工具和调用顺序
- 工具调用：使用指定的工具函数和参数
- 结果处理：根据工具执行结果决定下一步操作或总结回答

当使用 fetch_webpage 工具获取网页内容后，你可以对内容进行总结，提取关键信息，或根据用户需求进行分析。

当使用 anythingllm_query 工具访问文档仓库后，你可以根据返回的结果向用户提供相关信息。

当使用 load_skill_content 工具加载技能内容后，请严格按照技能要求执行任务，不要偏离技能规范。

输出格式：
- 如果需要继续调用工具，请使用：{{"done": false, "tool_call": {{"name": "工具名称", "arguments": {{"参数名": "参数值"}}}}}}
- 如果任务完成，请使用：{{"done": true, "answer": "最终回答内容"}}"""
    
    chat_history = [
        {"role": "system", "content": system_prompt}
    ]
    
    chat_rounds = 0
    
    print("=== LLM 链式工具调用客户端 ===")
    print("输入消息开始聊天，按 Ctrl+C 退出")
    print("=======================")
    print("支持链式工具调用，可自动进行多步骤操作")
    print()
    print("示例：")
    print("1. 链式文件操作：查找 practice06 目录下所有包含'def'关键词的文件，并总结这些文件的主要内容")
    print("2. 多文件操作：读取 1.txt 和 2.txt，把两个数相加的和写入 result.txt")
    print("3. 网页处理：访问网页并总结内容保存到文件")
    print()
    
    try:
        while True:
            user_input = input("你: ")
            
            if user_input.startswith('/search') or '查找聊天历史' in user_input or '搜索聊天' in user_input:
                if user_input.startswith('/search'):
                    query = user_input[7:].strip()
                else:
                    query = user_input
                
                tool_result = search_chat_history(query)
                result_data = json.loads(tool_result)
                if result_data.get('status') == 'success':
                    search_prompt = result_data.get('data', '')
                    search_messages = [
                        {"role": "system", "content": "你是一个聊天历史查询助手，需要根据聊天历史回答用户的问题。"},
                        {"role": "user", "content": search_prompt}
                    ]
                    print("助手: ", end='', flush=True)
                    search_response = stream_llm(search_messages)
                    if search_response:
                        chat_history.append({"role": "user", "content": user_input})
                        chat_history.append({"role": "assistant", "content": search_response})
                else:
                    print("助手: ", end='', flush=True)
                    print(result_data.get('message', '搜索失败'))
                    chat_history.append({"role": "user", "content": user_input})
                    chat_history.append({"role": "assistant", "content": result_data.get('message', '搜索失败')})
            else:
                chat_history.append({"role": "user", "content": user_input})
                chat_rounds += 1
                
                history_length = sum(len(msg.get('content', '')) for msg in chat_history)
                
                if (chat_rounds >= 5 and chat_rounds % 5 == 0) or history_length > 3000:
                    print("正在总结聊天历史...")
                    chat_history = summarize_chat_history(chat_history)
                
                if chat_rounds % 5 == 0:
                    print("正在提取关键信息...")
                    extract_key_info(chat_history)
                
                print("助手: ", end='', flush=True)
                
                try:
                    response = call_llm(chat_history, tools)
                    
                    if not response:
                        print("请求失败")
                        continue
                except Exception as e:
                    print(f"请求异常: {str(e)}")
                    continue
                
                if isinstance(response, dict):
                    choice = response.get('choices', [{}])[0]
                    message = choice.get('message', {})
                    
                    if message.get('tool_calls'):
                        for tool_call in message.get('tool_calls', []):
                            tool_result = execute_tool_call(tool_call)
                            
                            chat_history.append(message)
                            
                            chat_history.append({
                                "role": "tool",
                                "tool_call_id": tool_call.get('id'),
                                "name": tool_call.get('function', {}).get('name'),
                                "content": json.dumps(tool_result, ensure_ascii=False)
                            })
                        
                        final_response = stream_llm(chat_history)
                        if final_response:
                            chat_history.append({"role": "assistant", "content": final_response})
                    else:
                        content = message.get('content', '')
                        
                        # 检查是否为链式调用格式
                        try:
                            content_json = extract_json_from_response(content)
                            if content_json and isinstance(content_json, dict):
                                if content_json.get('done'):
                                    print(content_json.get('answer', ''))
                                    chat_history.append({"role": "assistant", "content": content})
                                elif content_json.get('tool_call'):
                                    print("开始链式工具调用...")
                                    final_answer = execute_chained_tool_call(user_input, tools)
                                    print(f"链式调用结果: {final_answer}")
                                    chat_history.append({"role": "assistant", "content": final_answer})
                                else:
                                    print(content)
                                    chat_history.append(message)
                            else:
                                print(content)
                                chat_history.append(message)
                        except:
                            print(content)
                            chat_history.append(message)
                else:
                    try:
                        content_json = extract_json_from_response(response)
                        if content_json and isinstance(content_json, dict):
                            if content_json.get('done'):
                                print(content_json.get('answer', ''))
                                chat_history.append({"role": "assistant", "content": response})
                            elif content_json.get('tool_call'):
                                print("开始链式工具调用...")
                                final_answer = execute_chained_tool_call(user_input, tools)
                                print(f"链式调用结果: {final_answer}")
                                chat_history.append({"role": "assistant", "content": final_answer})
                            else:
                                print(response)
                                chat_history.append({"role": "assistant", "content": response})
                        else:
                            print(response)
                            chat_history.append({"role": "assistant", "content": response})
                    except:
                        print(response)
                        chat_history.append({"role": "assistant", "content": response})
            
            print()
    except KeyboardInterrupt:
        print("\n退出工具调用客户端")
        sys.exit(0)

if __name__ == "__main__":
    main()