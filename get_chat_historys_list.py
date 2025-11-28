import requests
import json
import time
import datetime

def fetch_all_chat_sessions(authorization,cookie):
    """
    获取所有历史对话会话，使用正确的分页机制
    """
    all_sessions = []
    page_count = 0
    max_pages = 1000  # 安全限制，防止无限循环
    
    # 初始URL
    base_url = "https://chat.deepseek.com/api/v0/chat_session/fetch_page"
    params = {
        "lte_cursor.pinned": "false"
    }
    
    headers = {
        "authorization": authorization,
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
        "x-client-platform": "web",
        "x-client-version": "1.5.0"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    print("开始获取历史对话列表...")
    
    while page_count < max_pages:
        try:
            print(f"正在获取第 {page_count + 1} 页...")
            
            response = session.get(
                url=base_url,
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"请求失败，状态码: {response.status_code}")
                break
                
            data = response.json()
            
            # 检查返回的数据结构
            if 'data' not in data or 'biz_data' not in data['data']:
                print("返回数据格式异常，停止爬取")
                break
                
            biz_data = data['data']['biz_data']
            
            if 'chat_sessions' not in biz_data:
                print("没有chat_sessions字段，停止爬取")
                break
                
            sessions = biz_data['chat_sessions']
            has_more = biz_data.get('has_more', False)
            
            if not sessions:
                print("没有更多数据，爬取完成")
                break
                
            # 添加到总列表
            all_sessions.extend(sessions)
            
            print(f"本页获取到 {len(sessions)} 条对话记录")
            print(f"has_more: {has_more}")
            
            # 如果没有更多数据，停止爬取
            if not has_more:
                print("没有更多数据，爬取完成")
                break
            
            # 获取最后一个会话的updated_at作为下一页的光标
            if sessions:
                last_session = sessions[-1]
                next_cursor = last_session.get('updated_at')
                
                if next_cursor is None:
                    print("无法找到下一页光标，爬取完成")
                    break
                    
                # 更新参数，准备请求下一页
                params["lte_cursor.updated_at"] = next_cursor
                
                # 显示时间戳对应的人类可读时间
                readable_time = datetime.datetime.fromtimestamp(next_cursor).strftime('%Y-%m-%d %H:%M:%S')
                print(f"下一页光标时间戳: {next_cursor} ({readable_time})")
            
            page_count += 1
            
            # 随机延迟 1-3 秒
            delay = 1 + (time.time() % 2)  # 1-3秒的随机延迟
            print(f"等待 {delay:.1f} 秒后继续...")
            time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"JSON解析异常: {e}")
            break
        except Exception as e:
            print(f"未知异常: {e}")
            break
    
    print(f"爬取完成，共获取 {len(all_sessions)} 条对话记录，{page_count} 页")
    return all_sessions

def save_to_json(data, filename=None):
    """
    保存数据到JSON文件
    """
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deepseek_chat_sessions_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到: {filename}")
def load_cookie():
    authorization = input("粘贴你的authorization:")
    cookie = input("粘贴你的cookie:")
    return authorization,cookie

def main(authorization,cookie):
    """
    主函数
    """
    try:

        # 获取所有对话会话
        all_sessions = fetch_all_chat_sessions(authorization,cookie)
        
        if all_sessions:
            # 保存到JSON文件
            save_to_json(all_sessions,"deepseek_chat_list.json")
        else:
            print("没有获取到任何数据")
            
    except KeyboardInterrupt:
        print("\n用户中断爬取")
    except Exception as e:
        print(f"程序异常: {e}")

if __name__ == "__main__":
    authorization,cookie = load_cookie()
    main(authorization,cookie)