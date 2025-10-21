#!/usr/bin/env python3
"""
基于LangGraph和MCP的多Agent协作系统 - 主程序
使用langchain_mcp_adapters和ChatTongyi实现

作者: AI工程师训练营
版本: 1.0
"""

import os
import sys
import asyncio
import argparse
from app_config import config
from mcp_client import MultiAgentClient
import logging
#logging.basicConfig(level=logging.DEBUG)

def print_banner():
    """打印系统横幅"""
    print("=" * 80)
    print("🤖 基于LangGraph和MCP的多Agent协作系统")
    print("   Multi-Agent Collaboration System with LangGraph & MCP")
    print("=" * 80)
    print("🔧 技术栈:")
    print("   • LangGraph - 工作流编排")
    print("   • MCP (Model Context Protocol) - Agent通信")
    print("   • 通义千问 - 大语言模型")
    print("   • FastMCP - MCP服务器框架")
    print("=" * 80)

def print_usage():
    """打印使用说明"""
    print("\n💡 使用说明:")
    print("   1. 确保已配置 DASHSCOPE_API_KEY 环境变量")
    print("   2. 运行: python main.py")
    print("   3. 输入您的需求，系统将自动协调多个Agent完成任务")
    print("\n📝 示例需求:")
    print("   • 写一篇关于人工智能发展趋势的文章")
    print("   • 创作一份区块链技术报告")
    print("   • 写一篇关于机器学习的博客文章")
    print("   • 分析量子计算的应用前景")

async def check_system():
    """检查系统环境"""
    print("\n🔍 系统环境检查...")
    
    # 检查API Key
    if not config.validate():
        print("❌ 系统检查失败")
        print("\n🔧 解决方案:")
        print("   1. 设置环境变量: export DASHSCOPE_API_KEY='your_api_key'")
        print("   2. 或在 .env 文件中添加: DASHSCOPE_API_KEY=your_api_key")
        return False
    
    print("✅ API Key 配置正确")
    
    # 检查依赖包
    try:
        import langchain
        import langgraph
        import langchain_mcp_adapters
        import langchain_community
        from mcp.server.fastmcp import FastMCP
        print("✅ 依赖包检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("\n🔧 解决方案:")
        print("   运行: pip install -r requirements.txt")
        return False
    
    print("✅ 系统环境检查通过")
    return True

async def run_interactive():
    """运行交互式模式"""
    print("\n🚀 启动多Agent协作系统...")
    
    # 创建客户端
    client = MultiAgentClient()
    
    # 初始化客户端
    if not await client.initialize():
        print("❌ 系统初始化失败")
        return
    
    # 运行交互式模式
    await client.run_interactive()

async def run_single_request(request: str):
    """运行单次请求模式"""
    print(f"\n🎯 处理单次请求: {request}")
    
    # 创建客户端
    client = MultiAgentClient()
    
    # 初始化客户端
    if not await client.initialize():
        print("❌ 系统初始化失败")
        return
    
    # 处理请求
    try:
        result = await client.process_request(request)
        
        # 显示结果
        print("\n" + "🎉" * 30)
        print("🎯 任务完成！")
        print("🎉" * 30)
        print(f"\n📝 原始需求: {request}")
        print("\n📄 最终结果:")
        print("=" * 80)
        print(result)
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 请求处理失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="基于LangGraph和MCP的多Agent协作系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                                    # 交互式模式
  python main.py --request "写一篇AI文章"            # 单次请求模式
  python main.py --check                           # 仅检查系统环境
        """
    )
    
    parser.add_argument(
        "--request", "-r",
        type=str,
        help="单次请求内容（非交互式模式）"
    )
    
    parser.add_argument(
        "--check", "-c",
        action="store_true",
        help="仅检查系统环境，不运行系统"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="多Agent协作系统 v1.0"
    )
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    async def async_main():
        # 系统检查
        if not await check_system():
            return
        
        # 仅检查模式
        if args.check:
            print("\n✅ 系统检查完成，可以正常运行")
            return
        
        # 打印使用说明
        if not args.request:
            print_usage()
        
        # 运行模式选择
        if args.request:
            # 单次请求模式
            await run_single_request(args.request)
        else:
            # 交互式模式
            await run_interactive()
    
    # 运行异步主函数
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()