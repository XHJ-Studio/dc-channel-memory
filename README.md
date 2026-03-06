# DC 群聊记忆 🧠

智能管理 Discord 群聊记忆，按频道分离存储，支持人员识别和私聊总结查询。

## ✨ 功能特性

- 📁 **按频道分离存储** - 每个 Discord 频道独立的记忆目录，便于长期管理
- 👤 **人员识别系统** - 自动记录用户 ID 和名称映射，支持标注真实姓名和角色
- 🔍 **私聊总结查询** - 私聊时可安全查询群聊概况，不泄露具体对话内容
- 📊 **智能分析** - 自动统计消息趋势、活跃时间、参与人数

## 🚀 快速开始

### 安装

```bash
cd ~/.openclaw/skills
git clone https://github.com/XHJ-Studio/dc-channel-memory.git
cd dc-channel-memory
pip3 install -r requirements.txt
```

### 配置

在 `~/.openclaw/openclaw.json` 中添加：

```json5
{
  skills: {
    entries: {
      discord_channel_memory: {
        enabled: true
      }
    }
  }
}
```

### 使用示例

在 OpenClaw 对话中：

```
# 查询频道概况
查看频道 1477961192604569703 的概况

# 查询用户信息
用户 小黄鸡工坊 是谁？
```

## 📖 详细文档

### 命令行工具

```bash
# 查询频道概况
python3 scripts/query_memory.py --channel <channel_id> --summary --days 7

# 查询用户信息（支持用户名或用户ID）
python3 scripts/query_memory.py --user <username>

# 列出所有已知用户
python3 scripts/query_memory.py --list-users
```

### Python API

```python
from scripts.memory_manager import DiscordChannelMemory

# 初始化
memory = DiscordChannelMemory()

# 保存消息
memory.save_message('channel_id', {
    'message_id': '12345',
    'user_id': '67890',
    'username': '用户名',
    'content': '消息内容',
    'timestamp': '2026-03-06T12:00:00',
    'hour': 12,
    'was_mentioned': False
})

# 识别/获取用户信息
identity = memory.identify_user('67890', '用户名', '频道昵称')

# 更新用户身份
memory.update_user_identity('67890', real_name='真实姓名', role='角色', notes='备注')

# 获取频道概况
summary = memory.get_channel_summary('channel_id', days=7)

# 获取用户信息
user = memory.get_user_info(user_id='67890')
```

## 📁 数据存储结构

```
~/.openclaw/memory/discord/
├── channels/              # 频道消息记录
│   └── <channel_id>/
│       └── YYYY-MM-DD.jsonl    # 每日消息（JSON Lines 格式）
├── identities/            # 用户身份信息
│   └── <user_id>.json         # 用户身份档案
└── relationships/         # 关系图谱（预留扩展）
    └── channel-<channel_id>.json
```

### 消息记录格式

```json
{
  "message_id": "1479403049658220645",
  "user_id": "1103263501755105321",
  "username": "小黄鸡工坊",
  "content": "消息内容",
  "timestamp": "2026-03-06T17:33:31",
  "hour": 17,
  "was_mentioned": false
}
```

### 用户身份格式

```json
{
  "user_id": "1103263501755105321",
  "username": "小黄鸡工坊",
  "nickname": "老板",
  "username_history": ["小黄鸡工坊"],
  "real_name": "真实姓名",
  "role": "角色",
  "tags": [],
  "notes": "备注信息",
  "first_seen": "2026-03-06T17:33:41",
  "last_seen": "2026-03-06T17:33:41"
}
```

## 🔒 隐私说明

- ✅ 所有数据存储在本地，不上传任何云端服务
- ✅ 私聊查询只返回概况统计，不展示具体消息内容
- ✅ 用户可随时删除自己的身份记录
- ✅ 支持配置数据保留期限

## 🛠️ 开发计划

- [ ] 自动监听 Discord 消息并保存
- [ ] 自动检测新人并询问身份
- [ ] 定期自动总结频道话题
- [ ] 消息内容语义分析和主题提取
- [ ] 用户关系图谱可视化

## 🤝 贡献

欢迎提交 PR 和 Issue！

## 📄 许可证

MIT License © 小黄鸡工坊
