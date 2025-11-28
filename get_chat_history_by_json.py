import requests
import json
import time
import os
import random
from datetime import datetime

def load_session_ids(json_file):
    """
    从JSON文件中加载所有会话ID
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            sessions = json.load(f)
        
        session_ids = []
        for session in sessions:
            if 'id' in session:
                session_ids.append({
                    'id': session['id'],
                    'title': session.get('title', '无标题'),
                    'updated_at': session.get('updated_at', 0)
                })
        
        print(f"从 {json_file} 中加载了 {len(session_ids)} 个会话ID")
        return session_ids
    
    except Exception as e:
        print(f"加载会话文件失败: {e}")
        return []

def fetch_chat_history(session_id, headers, delay=2):
    """
    获取单个会话的对话历史
    """
    url = f"https://chat.deepseek.com/api/v0/chat/history_messages?chat_session_id={session_id}"
    
    try:
        # 随机延迟，避免请求过于频繁
        time.sleep(delay + random.uniform(0, 1))
        
        response = requests.get(
            url=url,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"请求失败，会话ID: {session_id}, 状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求异常，会话ID: {session_id}, 错误: {e}")
        return None
    except Exception as e:
        print(f"处理异常，会话ID: {session_id}, 错误: {e}")
        return None

def save_progress(progress_file, completed_ids, failed_ids):
    """
    保存爬取进度
    """
    progress = {
        'completed_ids': completed_ids,
        'failed_ids': failed_ids,
        'last_update': datetime.now().isoformat()
    }
    
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def load_progress(progress_file):
    """
    加载爬取进度
    """
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    return {'completed_ids': [], 'failed_ids': []}

def fetch_all_chat_histories(session_ids, output_dir, headers, delay,resume=True,):
    """
    获取所有会话的对话历史
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 进度文件路径
    progress_file = os.path.join(output_dir, 'progress.json')
    
    # 加载进度
    if resume:
        progress = load_progress(progress_file)
        completed_ids = set(progress.get('completed_ids', []))
        failed_ids = set(progress.get('failed_ids', []))
        print(f"从进度文件恢复: 已完成 {len(completed_ids)} 个, 失败 {len(failed_ids)} 个")
    else:
        completed_ids = set()
        failed_ids = set()
    
    # 过滤已完成的会话
    remaining_sessions = []
    for session in session_ids:
        if session['id'] not in completed_ids and session['id'] not in failed_ids:
            remaining_sessions.append(session)
    
    print(f"需要爬取 {len(remaining_sessions)} 个会话的历史记录")
    
    # 爬取对话历史
    all_histories = {}
    total_count = len(remaining_sessions)
    
    for i, session in enumerate(remaining_sessions):
        session_id = session['id']
        session_title = session['title']
        
        print(f"[{i+1}/{total_count}] 爬取会话: {session_title} (ID: {session_id})")
        
        # 获取对话历史
        history = fetch_chat_history(session_id, headers,delay)
        
        if history is not None:
            # 保存到总字典中
            all_histories[session_id] = {
                'session_info': session,
                'history_data': history
            }
            
            # 同时保存为单独的文件
            session_file = os.path.join(output_dir, f"{session_id}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            completed_ids.add(session_id)
            print(f"  ✓ 成功保存对话历史")
        else:
            failed_ids.add(session_id)
            print(f"  ✗ 获取失败")
        
        # 每10个会话保存一次进度
        if (i + 1) % 10 == 0:
            save_progress(progress_file, list(completed_ids), list(failed_ids))
            print(f"已保存进度，完成 {len(completed_ids)} 个会话")
    
    # 最终保存进度
    save_progress(progress_file, list(completed_ids), list(failed_ids))
    
    # 保存所有历史记录到一个文件
    if all_histories:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_histories_file = os.path.join(output_dir, f"all_chat_histories_{timestamp}.json")
        
        with open(all_histories_file, 'w', encoding='utf-8') as f:
            json.dump(all_histories, f, ensure_ascii=False, indent=2)
        
        print(f"所有对话历史已保存到: {all_histories_file}")
    
    return list(completed_ids), list(failed_ids)

def get_session_file():
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
        choice = input(f"\n请选择含有历史会话id的文件 (1-{len(json_files)}) [默认1]: ").strip()
        if choice == '':
            choice = 1
        else:
            choice = int(choice)
        
        if choice < 1 or choice > len(json_files):
            print("选择无效")
            return
        
        input_file = json_files[choice - 1]

    except ValueError:
        print("请输入有效的数字")
    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
    return input_file


def load_cookie():
    authorization = input("粘贴你的authorization:")
    cookie = input("粘贴你的cookie:")
    return authorization,cookie

def main(authorization,cookie):
    """
    主函数
    """
    # 配置
    SESSION_FILE = get_session_file()  
    OUTPUT_DIR = "chat_histories"
    
    # 请求头

    headers = {
        "authorization": authorization,
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
        "x-client-platform": "web",
        "x-client-version": "1.5.0"
    }
    
    print("DeepSeek 对话历史爬取工具")
    print("=" * 50)
    
    # 加载会话ID
    session_ids = load_session_ids(SESSION_FILE)
    if not session_ids:
        print("没有找到可用的会话ID，请检查文件路径和格式")
        return
    
    # 确认开始爬取
    confirm = input(f"即将爬取 {len(session_ids)} 个会话的对话历史，确认开始? (y/n): ").strip().lower()
    if confirm != 'y' and confirm != 'yes':
        print("取消操作")
        return
    
    # 设置延迟时间（秒）
    delay = float(input("设置请求延迟时间（秒，建议2-5秒）: ").strip() or "2")
    
    # 开始爬取
    start_time = time.time()
    
    try:
        completed_ids, failed_ids = fetch_all_chat_histories(
            session_ids=session_ids,
            output_dir=OUTPUT_DIR,
            headers=headers,
            delay=delay,
            resume=True  # 支持断点续传
        )
        
        # 显示统计信息
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("\n" + "=" * 50)
        print("爬取完成!")
        print(f"总会话数: {len(session_ids)}")
        print(f"成功爬取: {len(completed_ids)}")
        print(f"失败: {len(failed_ids)}")
        print(f"总耗时: {elapsed_time:.2f} 秒")
        print(f"平均每个会话: {elapsed_time/len(session_ids):.2f} 秒")
        
        # 显示失败会话
        if failed_ids:
            print(f"\n失败的会话ID:")
            for failed_id in failed_ids:
                print(f"  - {failed_id}")
        
    except KeyboardInterrupt:
        print("\n用户中断爬取")
        print("进度已保存，可以重新运行脚本继续爬取")
    except Exception as e:
        print(f"爬取过程中发生错误: {e}")

if __name__ == "__main__":
    authorization,cookie = load_cookie()
    main(authorization,cookie)