import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from tool_client import load_env, call_llm, list_available_skills, load_skill_content

def test_scenario_1():
    print("=" * 50)
    print("测试场景1：未指定部门撰写五一节放假通知")
    print("=" * 50)
    
    load_env()
    
    # 获取技能列表
    skills_result = list_available_skills()
    print("技能列表：")
    print(skills_result)
    print()
    
    # 构建测试消息
    messages = [
        {
            "role": "system",
            "content": """你是一个具有技能调用能力的AI助手。当用户请求涉及特定技能或任务时，请先使用 list_available_skills 工具查看可用技能，然后根据用户需求判断是否需要使用某个技能。如果需要使用某个技能，请使用 load_skill_content 工具加载该技能的详细内容，并严格按照技能要求执行任务。"""
        },
        {
            "role": "user",
            "content": "帮我写一个五一节放假的通知"
        }
    ]
    
    # 调用 LLM
    print("发送请求到 LLM...")
    response = call_llm(messages)
    
    if response:
        print("LLM 响应：")
        print(response)
    else:
        print("请求失败")
    
    print()

def test_scenario_2():
    print("=" * 50)
    print("测试场景2：指定销售部撰写五一节放假通知")
    print("=" * 50)
    
    load_env()
    
    # 构建测试消息
    messages = [
        {
            "role": "system",
            "content": """你是一个具有技能调用能力的AI助手。当用户请求涉及特定技能或任务时，请先使用 list_available_skills 工具查看可用技能，然后根据用户需求判断是否需要使用某个技能。如果需要使用某个技能，请使用 load_skill_content 工具加载该技能的详细内容，并严格按照技能要求执行任务。"""
        },
        {
            "role": "user",
            "content": "我是销售部的，帮我写一个五一节放假的通知"
        }
    ]
    
    # 调用 LLM
    print("发送请求到 LLM...")
    response = call_llm(messages)
    
    if response:
        print("LLM 响应：")
        print(response)
    else:
        print("请求失败")
    
    print()

if __name__ == "__main__":
    print("开始测试...")
    print()
    
    # 测试场景1
    test_scenario_1()
    
    # 测试场景2
    test_scenario_2()
    
    print("测试完成！")