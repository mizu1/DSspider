# DeepSeek 对话记录爬虫工具
## 功能简介
一个用于获取 DeepSeek 对话记录的爬虫工具，能够提取用户的会话历史列表和具体的对话内容。

### 使用方法
1. ### 获取认证信息：

    登录 DeepSeek 官网

    打开浏览器开发者工具（Network 面板）

    寻找包含 history_messages?chat_session_id 或 fetch_page?lte_cursor.pinned 的请求

    复制请求中的 authorization 和 cookie 信息

    运行工具：

    ```bash
    python pipeline.py
    ````
    将获取的 authorization 和 cookie 粘贴到控制台

    按照提示完成后续操作

### 运行流程
### 第一步：获取会话历史列表

执行 get_chat_historys_list 模块

提取用户的所有会话历史记录

保存为 JSON 文件供后续使用

### 注意：由于 DeepSeek 网页端采用分页加载机制，基于时间戳进行分页，可能导致部分记录重复爬取。

### 第二步：数据去重处理

运行 chat_historys_list_distinct.py 模块

自动删除重复记录

生成去重后的历史记录列表 JSON 文件

第三步：提取具体对话内容

运行 get_chat_history_by_json.py 模块

从历史记录列表中获取各会话的 session_id

访问接口获取完整对话内容：

```text
https://chat.deepseek.com/api/v0/chat/history_messages?chat_session_id={session_id}
```
### 模块说明

pipeline.py - 主执行流程

get_chat_historys_list - 会话列表获取

chat_historys_list_distinct.py - 数据去重处理

get_chat_history_by_json.py - 具体对话内容提取
