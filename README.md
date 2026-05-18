# LLM开发实践课仓库

本仓库是LLM（大语言模型）开发实践课的代码仓库，包含了一系列实践项目，从基础的API调用到复杂的工具调用和文档仓库访问。

## 目录结构

```
├── practice01/          # 基础LLM API调用实践
├── practice02/          # 工具调用基础实践
├── practice03/          # 文件操作和网络访问工具实践
├── practice04/          # 聊天历史管理实践
├── practice05/          # AnythingLLM文档仓库访问实践
├── practice06/          # 技能调用系统实践
├── practice07/          # 链式工具调用实践
├── tools/               # 工具文件
├── .env                 # 环境变量配置文件
├── log.txt              # 聊天历史和关键信息日志
└── README.md            # 项目说明文件
```

## 子目录说明

### practice01 - 基础LLM API调用实践

**文件说明**：
- `chat_client.py`：实现流式调用LLM API的聊天客户端，支持多轮对话，实时显示模型响应
- `llm_client.py`：实现单次调用LLM API并统计性能指标，包括执行时间和Token使用情况
- `prompt01.txt`：系统提示词配置文件

**功能**：
- 基于HTTP协议的LLM API调用
- 流式和非流式两种API调用方式
- 环境变量配置和管理
- 简单的命令行聊天客户端
- LLM响应的性能指标分析

### practice02 - 工具调用基础实践

**文件说明**：
- `tool_client.py`：实现基础的工具调用功能，包括简单的工具定义和调用流程
- `prompt02.txt`：系统提示词配置文件

**功能**：
- 工具调用的基础实现
- 简单的工具定义和执行
- 工具调用流程的基本框架

### practice03 - 文件操作和网络访问工具实践

**文件说明**：
- `tool_client.py`：实现文件操作和网络访问工具的客户端
- `prompt03.txt`：系统提示词配置文件

**功能**：
- 文件操作工具：列出目录内容、重命名文件、删除文件、创建文件、读取文件
- 网络访问工具：访问网页并返回内容
- 完整的工具调用流程实现
- 命令行交互界面

### practice04 - 聊天历史管理实践

**文件说明**：
- `tool_client.py`：扩展了聊天历史管理功能的客户端
- `prompt04.txt`：系统提示词配置文件

**功能**：
- 聊天历史搜索工具：搜索历史聊天记录
- 聊天历史总结：自动总结冗长的聊天历史
- 关键信息提取：按照5W规则提取聊天中的关键信息
- 聊天历史长度和轮数的监控

### practice05 - AnythingLLM文档仓库访问实践

**文件说明**：
- `tool_client.py`：扩展了AnythingLLM文档仓库访问功能的客户端
- `prompt05.txt`：系统提示词配置文件

**功能**：
- AnythingLLM文档仓库访问工具：访问文档仓库，查询仓库中的文件和内容
- 使用subprocess模块调用curl命令
- API认证和中文编码处理
- 完善的错误处理机制

### practice06 - 技能调用系统实践

**文件说明**：
- `tool_client.py`：实现技能调用系统的客户端，支持动态加载和使用预定义技能
- `test_simple.py`：简单测试脚本，测试技能列表读取和技能内容加载功能
- `test_skills.py`：完整测试脚本，测试LLM调用技能的完整流程
- `.env`：环境变量配置文件
- `.agents/skills/notice/SKILL.md`：通知撰写技能定义文件

**功能**：
- `list_available_skills()`：自动读取`.agents/skills`目录下的所有技能，解析YAML front matter
- `load_skill_content(skill_name)`：加载指定技能的详细内容
- 动态技能列表加载：启动时自动获取技能列表并嵌入系统提示词
- 技能调用集成：LLM可以根据用户请求自动选择和使用合适的技能
- YAML front matter解析：支持技能元数据的提取和管理

**技能系统工作流程**：
1. 启动时：程序自动读取`.agents/skills`目录下的所有技能
2. 用户输入：用户提交请求
3. 技能识别：LLM根据用户请求判断是否需要使用某个技能
4. 技能加载：如果需要，调用`load_skill_content`加载技能详细内容
5. 任务执行：LLM按照技能要求执行任务
6. 结果输出：返回符合技能规范的输出结果

### practice07 - 链式工具调用实践

**文件说明**：
- `tool_client.py`：实现链式工具调用功能的客户端，支持多步骤工具调用和上下文管理
- `test_simple_chained.py`：简单测试脚本，测试链式调用上下文管理器和JSON解析功能
- `test_chained_calls.py`：完整测试脚本，测试三个链式调用场景
- `1.txt`：测试数据文件（包含数字42）
- `2.txt`：测试数据文件（包含数字100）

