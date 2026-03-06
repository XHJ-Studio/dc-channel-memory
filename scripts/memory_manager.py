#!/usr/bin/env python3
"""
Discord 群聊记忆管理核心模块
用于按频道分离存储、人员识别和私聊总结
"""

import os
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据目录
BASE_DIR = Path(os.path.expanduser("~/.openclaw/memory/discord"))
CHANNELS_DIR = BASE_DIR / "channels"
IDENTITIES_DIR = BASE_DIR / "identities"
RELATIONSHIPS_DIR = BASE_DIR / "relationships"

# 确保目录存在
CHANNELS_DIR.mkdir(parents=True, exist_ok=True)
IDENTITIES_DIR.mkdir(parents=True, exist_ok=True)
RELATIONSHIPS_DIR.mkdir(parents=True, exist_ok=True)


class DiscordChannelMemory:
    """Discord 频道记忆管理器"""
    
    def __init__(self):
        self.channels_dir = CHANNELS_DIR
        self.identities_dir = IDENTITIES_DIR
        self.relationships_dir = RELATIONSHIPS_DIR
    
    def save_message(self, channel_id: str, message_data: dict):
        """
        保存单条消息到对应频道
        
        Args:
            channel_id: Discord 频道 ID
            message_data: 消息数据字典
        """
        # 创建频道目录
        channel_dir = self.channels_dir / channel_id
        channel_dir.mkdir(exist_ok=True)
        
        # 按日期分文件
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = channel_dir / f"{date_str}.jsonl"
        
        # 追加写入
        with open(file_path, 'a', encoding='utf-8') as f:
            json.dump(message_data, f, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"已保存消息到频道 {channel_id}")
    
    def identify_user(self, user_id: str, username: str, nickname: str = None) -> dict:
        """
        识别或获取用户信息
        
        Args:
            user_id: Discord 用户 ID
            username: 用户名
            nickname: 频道昵称
            
        Returns:
            用户身份信息
        """
        identity_file = self.identities_dir / f"{user_id}.json"
        
        if identity_file.exists():
            # 已存在，读取并更新
            with open(identity_file, 'r', encoding='utf-8') as f:
                identity = json.load(f)
            
            # 更新最后出现时间
            identity['last_seen'] = datetime.now().isoformat()
            identity['username_history'] = list(set(
                identity.get('username_history', []) + [username]
            ))
            
            if nickname:
                identity['nickname_history'] = list(set(
                    identity.get('nickname_history', []) + [nickname]
                ))
            
            # 检查是否需要询问身份
            if identity.get('real_name') is None and not identity.get('asked_identity', False):
                identity['should_ask_identity'] = True
            
        else:
            # 新用户，创建记录
            identity = {
                'user_id': user_id,
                'username': username,
                'nickname': nickname,
                'username_history': [username],
                'nickname_history': [nickname] if nickname else [],
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'real_name': None,
                'role': None,
                'tags': [],
                'notes': '',
                'should_ask_identity': True,
                'asked_identity': False,
                'channels': []
            }
            logger.info(f"发现新用户: {username} ({user_id})")
        
        # 保存
        with open(identity_file, 'w', encoding='utf-8') as f:
            json.dump(identity, f, ensure_ascii=False, indent=2)
        
        return identity
    
    def update_user_identity(self, user_id: str, real_name: str = None, role: str = None, notes: str = None):
        """更新用户身份信息"""
        identity_file = self.identities_dir / f"{user_id}.json"
        
        if not identity_file.exists():
            return False
        
        with open(identity_file, 'r', encoding='utf-8') as f:
            identity = json.load(f)
        
        if real_name:
            identity['real_name'] = real_name
            identity['should_ask_identity'] = False
        
        if role:
            identity['role'] = role
        
        if notes:
            identity['notes'] = notes
        
        identity['asked_identity'] = True
        
        with open(identity_file, 'w', encoding='utf-8') as f:
            json.dump(identity, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_channel_summary(self, channel_id: str, days: int = 7) -> dict:
        """
        获取频道概况（用于私聊查询）
        
        Args:
            channel_id: 频道 ID
            days: 查询最近几天的记录
            
        Returns:
            频道概况信息（不包含具体消息内容）
        """
        channel_dir = self.channels_dir / channel_id
        
        if not channel_dir.exists():
            return {"error": "频道无记录"}
        
        summary = {
            "channel_id": channel_id,
            "period_days": days,
            "total_messages": 0,
            "unique_users": set(),
            "active_hours": {},
            "topics": [],
            "last_activity": None,
            "message_count_trend": [],
            "mentions_count": 0
        }
        
        # 读取最近几天的记录
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            file_path = channel_dir / f"{date_str}.jsonl"
            
            if file_path.exists():
                daily_count = 0
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            msg = json.loads(line.strip())
                            summary['total_messages'] += 1
                            daily_count += 1
                            
                            user_id = msg.get('user_id')
                            if user_id:
                                summary['unique_users'].add(user_id)
                            
                            # 记录活跃时间
                            hour = msg.get('hour', 0)
                            summary['active_hours'][hour] = summary['active_hours'].get(hour, 0) + 1
                            
                            # 检测提及
                            if msg.get('was_mentioned', False):
                                summary['mentions_count'] += 1
                            
                            # 更新最后活动时间
                            if not summary['last_activity'] or msg.get('timestamp', '') > summary['last_activity']:
                                summary['last_activity'] = msg.get('timestamp')
                                
                        except json.JSONDecodeError:
                            continue
                
                summary['message_count_trend'].append({
                    'date': date_str,
                    'count': daily_count
                })
            
            current_date += timedelta(days=1)
        
        # 转换 set 为 list 以便 JSON 序列化
        summary['unique_users'] = list(summary['unique_users'])
        summary['unique_user_count'] = len(summary['unique_users'])
        
        # 找出最活跃的时间段
        if summary['active_hours']:
            peak_hour = max(summary['active_hours'], key=summary['active_hours'].get)
            summary['peak_activity_hour'] = peak_hour
        
        return summary
    
    def get_user_info(self, user_id: str = None, username: str = None) -> Optional[dict]:
        """
        获取用户信息
        
        Args:
            user_id: Discord 用户 ID
            username: 用户名（如果不知道 ID）
        """
        # 先尝试 user_id
        if user_id:
            identity_file = self.identities_dir / f"{user_id}.json"
            if identity_file.exists():
                with open(identity_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        # 尝试通过 username 查找
        if username:
            for identity_file in self.identities_dir.glob("*.json"):
                with open(identity_file, 'r', encoding='utf-8') as f:
                    identity = json.load(f)
                    if username in identity.get('username_history', []) or \
                       username == identity.get('username'):
                        return identity
        
        return None
    
    def list_all_identities(self) -> List[dict]:
        """列出所有已知用户身份"""
        identities = []
        for identity_file in self.identities_dir.glob("*.json"):
            with open(identity_file, 'r', encoding='utf-8') as f:
                identities.append(json.load(f))
        return identities
    
    def get_recent_topics(self, channel_id: str, limit: int = 10) -> List[str]:
        """
        提取近期话题（简化版，实际可使用 NLP）
        
        Args:
            channel_id: 频道 ID
            limit: 返回话题数量
        """
        # 这里可以实现更复杂的主题提取
        # 简单实现：返回最近活跃的日期和消息趋势
        summary = self.get_channel_summary(channel_id, days=7)
        
        topics = []
        if summary.get('total_messages', 0) > 0:
            topics.append(f"近期共有 {summary['total_messages']} 条消息")
            topics.append(f"{summary['unique_user_count']} 人参与讨论")
            
            if summary.get('peak_activity_hour') is not None:
                topics.append(f"活跃高峰在 {summary['peak_activity_hour']}:00 左右")
        
        return topics


# 便捷函数
def save_discord_message(channel_id: str, message_data: dict):
    """便捷函数：保存 Discord 消息"""
    memory = DiscordChannelMemory()
    memory.save_message(channel_id, message_data)


def identify_discord_user(user_id: str, username: str, nickname: str = None):
    """便捷函数：识别 Discord 用户"""
    memory = DiscordChannelMemory()
    return memory.identify_user(user_id, username, nickname)


def get_channel_overview(channel_id: str, days: int = 7):
    """便捷函数：获取频道概况"""
    memory = DiscordChannelMemory()
    return memory.get_channel_summary(channel_id, days)


def get_user_by_username(username: str):
    """便捷函数：通过用户名获取信息"""
    memory = DiscordChannelMemory()
    return memory.get_user_info(username=username)


if __name__ == "__main__":
    # 测试代码
    memory = DiscordChannelMemory()
    
    # 测试保存消息
    test_msg = {
        "message_id": "12345",
        "user_id": "1103263501755105321",
        "username": "小黄鸡工坊",
        "content": "测试消息",
        "timestamp": datetime.now().isoformat(),
        "hour": datetime.now().hour,
        "was_mentioned": True
    }
    memory.save_message("1477961192604569703", test_msg)
    
    # 测试识别用户
    identity = memory.identify_user("1103263501755105321", "小黄鸡工坊")
    print(f"用户身份: {identity}")
    
    # 测试获取频道概况
    summary = memory.get_channel_summary("1477961192604569703", days=1)
    print(f"频道概况: {summary}")
