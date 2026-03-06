---
name: dc_channel_memory
description: DC 群聊记忆 - Discord 频道分离存储、人员识别、私聊总结查询
metadata: { "openclaw": { "emoji": "🧠", "homepage": "https://github.com/XHJ-Studio/dc-channel-memory", "requires": { "bins": ["python3"] }, "primaryEnv": "DC_CHANNEL_MEMORY_ENABLED" } }
---

# DC 群聊记忆 🧠

智能管理 Discord 群聊记忆，按频道分离存储，支持人员识别和私聊总结查询。

## 功能特性

- 📁 **按频道分离存储** - 每个 Discord 频道有独立的记忆目录
- 👤 **人员识别系统** - 自动记录用户身份，支持真实姓名和角色标注
- 🔍 **私聊总结查询** - 私聊时可查询群聊概况，不泄露具体对话内容
- 📊 **智能分析** - 消息趋势、活跃时间、参与人数统计

## 安装

### 1. 克隆技能

```bash
cd ~/.openclaw/skills
git clone https://github.com/XHJ-Studio/discord-channel-memory.git
```

### 2. 安装依赖

```bash
cd discord-channel-memory
pip3 install -r requirements.txt
```

### 3. 配置环境变量（可选）

```bash
export DISCORD_CHANNEL_MEMORY_ENABLED=true
```

或在 `~/.openclaw/openclaw.json` 中配置：

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

## 使用方法

### 方式 1：作为工具调用

在 OpenClaw 对话中使用：

```
# 保存消息到指定频道
使用 discord_channel_memory 保存消息 频道ID:1477961192604569703 用户ID:12345 内容:测试消息

# 查询频道概况
查看频道 1477961192604569703 的概况

# 查询用户信息
用户 小黄鸡工坊 是谁？
```

### 方式 2：命令行工具

```bash
# 查询频道概况
python3 scripts/query_memory.py --channel 1477961192604569703 --summary

# 查询用户信息
python3 scripts/query_memory.py --user 用户名

# 列出所有用户
python3 scripts/query_memory.py --list-users
```

## 数据存储

数据默认存储在：
```
~/.openclaw/memory/discord/
├── channels/              # 频道消息记录
│   └── <channel_id>/
│       └── YYYY-MM-DD.jsonl
├── identities/            # 用户身份信息
│   └── <user_id>.json
└── relationships/         # 关系图谱（预留）
```

## 隐私说明

- 所有数据存储在本地，不上传云端
- 私聊查询只返回概况统计，不展示具体消息内容
- 用户可删除自己的身份记录

## 版本

v1.0.0 - 初始版本

## 许可证

MIT License
