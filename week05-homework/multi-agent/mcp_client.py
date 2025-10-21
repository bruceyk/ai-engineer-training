#!/usr/bin/env python3
"""
基于LangGraph和MCP的多Agent协作系统客户端
使用langchain_mcp_adapters和ChatTongyi实现
"""

import os
import sys
import asyncio
from typing import List, Dict, Any
from typing_extensions import TypedDict
from typing import Annotated

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langchain_community.chat_models import ChatTongyi

from app_config import config

class MultiAgentClient:
    """基于LangGraph的多Agent协作客户端"""
    
    def __init__(self):
        self.config = config
        self.mcp_client = None
        self.agent_graph = None
        self.llm = None
        
    async def initialize(self):
        """初始化客户端"""
        print("🚀 初始化基于LangGraph的多Agent协作系统...")
        
        # 验证配置
        if not self.config.validate():
            return False
            
        # 初始化通义千问模型
        self.llm = ChatTongyi(
            dashscope_api_key=self.config.dashscope_api_key,
            model_name=self.config.tongyi_config['model_name'],
            temperature=self.config.tongyi_config['temperature'],
            max_tokens=self.config.tongyi_config['max_tokens'],
            top_p=self.config.tongyi_config['top_p']
        )
        
        # 初始化MCP客户端 - 连接统一服务器
        mcp_config = self.config.get_mcp_client_config()
        self.mcp_client = MultiServerMCPClient(mcp_config)
        
        print("✅ 系统初始化成功")
        return True
    
    async def create_agent_graph(self, sessions: Dict[str, Any]):
        """创建基于LangGraph的Agent工作流图"""
        
        # 加载所有MCP工具
        all_tools = []
        for server_name, session in sessions.items():
            try:
                tools = await load_mcp_tools(session)
                all_tools.extend(tools)
                print(f"✅ {server_name}Agent MCP工具加载成功 ({len(tools)}个工具)")
            except Exception as e:
                print(f"❌ {server_name}Agent 工具加载失败: {e}")
        
        if not all_tools:
            raise Exception("未能加载任何MCP工具")
            
        # 绑定工具到LLM
        llm_with_tools = self.llm.bind_tools(all_tools)
        
        # 使用配置中的系统提示词
        system_prompt = self.config.prompts['system_prompt']
        
        # 创建提示词模板
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        chat_llm = prompt_template | llm_with_tools
        
        # 定义状态
        class State(TypedDict):
            messages: Annotated[List[AnyMessage], add_messages]
            current_step: str
            research_result: str
            writing_result: str
            review_result: str
            final_result: str
        
        # 定义节点函数
        def chat_node(state: State) -> State:
            """主对话节点"""
            response = chat_llm.invoke({"messages": state["messages"]})
            return {"messages": [response]}
        
        # 创建工具节点
        tool_node = ToolNode(tools=all_tools)
        
        # 构建图
        graph_builder = StateGraph(State)
        graph_builder.add_node("chat_node", chat_node)
        graph_builder.add_node("tool_node", tool_node)
        
        # 添加边
        graph_builder.add_edge(START, "chat_node")
        graph_builder.add_conditional_edges(
            "chat_node",
            tools_condition,
            {"tools": "tool_node", "__end__": END}
        )
        graph_builder.add_edge("tool_node", "chat_node")
        
        # 编译图
        self.agent_graph = graph_builder.compile(checkpointer=MemorySaver())
        
        return self.agent_graph
    
    async def process_request(self, user_request: str) -> str:
        """处理用户请求的完整工作流"""
        
        print(f"\n🎯 处理用户请求: {user_request}")
        print("=" * 80)
        
        # 连接统一MCP服务器
        async with self.mcp_client.session("multi_agent") as session:
            sessions = {"multi_agent": session}
            
            # 创建Agent图
            await self.create_agent_graph(sessions)
            
            # 执行多Agent协作工作流
            return await self._execute_workflow(user_request)
    
    async def _execute_workflow(self, user_request: str) -> str:
        """执行多Agent协作工作流"""
        
        config_dict = {"configurable": {"thread_id": self.config.langgraph_config['thread_id']}}
        
        # 第1步：研究分析
        print("\n" + "=" * 80)
        print("🔍 第1步：研究分析阶段")
        print("=" * 80)
        
        research_prompt = self.config.prompts['research_stage_prompt'].format(
            user_request=user_request
        )
        
        research_response = await self.agent_graph.ainvoke(
            {"messages": [{"role": "user", "content": research_prompt}]},
            config=config_dict
        )
        
        research_result = research_response["messages"][-1].content
        print(f"研究结果：\n{research_result[:500]}...")
        
        # 第2步：内容创作
        print("\n" + "=" * 80)
        print("✍️ 第2步：内容创作阶段")
        print("=" * 80)
        
        writing_prompt = self.config.prompts['writing_stage_prompt'].format(
            user_request=user_request,
            research_result=research_result
        )
        
        writing_response = await self.agent_graph.ainvoke(
            {"messages": [{"role": "user", "content": writing_prompt}]},
            config=config_dict
        )
        
        writing_result = writing_response["messages"][-1].content
        print(f"写作结果：\n{writing_result[:500]}...")
        
        # 第3步：内容审核
        print("\n" + "=" * 80)
        print("🔍 第3步：内容审核阶段")
        print("=" * 80)
        
        review_prompt = self.config.prompts['review_stage_prompt'].format(
            writing_result=writing_result
        )
        
        review_response = await self.agent_graph.ainvoke(
            {"messages": [{"role": "user", "content": review_prompt}]},
            config=config_dict
        )
        
        review_result = review_response["messages"][-1].content
        print(f"审核结果：\n{review_result[:500]}...")
        
        # 第4步：内容润色
        print("\n" + "=" * 80)
        print("✨ 第4步：内容润色阶段")
        print("=" * 80)
        
        editing_prompt = self.config.prompts['editing_stage_prompt'].format(
            writing_result=writing_result,
            review_result=review_result
        )
        
        editing_response = await self.agent_graph.ainvoke(
            {"messages": [{"role": "user", "content": editing_prompt}]},
            config=config_dict
        )
        
        final_result = editing_response["messages"][-1].content
        
        return final_result
    
    async def run_interactive(self):
        """运行交互式模式"""
        print("\n🤖 基于LangGraph和MCP的多Agent协作系统")
        print("真正的MCP服务器 + 通义千问模型 + LangGraph工作流")
        print("=" * 80)
        
        # 显示配置信息
        self.config.print_config_summary()
        print()
        
        print("💬 请输入您的需求（输入 'quit' 退出）:")
        print("示例：写一篇关于人工智能发展趋势的文章")
        print("示例：创作一份区块链技术报告")
        print("示例：写一篇关于机器学习的博客文章")
        print()
        
        while True:
            try:
                user_input = input("User: ").strip()
                if user_input.lower() in ["quit", "exit", "退出", "q"]:
                    print("👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                # 处理用户请求
                result = await self.process_request(user_input)
                
                # 显示最终结果
                print("\n" + "🎉" * 30)
                print("🎯 任务完成！")
                print("📝 原始需求:", user_input)
                print("🎉" * 30)
                print()
                print("📄 最终结果:")
                print("=" * 80)
                print(result)
                print("=" * 80)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 已退出。")
                break
            except Exception as e:
                print(f"❌ 处理过程中出现错误: {e}")
                print("请检查MCP服务器是否正常运行")

async def main():
    """主函数"""
    client = MultiAgentClient()
    
    # 初始化客户端
    if not await client.initialize():
        print("❌ 客户端初始化失败")
        return
    
    # 运行交互式模式
    await client.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())