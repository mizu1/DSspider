from get_chat_historys_list import main as get_chat_historys_list
from get_chat_historys_list import load_cookie
from chat_historys_list_distinct import main as chat_historys_list_distinct
from get_chat_history_by_json import main as get_chat_history_by_json

authorization,cookie = load_cookie()

get_chat_historys_list(authorization,cookie)
print("=" * 50)
chat_historys_list_distinct()
print("=" * 50)
print("获取具体的对话记录")
print("=" * 50)
get_chat_history_by_json(authorization,cookie)