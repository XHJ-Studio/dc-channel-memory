#!/usr/bin/env python3
"""
Discord 频道记忆查询工具
用于私聊中查询群聊概况
"""

import sys
import argparse
from memory_manager import DiscordChannelMemory


def format_summary(summary: dict) -> str:
    """格式化频道概况为易读文本"""
    if 'error' in summary:
        return f"❌ {summary['error']}"
    
    lines = []
    lines.append(f"📊 频道概况（最近 {summary['period_days']} 天）")
    lines.append(f"   总消息数: {summary['total_messages']}")
    lines.append(f"   参与人数: {summary['unique_user_count']} 人")
    
    if summary.get('last_activity'):
        lines.append(f"   最后活动: {summary['last_activity'][:16]}")
    
    if summary.get('peak_activity_hour') is not None:
        lines.append(f"   活跃高峰: {summary['peak_activity_hour']}:00")
    
    if summary['mentions_count'] > 0:
        lines.append(f"   提及次数: {summary['mentions_count']}")
    
    # 消息趋势
    if summary.get('message_count_trend'):
        lines.append("\n📈 消息趋势:")
        for day in summary['message_count_trend'][-5:]:  # 最近5天
            lines.append(f"   {day['date']}: {day['count']} 条")
    
    return "\n".join(lines)


def format_user_info(user_info: dict) -> str:
    """格式化用户信息"""
    if not user_info:
        return "❌ 未找到该用户信息"
    
    lines = []
    lines.append(f"👤 用户信息")
    lines.append(f"   Discord ID: {user_info['user_id']}")
    lines.append(f"   用户名: {user_info['username']}")
    
    if user_info.get('real_name'):
        lines.append(f"   真实姓名: {user_info['real_name']} ✅")
    else:
        lines.append(f"   真实姓名: 未知 ❓")
    
    if user_info.get('role'):
        lines.append(f"   身份角色: {user_info['role']}")
    
    if user_info.get('notes'):
        lines.append(f"   备注: {user_info['notes']}")
    
    # 历史名称
    if len(user_info.get('username_history', [])) > 1:
        lines.append(f"\n   曾用名: {', '.join(user_info['username_history'])}")
    
    # 首次和最后出现
    lines.append(f"\n   首次出现: {user_info.get('first_seen', '未知')[:10]}")
    lines.append(f"   最后出现: {user_info.get('last_seen', '未知')[:10]}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Discord 频道记忆查询工具')
    parser.add_argument('--channel', '-c', help='频道 ID')
    parser.add_argument('--user', '-u', help='查询用户（用户名或 ID）')
    parser.add_argument('--days', '-d', type=int, default=7, help='查询天数（默认7天）')
    parser.add_argument('--list-users', action='store_true', help='列出所有已知用户')
    parser.add_argument('--summary', '-s', action='store_true', help='显示频道概况')
    
    args = parser.parse_args()
    
    memory = DiscordChannelMemory()
    
    # 查询频道概况
    if args.channel and args.summary:
        summary = memory.get_channel_summary(args.channel, args.days)
        print(format_summary(summary))
        return
    
    # 查询用户信息
    if args.user:
        user_info = memory.get_user_info(
            user_id=args.user if args.user.isdigit() else None,
            username=args.user if not args.user.isdigit() else None
        )
        print(format_user_info(user_info))
        return
    
    # 列出所有用户
    if args.list_users:
        users = memory.list_all_identities()
        print(f"📋 已知用户列表（共 {len(users)} 人）\n")
        for user in users:
            real_name = user.get('real_name') or '未知'
            username = user.get('username', '未知')
            print(f"   • {username} ({real_name})")
        return
    
    # 默认帮助
    parser.print_help()


if __name__ == "__main__":
    main()
