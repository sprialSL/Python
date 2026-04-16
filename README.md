# Python 实践项目

## 项目结构

```
Python/
├── practice01/
│   └── llm_client.py        # 使用 Python 标准库调用 OpenAI 兼容 API
├── practice02/
│   ├── chat_client.py       # 终端界面聊天客户端
│   └── tool_calling_client.py # 工具调用客户端
├── practice03/
│   └── chat_client.py       # 带聊天记录总结和压缩功能的终端界面聊天客户端
├── .env.example             # 环境变量示例文件
├── .gitignore               # Git 忽略文件配置
└── requirements.txt         # 项目依赖
```

## 代码功能和教学目标

### practice01/llm_client.py

#### 功能
1. 读取 .env 配置文件
2. 使用 http.client 调用 LLM API
3. 支持流式输出（Streaming）
4. 统计 token 消耗、时间、首token延迟和速度

#### 教学目标
1. 学习如何使用 Python 标准库（http.client）调用 OpenAI 兼容 API
2. 了解如何处理流式输出（Streaming）
3. 学习如何统计 API 调用的性能指标
4. 了解如何读取和解析配置文件
5. 学习如何构建 API 请求路径
6. 掌握 HTTP 请求的基本原理和实现

#### 主要函数
- `load_env(env_path)`: 手动解析 .env 文件
- `build_request_path(base_url)`: 构建 API 请求路径
- `call_llm_api_stream()`: 使用流式方式调用 LLM API
- `call_llm_api_normal()`: 使用非流式方式调用 LLM API
- `print_stream_statistics()`: 打印流式输出统计信息
- `print_normal_statistics()`: 打印非流式输出统计信息

### practice02/chat_client.py

#### 功能
1. 支持终端界面输入聊天内容
2. 支持流式输出
3. 支持历史聊天记录自动添加到上下文
4. 直到用户ctrl+c退出终端，否则一直循环

#### 教学目标
1. 学习如何实现终端交互界面
2. 了解如何处理用户输入和程序退出（Ctrl+C）
3. 学习如何维护聊天历史上下文
4. 掌握循环结构和异常处理
5. 了解如何在实际应用中使用 LLM API

#### 主要函数
- `load_env(env_path)`: 手动解析 .env 文件
- `build_request_path(base_url)`: 构建 API 请求路径
- `call_llm_api_stream()`: 使用流式方式调用 LLM API
- `print_stream_statistics()`: 打印流式输出统计信息

### practice02/tool_calling_client.py

#### 功能
1. 列出某个目录下有哪些文件（包括文件的基本属性、大小等信息）
2. 修改某个目录下某个文件的名字
3. 删除某个目录下的某个文件
4. 在某个目录下新建1个文件，并且写入内容
5. 读取某个目录下的某个文件的内容
6. 通过curl访问网页并返回网页内容
7. 将这些工具调用的能力作为系统提示词发送给LLM，实现工具调用

#### 教学目标
1. 学习如何实现工具调用功能
2. 了解如何设计系统提示词以支持工具调用
3. 学习如何解析和执行工具调用
4. 掌握文件操作的基本方法
5. 了解如何在实际应用中集成工具调用能力

#### 主要函数
- `load_env(env_path)`: 手动解析 .env 文件
- `build_request_path(base_url)`: 构建 API 请求路径
- `call_llm_api_stream()`: 使用流式方式调用 LLM API
- `print_stream_statistics()`: 打印流式输出统计信息
- `list_files(directory)`: 列出目录下的文件
- `rename_file(directory, old_name, new_name)`: 修改文件名
- `delete_file(directory, filename)`: 删除文件
- `create_file(directory, filename, content)`: 创建文件并写入内容
- `read_file(directory, filename)`: 读取文件内容
- `curl(url)`: 通过curl访问网页并返回网页内容
- `execute_tool_call(tool_call)`: 执行工具调用

### practice03/chat_client.py

#### 功能
1. 支持终端界面输入聊天内容
2. 支持流式输出
3. 支持历史聊天记录自动添加到上下文
4. 当聊天超过5轮或上下文长度超过3k时，自动触发聊天记录总结和压缩
5. 对于前70%左右的内容进行压缩，最后30%左右的内容保留原文
6. 每五次聊天提取一次关键信息，按照5W规则（谁who、做了什么事what、什么时候when（可选）、在何处where（可选）、为什么要做这个事why（可选））进行提取
7. 将提取的关键信息记录到用户主目录下的chat-log\log.txt文件中（如果文件和目录不存在就新建）
8. 直到用户ctrl+c退出终端，否则一直循环

#### 教学目标
1. 学习如何实现聊天记录的总结和压缩功能
2. 了解如何判断聊天历史是否需要压缩
3. 学习如何分割聊天记录并进行部分总结
4. 掌握非流式API调用的实现
5. 了解如何在实际应用中优化上下文管理
6. 学习如何从聊天记录中提取关键信息
7. 掌握文件操作和目录创建的基本方法
8. 了解如何实现增量记录功能

#### 主要函数
- `load_env(env_path)`: 手动解析 .env 文件
- `build_request_path(base_url)`: 构建 API 请求路径
- `call_llm_api_stream()`: 使用流式方式调用 LLM API
- `call_llm_api()`: 使用非流式方式调用 LLM API（用于生成总结和提取关键信息）
- `print_stream_statistics()`: 打印流式输出统计信息
- `summarize_chat_history()`: 总结聊天历史记录
- `should_compress_chat_history()`: 判断是否需要压缩聊天历史
- `compress_chat_history()`: 压缩聊天历史记录
- `extract_key_information()`: 从聊天记录中提取关键信息
- `record_key_information()`: 记录关键信息到本地文件

## 如何运行

### 运行 practice01/llm_client.py
1. 复制 `.env.example` 文件为 `.env`
2. 编辑 `.env` 文件，填写相关配置信息
3. 运行 `python practice01/llm_client.py`

### 运行 practice02/chat_client.py
1. 复制 `.env.example` 文件为 `.env`（如果还没有）
2. 编辑 `.env` 文件，填写相关配置信息
3. 运行 `python practice02/chat_client.py`
4. 在终端中输入消息并按回车发送
5. 按 Ctrl+C 退出程序

### 运行 practice02/tool_calling_client.py
1. 复制 `.env.example` 文件为 `.env`（如果还没有）
2. 编辑 `.env` 文件，填写相关配置信息
3. 运行 `python practice02/tool_calling_client.py`
4. 在终端中输入消息并按回车发送
5. 当需要执行文件操作时，AI会生成工具调用
6. 按 Ctrl+C 退出程序

### 运行 practice03/chat_client.py
1. 复制 `.env.example` 文件为 `.env`（如果还没有）
2. 编辑 `.env` 文件，填写相关配置信息
3. 运行 `python practice03/chat_client.py`
4. 在终端中输入消息并按回车发送
5. 当聊天超过5轮或上下文长度超过3k时，系统会自动总结和压缩聊天记录
6. 按 Ctrl+C 退出程序

## 环境变量配置

```
# .env 文件示例
OPENAI_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=qwen/qwen3-4b-2507
TEMPERATURE=0.7
MAX_TOKENS=4096
USE_STREAM=true
```
