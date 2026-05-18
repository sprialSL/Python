"""简单测试链式调用功能，模拟LLM响应"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from tool_client import ChainedCallContext, build_analysis_prompt, extract_json_from_response, execute_tool_call

def test_chained_call_context():
    """测试链式调用上下文管理器"""
    print("=" * 60)
    print("测试 ChainedCallContext 类")
    print("=" * 60)
    
    context = ChainedCallContext(max_iterations=5)
    
    # 测试添加调用记录
    context.add_call("list_directory", {"path": "/test"}, '{"status": "success", "data": ["file1.txt", "file2.txt"]}')
    context.add_call("read_file", {"directory": "/test", "file_name": "file1.txt"}, '{"status": "success", "data": "Hello World"}')
    context.increment_iteration()
    
    # 测试变量存储
    context.set_variable("file_list", ["file1.txt", "file2.txt"])
    context.set_variable("content", "Hello World")
    
    # 测试获取变量
    print(f"file_list: {context.get_variable('file_list')}")
    print(f"content: {context.get_variable('content')}")
    print(f"不存在的变量: {context.get_variable('nonexistent', 'default')}")
    
    # 测试调用历史摘要
    print("\n调用历史摘要:")
    print(context.get_summary())
    
    # 测试完成标记
    context.mark_completed("任务完成！")
    print(f"\n任务已完成: {context.is_completed}")
    print(f"最终答案: {context.final_answer}")
    
    print()

def test_extract_json():
    """测试JSON提取功能"""
    print("=" * 60)
    print("测试 extract_json_from_response 函数")
    print("=" * 60)
    
    # 测试带代码块的响应
    response1 = '```json\n{"done": true, "answer": "测试完成"}```'
    result1 = extract_json_from_response(response1)
    print(f"输入1 (带代码块): {response1}")
    print(f"输出1: {result1}")
    print()
    
    # 测试纯JSON响应
    response2 = '{"done": false, "tool_call": {"name": "list_directory", "arguments": {"path": "/test"}}}'
    result2 = extract_json_from_response(response2)
    print(f"输入2 (纯JSON): {response2}")
    print(f"输出2: {result2}")
    print()
    
    # 测试带其他内容的响应
    response3 = '我需要调用工具。\n```json\n{"done": false, "tool_call": {"name": "read_file", "arguments": {"file": "test.txt"}}}\n```\n请执行。'
    result3 = extract_json_from_response(response3)
    print(f"输入3 (带其他内容): {response3}")
    print(f"输出3: {result3}")
    print()

def test_tool_execution():
    """测试工具执行功能"""
    print("=" * 60)
    print("测试 execute_tool_call 函数")
    print("=" * 60)
    
    # 测试列出目录
    result1 = execute_tool_call({
        "type": "function",
        "function": {
            "name": "list_directory",
            "arguments": {"path": os.path.dirname(__file__)}
        }
    })
    print(f"list_directory 结果: {json.loads(result1)['status']}")
    print()
    
    # 测试读取文件
    result2 = execute_tool_call({
        "type": "function",
        "function": {
            "name": "read_file",
            "arguments": {"directory": os.path.dirname(__file__), "file_name": "1.txt"}
        }
    })
    print(f"read_file 结果: {json.loads(result2)['status']}")
    data = json.loads(result2)
    if data['status'] == 'success':
        print(f"文件内容: {data['data']}")
    print()
    
    # 测试创建文件
    result3 = execute_tool_call({
        "type": "function",
        "function": {
            "name": "create_file",
            "arguments": {"directory": os.path.dirname(__file__), "file_name": "test_output.txt", "content": "测试内容"}
        }
    })
    print(f"create_file 结果: {json.loads(result3)['status']}")
    print()

def test_prompt_building():
    """测试提示词构建功能"""
    print("=" * 60)
    print("测试 build_analysis_prompt 函数")
    print("=" * 60)
    
    context = ChainedCallContext()
    context.add_call("list_directory", {"path": "/test"}, '{"status": "success", "data": ["file1.txt"]}')
    context.set_variable("files", ["file1.txt"])
    context.increment_iteration()
    
    prompt = build_analysis_prompt("读取文件内容并总结", context)
    print("构建的提示词（前500字符）:")
    print(prompt[:500])
    print()

if __name__ == "__main__":
    print("开始简单测试链式调用功能...")
    print()
    
    # 测试上下文管理器
    test_chained_call_context()
    
    # 测试JSON提取
    test_extract_json()
    
    # 测试工具执行
    test_tool_execution()
    
    # 测试提示词构建
    test_prompt_building()
    
    print("所有简单测试完成！")