import json
import os
from datetime import datetime

def remove_duplicate_sessions(input_file=None, output_file=None):
    """
    去除重复的会话记录，基于会话ID去重
    
    Args:
        input_file: 输入的JSON文件路径，如果为None则查找最新的文件
        output_file: 输出的JSON文件路径，如果为None则自动生成
    """
    
    # 如果未指定输入文件，查找最新的会话文件
    if input_file is None:
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        if not json_files:
            print("未找到会话文件，请指定输入文件路径")
            return
        
        # 按修改时间排序，获取最新的文件
        json_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        input_file = json_files[0]
        print(f"自动选择最新文件: {input_file}")
    
    # 如果未指定输出文件，自动生成
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_deduplicated_{timestamp}.json"
    
    try:
        # 读取原始数据
        with open(input_file, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        print(f"原始数据共 {len(sessions)} 条记录")
        
        # 基于会话ID去重
        seen_ids = set()
        unique_sessions = []
        duplicate_count = 0
        
        for session in sessions:
            session_id = session.get('id')
            if session_id not in seen_ids:
                seen_ids.add(session_id)
                unique_sessions.append(session)
            else:
                duplicate_count += 1
                print(f"发现重复会话: {session.get('title', '无标题')} (ID: {session_id})")
        
        print(f"去重后剩余 {len(unique_sessions)} 条唯一记录")
        print(f"移除 {duplicate_count} 条重复记录")
        
        # 按更新时间排序（从新到旧）
        unique_sessions.sort(key=lambda x: x.get('updated_at', 0), reverse=True)
        
        # 保存去重后的数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_sessions, f, ensure_ascii=False, indent=2)
        
        print(f"去重后的数据已保存到: {output_file}")
        
        # 显示统计信息
        analyze_deduplicated_data(unique_sessions)
        
        return output_file
        
    except FileNotFoundError:
        print(f"文件未找到: {input_file}")
    except json.JSONDecodeError:
        print(f"JSON解析错误: {input_file}")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")

def analyze_deduplicated_data(sessions):
    """
    分析去重后的数据
    """
    if not sessions:
        return
    
    print("\n=== 去重后数据分析 ===")
    print(f"唯一对话数: {len(sessions)}")
    
    # 按时间统计
    latest_time = max(s.get('updated_at', 0) for s in sessions)
    earliest_time = min(s.get('updated_at', 0) for s in sessions)
    
    latest_str = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M:%S')
    earliest_str = datetime.fromtimestamp(earliest_time).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"时间范围: {earliest_str} ~ {latest_str}")
    
    # 统计标题类型
    title_types = {}
    for session in sessions:
        title_type = session.get('title_type', 'UNKNOWN')
        title_types[title_type] = title_types.get(title_type, 0) + 1
    
    print("标题类型分布:")
    for title_type, count in title_types.items():
        print(f"  {title_type}: {count}")
    
    # 显示一些示例标题
    print("\n最新的一些对话标题:")
    for i, session in enumerate(sessions[:10]):
        readable_time = datetime.fromtimestamp(session.get('updated_at', 0)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  {i+1}. [{readable_time}] {session.get('title', '无标题')}")

def compare_files(original_file, deduplicated_file):
    """
    比较原始文件和去重文件的差异
    """
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        with open(deduplicated_file, 'r', encoding='utf-8') as f:
            deduplicated_data = json.load(f)
        
        print(f"\n=== 文件比较 ===")
        print(f"原始文件: {original_file} - {len(original_data)} 条记录")
        print(f"去重文件: {deduplicated_file} - {len(deduplicated_data)} 条记录")
        print(f"移除重复: {len(original_data) - len(deduplicated_data)} 条记录")
        
    except Exception as e:
        print(f"比较文件时发生错误: {e}")

def main():
    """
    主函数 - 提供交互式选择
    """
    print("DeepSeek 会话数据去重工具")
    print("=" * 40)
    
    # 查找所有会话文件
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if not json_files:
        print("未找到任何会话文件，请确保JSON文件在当前目录")
        return
    
    # 显示文件列表
    print("找到以下会话文件:")
    for i, file in enumerate(json_files):
        print(f"  {i+1}. {file}")
    
    # 让用户选择文件
    try:
        choice = input(f"\n请选择要处理的文件 (1-{len(json_files)}) [默认1]: ").strip()
        if choice == '':
            choice = 1
        else:
            choice = int(choice)
        
        if choice < 1 or choice > len(json_files):
            print("选择无效")
            return
        
        input_file = json_files[choice - 1]
        
        # 执行去重
        result = remove_duplicate_sessions(input_file=input_file)
        
        if result:
            output_file = result
            
            # 询问是否比较文件
            compare = input("\n是否比较原始文件和去重文件? (y/n) [默认n]: ").strip().lower()
            if compare == 'y' or compare == 'yes':
                compare_files(input_file, output_file)
        
    except ValueError:
        print("请输入有效的数字")
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

if __name__ == "__main__":
    main()