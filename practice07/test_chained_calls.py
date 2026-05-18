import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tool_client import load_env, execute_chained_tool_call

# 定义工具列表
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
    }
]

def test_scenario_1():
    """测试1：文件搜索链式调用"""
    print("=" * 60)
    print("测试场景1：文件搜索链式调用")
    print("=" * 60)
    print("用户请求：查找 practice06 目录下所有文件，并总结这些文件的主要内容")
    print()
    
    # 获取 practice06 目录路径
    practice06_path = os.path.join(os.path.dirname(__file__), '..', 'practice06')
    user_request = f"查找 {practice06_path} 目录下所有文件，并总结这些文件的主要内容"
    
    print(f"目标目录: {practice06_path}")
    print()
    
    # 执行链式调用
    result = execute_chained_tool_call(user_request, tools, max_iterations=10)
    
    print()
    print("测试结果：")
    print(result)
    print()

def test_scenario_2():
    """测试2：多文件操作"""
    print("=" * 60)
    print("测试场景2：多文件操作")
    print("=" * 60)
    print("用户请求：读取 1.txt 和 2.txt 两个文件，文件内容都是正整数，把两个数相加的和写入 result.txt 文件")
    print()
    
    # 获取当前目录路径
    current_dir = os.path.dirname(__file__)
    user_request = f"读取 {current_dir}\\1.txt 和 {current_dir}\\2.txt 两个文件，文件内容都是正整数，把两个数相加的和写入 result.txt 文件"
    
    print(f"当前目录: {current_dir}")
    print()
    
    # 执行链式调用
    result = execute_chained_tool_call(user_request, tools, max_iterations=10)
    
    print()
    print("测试结果：")
    print(result)
    print()
    
    # 验证结果文件
    result_file = os.path.join(current_dir, 'result.txt')
    if os.path.exists(result_file):
        with open(result_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        print(f"result.txt 内容: {content}")
    else:
        print("result.txt 文件未创建")
    print()

def test_scenario_3():
    """测试3：网页处理链式调用"""
    print("=" * 60)
    print("测试场景3：网页处理链式调用")
    print("=" * 60)
    print("用户请求：访问网页并总结页面内容，保存到 practice07/summary.txt")
    print()
    
    # 获取当前目录路径
    current_dir = os.path.dirname(__file__)
    user_request = f"访问 `https://www.nsu.edu.cn/HTML/news/2024/06/article_3974.html` 并总结页面内容，保存到 {current_dir}/summary.txt"
    
    print()
    
    # 执行链式调用
    result = execute_chained_tool_call(user_request, tools, max_iterations=10)
    
    print()
    print("测试结果：")
    print(result)
    print()
    
    # 验证结果文件
    summary_file = os.path.join(current_dir, 'summary.txt')
    if os.path.exists(summary_file):
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"summary.txt 文件已创建，内容长度: {len(content)} 字符")
        print("文件内容预览：")
        print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print("summary.txt 文件未创建")
    print()

if __name__ == "__main__":
    print("加载环境变量...")
    load_env()
    print()
    
    print("开始链式工具调用测试...")
    print()
    
    # 测试场景1
    test_scenario_1()
    
    # 测试场景2
    test_scenario_2()
    
    # 测试场景3
    test_scenario_3()
    
    print("所有测试完成！")