# Practice04 实验报告

## 1. 实验目的

本次实验的主要目的是：
- 学习如何在聊天客户端中集成外部文档仓库访问功能
- 掌握使用subprocess模块调用curl命令访问API的方法
- 了解AnythingLLM文档仓库的API调用方式
- 学习如何处理API认证和错误处理
- 掌握如何在聊天客户端中添加新的工具调用功能

## 2. 实验内容

### 2.1 主要功能实现

1. **基础聊天功能**：
   - 终端界面输入输出
   - 流式输出LLM响应
   - 聊天历史记录管理
   - 聊天记录自动总结和压缩

2. **AnythingLLM文档仓库访问**：
   - 使用subprocess模块调用curl命令
   - 访问AnythingLLM的聊天API接口
   - 使用API密钥进行认证
   - 处理API响应和错误情况

3. **触发机制**：
   - 当用户输入以`/anything`开头时触发
   - 当用户提到"文档仓库"、"文件仓库"或"仓库"时触发

### 2.2 核心代码实现

#### 2.2.1 AnythingLLM查询函数

```python
def anythingllm_query(message, api_key, workspace_slug):
    """
    使用subprocess模块调用curl命令，访问AnythingLLM的聊天API接口
    
    Args:
        message: 要发送的查询消息
        api_key: AnythingLLM的API密钥
        workspace_slug: AnythingLLM的工作区slug
    
    Returns:
        从AnythingLLM返回的响应内容
    """
    # 构建API URL - 使用正确的路径格式
    url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
    
    # 构建请求数据
    payload = json.dumps({
        "message": message
    })
    
    # 构建curl命令
    curl_command = [
        "curl",
        "-X", "POST",
        url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", payload
    ]
    
    try:
        # 执行curl命令
        print("正在访问AnythingLLM API...")
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 检查命令是否成功执行
        if result.returncode == 0:
            # 解析响应
            try:
                response_data = json.loads(result.stdout)
                return json.dumps({"status": "success", "data": response_data}, ensure_ascii=False)
            except json.JSONDecodeError:
                return json.dumps({"status": "error", "message": f"响应解析失败: {result.stdout}"}, ensure_ascii=False)
        else:
            return json.dumps({"status": "error", "message": f"curl命令执行失败: {result.stderr}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
```

#### 2.2.2 触发机制实现

```python
# 检查是否需要调用AnythingLLM查询
need_anythingllm = False
anythingllm_keywords = ["文档仓库", "文件仓库", "仓库"]
# 检查用户输入是否以/anything开头
if user_input.startswith("/anything"):
    need_anythingllm = True
else:
    # 检查用户输入是否包含相关关键词
    for keyword in anythingllm_keywords:
        if keyword in user_input:
            need_anythingllm = True
            break
```

#### 2.2.3 响应处理

```python
if need_anythingllm and anythingllm_api_key and anythingllm_workspace_slug:
    # 调用AnythingLLM查询
    anythingllm_response = anythingllm_query(user_input, anythingllm_api_key, anythingllm_workspace_slug)
    
    # 解析AnythingLLM响应
    try:
        response_data = json.loads(anythingllm_response)
        if response_data.get("status") == "success":
            anythingllm_content = json.dumps(response_data.get("data", {}), ensure_ascii=False, indent=2)
        else:
            anythingllm_content = response_data.get("message", "查询失败")
    except json.JSONDecodeError:
        anythingllm_content = anythingllm_response
    
    # 构建包含AnythingLLM响应的消息
    anythingllm_messages = [
        {"role": "system", "content": "你是一个有帮助的AI助手。请根据AnythingLLM返回的信息，为用户提供详细的回答。"},
        {"role": "user", "content": f"用户请求: {user_input}\n\n从文档仓库获取的信息:\n{anythingllm_content}"}
    ]
    
    print("AI: ", end="", flush=True)
    
    # 调用API获取响应
    content, stats = call_llm_api_stream(
        base_url=base_url,
        api_key=api_key,
        model=model,
        messages=anythingllm_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
```

## 3. 实验结果

### 3.1 环境配置

成功配置了以下环境变量：
- `ANYTHINGLLM_API_KEY`: N7RJRS2-DHEM7MW-JKKVTCG-8C2PGGB
- `ANYTHINGLLM_WORKSPACE_SLUG`: new

### 3.2 功能测试

1. **启动测试**：
   - 成功加载配置文件
   - 显示配置信息，包括AnythingLLM API密钥和工作区配置

2. **正常聊天**：
   - 成功与LLM进行多轮对话
   - 支持流式输出
   - 当聊天超过5轮时自动压缩聊天历史

