# coding=utf-8
"""
测试飞书 Webhook 是否有效

使用方法：
1. 设置环境变量：export FEISHU_WEBHOOK_URL="你的Webhook URL"
2. 或者直接修改下面的 webhook_url 变量
3. 运行：python test_feishu_webhook.py
"""

import os
import requests
import json
from typing import Optional


def test_feishu_webhook(webhook_url: Optional[str] = None) -> bool:
    """
    测试飞书 Webhook
    
    Args:
        webhook_url: Webhook URL，如果为 None 则从环境变量读取
    
    Returns:
        是否测试成功
    """
    if not webhook_url:
        webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    
    if not webhook_url:
        print("❌ 错误: 未提供 Webhook URL")
        print("   请设置环境变量 FEISHU_WEBHOOK_URL 或直接修改代码中的 webhook_url 变量")
        return False
    
    # 验证 URL 格式
    if not webhook_url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/"):
        print(f"⚠️  警告: Webhook URL 格式可能不正确")
        print(f"   期望格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx")
        print(f"   当前 URL: {webhook_url[:60]}...")
    
    print(f"🔍 测试飞书 Webhook...")
    print(f"   URL: {webhook_url[:60]}...")
    
    # 构建测试消息
    payload = {
        "msg_type": "text",
        "content": {
            "text": "这是一条测试消息\n\n如果你收到这条消息，说明 Webhook 配置正确 ✅"
        }
    }
    
    try:
        print("\n📤 发送测试消息...")
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        print(f"   状态码: {response.status_code}")
        print(f"   响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                status_code = result.get("StatusCode") or result.get("code")
                
                if status_code == 0:
                    print("\n✅ Webhook 测试成功！")
                    print("   请检查飞书群聊，应该能看到测试消息")
                    return True
                else:
                    error_msg = result.get("msg") or result.get("StatusMessage") or "未知错误"
                    print(f"\n❌ Webhook 返回错误: {error_msg}")
                    print(f"   完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    return False
            except json.JSONDecodeError:
                print(f"\n⚠️  响应不是有效的 JSON: {response.text}")
                return False
        else:
            print(f"\n❌ HTTP 错误: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时")
        print("   请检查网络连接")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接错误")
        print("   请检查网络连接和 URL 是否正确")
        return False
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("飞书 Webhook 测试工具")
    print("=" * 60)
    
    # 方式1: 从环境变量读取
    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    
    # 方式2: 如果环境变量没有，可以在这里直接设置
    if not webhook_url:
        # 在这里填入你的 Webhook URL
        webhook_url = ""
    
    success = test_feishu_webhook(webhook_url)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试完成：Webhook 正常工作")
    else:
        print("❌ 测试完成：Webhook 存在问题")
        print("\n💡 建议：")
        print("   1. 检查 Webhook URL 是否正确")
        print("   2. 确认飞书机器人是否已启用")
        print("   3. 确认机器人是否在群聊中")
        print("   4. 尝试重新创建飞书机器人")
    print("=" * 60)


if __name__ == "__main__":
    main()