**功能**：
- `ChainedCallContext`类：链式调用上下文管理器，记录每一步的调用和结果，存储中间变量供后续步骤使用，设置最大迭代次数防止无限循环
- `build_analysis_prompt()`：构建分析提示词，包含用户请求、已执行步骤历史、决策规则和JSON输出格式要求
- `execute_chained_tool_call()`：执行链式工具调用的完整流程，支持最大迭代次数限制
- `extract_json_from_response()`：从LLM响应中提取JSON部分，支持markdown代码块格式
- 链式调用规则：前一个工具的输出可以作为后一个工具的输入参数

**链式调用工作流程**：
1. 初始化：创建链式调用上下文，设置最大迭代次数
2. 循环调用：最多迭代max_iterations次
   - 构建分析提示词（包含用户请求和已执行步骤）
   - 调用LLM决定下一步操作
   - 解析LLM响应（支持JSON格式和tool_calls格式）
   - 如果任务完成，返回最终回答
   - 如果需继续调用，执行工具并记录到上下文
3. 结束：返回最终结果

**输出格式**：
- 完成任务：`{"done": true, "answer": "最终回答内容"}`
- 继续调用：`{"done": false, "tool_call": {"name": "工具名称", "arguments": {"参数名": "参数值"}}}`

**测试场景**：
1. 文件搜索链式调用：查找目录下所有文件并总结内容
2. 多文件操作：读取两个文件内容，将数字相加后写入结果文件
3. 网页处理链式调用：访问网页并总结内容保存到文件

## 环境配置

本项目使用`.env`文件管理环境变量，包括：

- `BASE_URL`：LLM API的基础URL
- `MODEL`：使用的LLM模型
- `API_KEY`：LLM API的认证密钥
- `TEMPERATURE`：生成文本的温度参数
- `MAX_TOKENS`：最大生成Token数
- `ANYTHINGLLM_API_KEY`：AnythingLLM的API密钥
- `ANYTHINGLLM_WORKSPACE_SLUG`：AnythingLLM的工作区slug

## 使用方法

1. 配置`.env`文件，填写相应的API密钥和配置参数
2. 进入相应的practice目录，运行`python tool_client.py`或`python chat_client.py`
3. 按照提示输入消息，与AI助手进行交互

## 工具列表

| 工具名称 | 描述 | 所在目录 |
|---------|------|---------|
| `list_directory` | 列出指定目录下的所有文件和目录，包括基本属性 | practice03, practice04, practice05 |
| `rename_file` | 修改指定目录下的文件名称 | practice03, practice04, practice05 |
| `delete_file` | 删除指定目录下的文件 | practice03, practice04, practice05 |
| `create_file` | 在指定目录下创建新文件并写入内容 | practice03, practice04, practice05 |
| `read_file` | 读取指定目录下的文件内容 | practice03, practice04, practice05 |
| `fetch_webpage` | 访问指定URL的网页并返回内容 | practice03, practice04, practice05 |
| `search_chat_history` | 搜索聊天历史记录 | practice04, practice05 |
| `anythingllm_query` | 访问AnythingLLM文档仓库 | practice05 |
| `list_available_skills` | 读取.agents/skills目录下的所有技能列表 | practice06 |
| `load_skill_content` | 加载指定技能的详细内容 | practice06 |
| `ChainedCallContext` | 链式调用上下文管理器，管理多步骤工具调用的状态和数据传递 | practice07 |
| `execute_chained_tool_call` | 执行链式工具调用的完整流程 | practice07 |
| `build_analysis_prompt` | 构建链式调用分析提示词 | practice07 |

## 技术栈

- Python 3.12+
- HTTP/HTTPS客户端
- JSON处理
- 命令行交互
- Subprocess模块
- 环境变量管理

## 实验报告

每个practice目录下都有对应的实验报告，详细记录了实验目的、过程、结果和总结：

- `practice01/practice01实验报告.md`
- `practice02/practice02实验报告.md`
- `practice03/practice03实验报告.md`
- `practice04/practice04实验报告.md`
- `practice05/practice05实验报告.md`
- `practice06/practice06实验报告.md`
- `practice07/practice07实验报告.md`

## 总结

本仓库通过一系列实践项目，逐步构建了一个功能丰富的LLM应用，从基础的API调用到复杂的工具调用和文档仓库访问，展示了LLM应用开发的完整流程和技术要点。通过这些实践，我们学习了：

- LLM API的调用方法（流式和非流式）
- 工具调用的设计和实现
- 文件操作和网络访问
- 聊天历史管理和分析
- 外部服务的集成（如AnythingLLM）
- 技能调用系统的设计和实现
- YAML front matter解析和技能元数据管理
- 动态技能加载和系统提示词集成

- 链式工具调用的设计和实现：支持多步骤工具调用，前一个工具的输出可以作为后一个工具的输入参数
- 上下文管理器的设计：管理调用状态和中间变量
- JSON格式解析和响应处理：支持多种响应格式

这些技术和经验为构建更加智能、功能丰富的LLM应用奠定了基础。