3. **AnythingLLM文档仓库访问**：
   - 当输入`/anything 有多少个文件`时，成功调用API
   - 当输入`文档仓库有多少个文件`时，成功触发API调用
   - 能够正确处理API响应

4. **错误处理**：
   - 当工作区配置错误时，能够显示错误信息
   - 当API调用失败时，能够捕获并显示错误

### 3.3 测试输出示例

```
正在加载配置文件: e:\ruanjian\23000\Documents\Python\.env

配置信息:
  - Base URL: http://127.0.0.1:1234/v1
  - Model: google/gemma-4-e4b
  - Temperature: 0.3
  - Max Tokens: 8192
  - AnythingLLM API Key: 已配置
  - AnythingLLM Workspace Slug: new

欢迎使用终端聊天客户端！
输入消息后按回车发送，按 Ctrl+C 退出。
当聊天超过5轮或上下文长度超过3k时，系统会自动总结和压缩聊天记录。
每五次聊天，系统会自动提取关键信息并记录到本地文件。
使用 '/search' 开头或表达 '查找聊天历史' 可以查询历史聊天记录。
当提到 '文档仓库'、'文件仓库' 或 '仓库' 时，系统会自动查询AnythingLLM文档仓库。

你: 文档仓库有多少个文件
正在访问AnythingLLM API...
AI: 我需要查询文档仓库来获取文件数量信息。

根据从文档仓库获取的信息，我可以看到：

**当前工作区：new**

在这个工作区中，系统成功识别到了仓库的存在，并且能够正常访问。

关于文件数量的具体信息，从返回的数据中可以看出，系统已经成功连接到了工作区，但是具体的文件数量信息可能需要进一步查询。

如果你需要更详细的文件列表或数量统计，请告诉我，我可以帮你进行更具体的查询。
==================================================
LLM API 调用统计报告 (流式输出)
==================================================

时间统计:
  - 首Token延迟: 0.67 秒
  - 生成时间: 2.34 秒
  - 总耗时: 3.01 秒

Token 统计:
  - 估算Token数: 120

速度统计:
  - 生成速度: 51.28 tokens/秒

响应内容长度: 450 字符
==================================================
```

## 4. 实验总结

### 4.1 实验成功点

1. **功能实现**：成功实现了AnythingLLM文档仓库访问功能，包括API调用、认证和响应处理。

2. **触发机制**：实现了两种触发方式，用户可以通过命令或关键词触发文档仓库查询。

3. **错误处理**：添加了完善的错误处理机制，能够处理API调用失败、响应解析失败等情况。

4. **集成性**：将AnythingLLM功能无缝集成到现有的聊天客户端中，保持了代码的模块化和可维护性。

### 4.2 技术要点

1. **subprocess模块**：学习了如何使用subprocess模块调用外部命令，特别是curl命令。

2. **API认证**：掌握了如何在API调用中使用Bearer token进行认证。

3. **JSON处理**：学习了如何构建JSON请求数据和解析JSON响应。

4. **错误处理**：了解了如何处理各种可能的错误情况，提高了代码的健壮性。

5. **工具集成**：学习了如何在聊天客户端中添加新的工具调用功能，扩展了客户端的能力。

### 4.3 应用前景

1. **知识管理**：通过集成AnythingLLM文档仓库，可以方便地查询和管理文档内容。

2. **信息检索**：用户可以通过自然语言查询文档仓库中的信息，提高信息获取效率。

3. **智能助手**：结合LLM和文档仓库，可以构建更智能的助手，能够回答基于文档内容的问题。

4. **系统集成**：这种集成方式可以推广到其他类似的API服务，扩展聊天客户端的功能。

### 4.4 改进方向

1. **性能优化**：可以考虑使用requests库替代subprocess调用curl，提高API调用性能。

2. **缓存机制**：添加缓存机制，避免重复查询相同的内容，提高响应速度。

3. **多工作区支持**：增加多工作区切换功能，支持查询不同的文档仓库。

4. **更丰富的查询功能**：扩展查询功能，支持更复杂的文档操作，如上传、修改文档等。

5. **用户界面优化**：可以考虑添加更友好的用户界面，如彩色输出、进度显示等。

## 5. 结论

本次实验成功实现了在聊天客户端中集成AnythingLLM文档仓库访问功能，通过使用subprocess模块调用curl命令，实现了对AnythingLLM API的访问和认证。实验过程中遇到了工作区配置错误的问题，通过查询API获取正确的工作区信息并进行配置，最终成功解决了问题。

通过本次实验，我们学习了如何在Python中调用外部API，如何处理API认证和错误，以及如何将外部服务集成到聊天客户端中。这些技术对于构建功能丰富的LLM应用具有重要意义。