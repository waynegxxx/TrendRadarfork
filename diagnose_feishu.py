# coding=utf-8
"""
飞书通知诊断工具

快速诊断为什么飞书没有收到消息
"""

import os
import sys
from pathlib import Path
import yaml


def check_github_secrets():
    """检查 GitHub Secrets 配置"""
    print("\n" + "=" * 60)
    print("1. 检查 GitHub Secrets 配置")
    print("=" * 60)
    
    feishu_url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    
    if feishu_url:
        print("✅ FEISHU_WEBHOOK_URL 已设置（环境变量）")
        print(f"   URL 前缀: {feishu_url[:50]}...")
        
        # 验证格式
        if feishu_url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/"):
            print("✅ URL 格式正确")
        else:
            print("⚠️  URL 格式可能不正确")
            print("   期望格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx")
    else:
        print("❌ FEISHU_WEBHOOK_URL 未设置（环境变量）")
        print("   请在 GitHub Secrets 中添加 FEISHU_WEBHOOK_URL")
    
    return feishu_url


def check_config_file():
    """检查配置文件"""
    print("\n" + "=" * 60)
    print("2. 检查配置文件")
    print("=" * 60)
    
    config_path = Path("config/config.yaml")
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return None
    
    print(f"✅ 配置文件存在: {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # 检查通知功能
        notification = config.get("notification", {})
        enable_notification = notification.get("enable_notification", True)
        
        if enable_notification:
            print("✅ 通知功能已启用")
        else:
            print("❌ 通知功能已禁用")
            print("   请在 config.yaml 中设置 enable_notification: true")
        
        # 检查推送时间窗口
        push_window = notification.get("push_window", {})
        enabled = push_window.get("enabled", False)
        
        if enabled:
            print("⚠️  推送时间窗口已启用")
            time_range = push_window.get("time_range", {})
            start = time_range.get("start", "")
            end = time_range.get("end", "")
            once_per_day = push_window.get("once_per_day", True)
            
            print(f"   时间窗口: {start} - {end}")
            print(f"   每天只推一次: {once_per_day}")
            print("   如果当前时间不在窗口内，或今天已推送过，将不会发送消息")
        else:
            print("✅ 推送时间窗口未启用（无时间限制）")
        
        # 检查报告模式
        report = config.get("report", {})
        mode = report.get("mode", "daily")
        
        print(f"\n📊 报告模式: {mode}")
        if mode == "incremental":
            print("   ⚠️  增量模式：只有新增新闻时才会推送")
        elif mode == "current":
            print("   ℹ️  当前榜单模式：按时推送当前榜单")
        else:
            print("   ℹ️  当日汇总模式：按时推送当日汇总")
        
        return config
        
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None


def check_keywords_file():
    """检查关键词文件"""
    print("\n" + "=" * 60)
    print("3. 检查关键词配置")
    print("=" * 60)
    
    keywords_path = Path("config/frequency_words.txt")
    
    if not keywords_path.exists():
        print(f"❌ 关键词文件不存在: {keywords_path}")
        return False
    
    print(f"✅ 关键词文件存在: {keywords_path}")
    
    try:
        with open(keywords_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        
        if lines:
            print(f"✅ 找到 {len(lines)} 个关键词")
            print(f"   前5个关键词: {', '.join(lines[:5])}")
        else:
            print("⚠️  关键词文件为空")
            print("   如果没有关键词，将不会匹配任何新闻")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取关键词文件失败: {e}")
        return False


def check_output_files():
    """检查输出文件"""
    print("\n" + "=" * 60)
    print("4. 检查输出文件")
    print("=" * 60)
    
    output_dir = Path("output")
    
    if not output_dir.exists():
        print("⚠️  output 目录不存在")
        print("   可能是首次运行，还没有生成数据")
        return False
    
    # 查找最新的输出文件
    date_dirs = sorted([d for d in output_dir.iterdir() if d.is_dir()], reverse=True)
    
    if date_dirs:
        latest_date = date_dirs[0]
        print(f"✅ 找到输出目录: {latest_date.name}")
        
        txt_dir = latest_date / "txt"
        if txt_dir.exists():
            txt_files = sorted(txt_dir.glob("*.txt"), reverse=True)
            if txt_files:
                latest_file = txt_files[0]
                print(f"✅ 最新输出文件: {latest_file.name}")
                
                # 读取文件内容
                try:
                    with open(latest_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = content.strip().split("\n")
                        print(f"   文件行数: {len(lines)}")
                        
                        if len(lines) > 0:
                            print("   前3行内容:")
                            for i, line in enumerate(lines[:3], 1):
                                print(f"     {i}. {line[:80]}...")
                except Exception as e:
                    print(f"   ⚠️  读取文件失败: {e}")
            else:
                print("⚠️  没有找到 txt 文件")
        else:
            print("⚠️  txt 目录不存在")
    else:
        print("⚠️  output 目录为空")
        print("   可能是首次运行，还没有生成数据")
    
    return True


def generate_summary(feishu_url, config):
    """生成诊断总结"""
    print("\n" + "=" * 60)
    print("📋 诊断总结")
    print("=" * 60)
    
    issues = []
    suggestions = []
    
    # 检查 Webhook URL
    if not feishu_url:
        issues.append("❌ FEISHU_WEBHOOK_URL 未设置")
        suggestions.append("   1. 访问 GitHub 仓库 Settings → Secrets → Actions")
        suggestions.append("   2. 添加 FEISHU_WEBHOOK_URL Secret")
        suggestions.append("   3. 填入你的飞书 Webhook URL")
    else:
        if not feishu_url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/"):
            issues.append("⚠️  Webhook URL 格式可能不正确")
            suggestions.append("   1. 确认 Webhook URL 格式正确")
            suggestions.append("   2. 重新创建飞书机器人获取新的 URL")
    
    # 检查通知功能
    if config:
        notification = config.get("notification", {})
        if not notification.get("enable_notification", True):
            issues.append("❌ 通知功能已禁用")
            suggestions.append("   在 config.yaml 中设置 enable_notification: true")
        
        push_window = notification.get("push_window", {})
        if push_window.get("enabled", False):
            issues.append("⚠️  推送时间窗口已启用")
            suggestions.append("   检查当前时间是否在时间窗口内")
            suggestions.append("   检查今天是否已经推送过（如果 once_per_day: true）")
    
    if issues:
        print("发现以下问题：")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n💡 建议：")
        for suggestion in suggestions:
            print(f"  {suggestion}")
    else:
        print("✅ 配置检查通过")
        print("\n💡 如果仍然没有收到消息，请：")
        print("   1. 查看 GitHub Actions 日志，查找错误信息")
        print("   2. 运行 test_feishu_webhook.py 测试 Webhook")
        print("   3. 检查飞书群聊中机器人是否正常")
        print("   4. 确认是否有匹配的新闻（检查关键词配置）")


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 飞书通知诊断工具")
    print("=" * 60)
    print("\n正在检查配置...")
    
    # 检查 GitHub Secrets
    feishu_url = check_github_secrets()
    
    # 检查配置文件
    config = check_config_file()
    
    # 检查关键词文件
    check_keywords_file()
    
    # 检查输出文件
    check_output_files()
    
    # 生成总结
    generate_summary(feishu_url, config)
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    print("\n📚 更多帮助：")
    print("   - 查看「飞书通知排查指南.md」获取详细排查步骤")
    print("   - 运行 test_feishu_webhook.py 测试 Webhook")
    print("   - 查看 GitHub Actions 日志获取详细错误信息")


if __name__ == "__main__":
    main()

