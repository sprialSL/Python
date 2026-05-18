import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from tool_client import list_available_skills, load_skill_content

def test_list_skills():
    print("=" * 50)
    print("测试1：获取技能列表")
    print("=" * 50)
    
    result = list_available_skills()
    data = json.loads(result)
    
    if data.get('status') == 'success':
        print("✓ 技能列表获取成功")
        print(f"技能列表：{data.get('data', '')}")
        
        # 解析技能列表
        skills_json = json.loads(data.get('data', '{}'))
        skills = skills_json.get('skills', [])
        print(f"\n找到 {len(skills)} 个技能：")
        for skill in skills:
            print(f"  - {skill['name']}: {skill['description']}")
    else:
        print(f"✗ 技能列表获取失败：{data.get('message')}")
    
    print()

def test_load_skill():
    print("=" * 50)
    print("测试2：加载 notice 技能内容")
    print("=" * 50)
    
    result = load_skill_content('notice')
    data = json.loads(result)
    
    if data.get('status') == 'success':
        print("✓ 技能内容加载成功")
        print(f"\n技能内容：\n{data.get('data', '')}")
    else:
        print(f"✗ 技能内容加载失败：{data.get('message')}")
    
    print()

def test_invalid_skill():
    print("=" * 50)
    print("测试3：加载不存在的技能")
    print("=" * 50)
    
    result = load_skill_content('nonexistent')
    data = json.loads(result)
    
    if data.get('status') == 'error':
        print(f"✓ 正确处理了不存在的技能：{data.get('message')}")
    else:
        print("✗ 未能正确处理不存在的技能")
    
    print()

if __name__ == "__main__":
    print("开始测试技能系统...")
    print()
    
    test_list_skills()
    test_load_skill()
    test_invalid_skill()
    
    print("=" * 50)
    print("测试完成！")
    print("=" * 50)