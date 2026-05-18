# Practice 06 - 技能调用系统

## 项目简介

本项目基于 practice05 的 tool_client.py，实现了一个技能调用系统，允许 LLM 动态加载和使用预定义的技能来处理特定任务。

## 主要功能

### 1. 技能列表读取 (`list_available_skills`)

自动读取 `.agents/skills` 目录下的所有技能，解析每个技能的 YAML front matter，提取技能名称和描述。

**功能特点：**
- 自动扫描 `.agents/skills` 目录下的一级子目录
- 解析每个子目录中的 `SKILL.md` 文件
- 提取 YAML front matter 中的 `name` 和 `description` 字段
- 返回 JSON 格式的技能列表

**返回格式：**
```json
{
  "skills": [
    {
      "name": "技能名称",
      "description": "技能描述"
    }
  ]
}
```

### 2. 技能内容加载 (`load_skill_content`)

当 LLM 判断需要使用某个技能时，通过此函数加载该技能的详细内容。

**功能特点：**
- 根据技能名称加载对应的 `SKILL.md` 文件
- 提取 YAML front matter 之后的正文内容
- 返回技能的详细使用说明和规则

### 3. 系统提示词集成

在启动时自动获取技能列表，并将技能信息嵌入到系统提示词中，使 LLM 能够了解可用的技能。

**系统提示词增强：**
```
当用户请求涉及特定技能或任务时，请先使用 list_available_skills 工具查看可用技能，然后根据用户需求判断是否需要使用某个技能。如果需要使用某个技能，请使用 load_skill_content 工具加载该技能的详细内容，并按照技能要求执行任务。

可用技能列表：
{
  "skills": [
    {
      "name": "notice",
      "description": "用于撰写、修改、润色各类通知的技能..."
    }
  ]
}
```

## 项目结构

```
practice06/
├── .agents/
│   └── skills/
│       └── notice/
│           └── SKILL.md          # 通知撰写技能
├── tool_client.py                # 主程序
├── test_simple.py                # 简单测试脚本
├── test_skills.py                # 完整测试脚本
├── .env                          # 环境配置文件
└── README.md                     # 项目文档
```

## 技能文件格式

技能文件使用 Markdown 格式，包含 YAML front matter 和正文内容。

**示例：**
```markdown
---
name: notice
description: 用于撰写、修改、润色各类通知的技能。
---

# 通知撰写技能

## 使用场景
当用户要求撰写、修改或润色通知类文档时使用此技能。

## 规则要求
1. **标题格式**：通知不能以"通知"二字开头，必须冠以"XX部"的前缀
2. **部门处理**：
   - 如果用户明确告知所在部门，使用用户指定的部门名称
   - 如果用户没有告知所在部门，使用"XX部"代替
```

## 使用方法

### 1. 配置环境变量

复制 `.env` 文件并填写正确的 API 配置：

```bash
BASE_URL=https://api.openai.com/v1
API_KEY=sk-your-api-key-here
MODEL=gpt-3.5-turbo
```

### 2. 运行主程序

```bash
python tool_client.py
```

### 3. 测试技能系统

运行简单测试：

```bash
python test_simple.py
```

运行完整测试：

```bash
python test_skills.py
```

## 测试结果

### 测试场景1：未指定部门撰写五一节放假通知

**用户输入：**
```
帮我写一个五一节放假的通知
```

**预期输出：**
```
XX部通知

五一节放假安排如下...
```

**测试结果：** ✓ 通过

### 测试场景2：指定销售部撰写五一节放假通知

**用户输入：**
```
我是销售部的，帮我写一个五一节放假的通知
```

**预期输出：**
```
销售部通知

五一节放假安排如下...
```

**测试结果：** ✓ 通过

## 技能系统工作流程

1. **启动时**：程序自动读取 `.agents/skills` 目录下的所有技能
2. **用户输入**：用户提交请求
3. **技能识别**：LLM 根据用户请求判断是否需要使用某个技能
4. **技能加载**：如果需要，调用 `load_skill_content` 加载技能详细内容
5. **任务执行**：LLM 按照技能要求执行任务
6. **结果输出**：返回符合技能规范的输出结果

## 新增工具函数

### list_available_skills()

列出所有可用的技能列表。

**参数：** 无

**返回：** JSON 格式的技能列表

### load_skill_content(skill_name)

加载指定技能的详细内容。

**参数：**
- `skill_name`: 技能名称

**返回：** JSON 格式的技能内容

## 与 practice05 的区别

| 功能 | practice05 | practice06 |
|------|-----------|-----------|
| 文件操作 | ✓ | ✓ |
| 网络访问 | ✓ | ✓ |
| 聊天历史搜索 | ✓ | ✓ |
| 文档仓库访问 | ✓ | ✓ |
| 技能列表读取 | ✗ | ✓ |
| 技能内容加载 | ✗ | ✓ |
| YAML front matter 解析 | ✗ | ✓ |

## 依赖项

- Python 3.6+
- PyYAML
- 其他依赖同 practice05

## 安装依赖

```bash
pip install pyyaml
```

## 注意事项

1. 技能文件必须放在 `.agents/skills` 目录下的一级子目录中
2. 每个技能目录必须包含 `SKILL.md` 文件
3. YAML front matter 必须使用 `---` 标记
4. 技能名称和描述字段为必填项
5. 确保 `.env` 文件配置正确

## 未来改进方向

1. 支持技能的动态热加载
2. 添加技能版本管理
3. 实现技能之间的依赖关系
4. 支持技能参数化配置
5. 添加技能执行日志记录

## 作者

Practice 06 教学项目

## 许可证

MIT License