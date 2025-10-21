#!/usr/bin/env python3
"""
统一MCP服务器 - 包含所有Agent工具
基于FastMCP和ChatTongyi实现
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from langchain_community.chat_models import ChatTongyi
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.prompts import PromptTemplate
from app_config import config
import logging
#logging.basicConfig(level=logging.DEBUG)

# 初始化统一MCP服务器
mcp = FastMCP("MultiAgentServer")

# 初始化通义千问模型
llm = ChatTongyi(
    dashscope_api_key=config.dashscope_api_key,
    model_name=config.tongyi_config['model_name'],
    temperature=config.tongyi_config['temperature'],
    max_tokens=config.tongyi_config['max_tokens'],
    top_p=config.tongyi_config['top_p']
)

from langchain_community.llms.tongyi import Tongyi
llm_tongyi = Tongyi()

template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: 原始输入问题的最终答案

Begin!

Question: {input}
Thought:{agent_scratchpad}'''

# 创建搜索工具
search_wrapper = DuckDuckGoSearchResults(output_format="list", num_results=3)

@tool("web_search_tool")
def search(query: str) -> list[str]:
    """通过搜索引擎查询辅助的信息"""
    print("Debug search query: " + query)
    result = search_wrapper.invoke(query)
    return [res["snippet"] for res in result]

# ================================
# 研究Agent工具
# ================================

@mcp.tool()
def analyze_topic(topic: str) -> str:
    """深入分析指定主题，提供全面的主题分析报告"""
    _prompt = config.prompts['agent_prompts']['analyze_topic'].format(topic=topic)
    
    try:
        agent = create_react_agent(
            llm = llm_tongyi,
            tools = [],
            prompt= PromptTemplate.from_template(template)
        )
        agent_executor = AgentExecutor(agent=agent, tools=[])
        response = agent_executor.invoke({"input": _prompt})
        return response.get('output', '无结果')
    except Exception as e:
        return f"分析过程中出现错误: {str(e)}"

@mcp.tool()
def collect_background_info(topic: str, focus_area: str = "") -> str:
    """收集指定主题的背景信息和相关资料"""
    focus_text = f"，特别关注{focus_area}方面" if focus_area else ""
    
    _prompt = config.prompts['agent_prompts']['collect_background_info'].format(
        topic=topic, 
        focus_text=focus_text
    )
    
    try:
        agent = create_react_agent(
            llm = llm_tongyi,
            tools = [search],
            prompt= PromptTemplate.from_template(template)
        )
        agent_executor = AgentExecutor(agent=agent, tools=[search])
        response = agent_executor.invoke({"input": _prompt})
        return response.get('output', '无结果')
    except Exception as e:
        return f"信息收集过程中出现错误: {str(e)}"

@mcp.tool()
def identify_key_concepts(topic: str) -> str:
    """识别主题相关的关键概念和术语"""
    prompt = config.prompts['agent_prompts']['identify_key_concepts'].format(topic=topic)
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"概念识别过程中出现错误: {str(e)}"

@mcp.tool()
def research_trends(topic: str) -> str:
    """研究主题的最新发展趋势和前沿动态"""
    prompt = config.prompts['agent_prompts']['research_trends'].format(topic=topic)
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"趋势研究过程中出现错误: {str(e)}"

# ================================
# 写作Agent工具
# ================================

@mcp.tool()
def create_article(research_content: str, topic: str, article_type: str = "综合性文章") -> str:
    """基于研究内容创作高质量文章"""
    prompt = config.prompts['agent_prompts']['create_article'].format(
        topic=topic,
        article_type=article_type,
        research_content=research_content
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"文章创作过程中出现错误: {str(e)}"

@mcp.tool()
def generate_title(content: str, style: str = "专业") -> str:
    """为内容生成合适的标题"""
    prompt = config.prompts['agent_prompts']['generate_title'].format(
        style=style,
        content=content[:500] + "..." if len(content) > 500 else content
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"标题生成过程中出现错误: {str(e)}"

@mcp.tool()
def structure_content(raw_content: str, target_structure: str = "标准文章结构") -> str:
    """对内容进行结构化组织"""
    prompt = config.prompts['agent_prompts']['structure_content'].format(
        target_structure=target_structure,
        raw_content=raw_content
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"内容结构化过程中出现错误: {str(e)}"

@mcp.tool()
def create_summary(content: str, length: str = "中等") -> str:
    """创建内容摘要"""
    length_map = {
        "简短": "100-200字",
        "中等": "200-400字", 
        "详细": "400-600字"
    }
    
    target_length = length_map.get(length, "200-400字")
    
    prompt = config.prompts['agent_prompts']['create_summary'].format(
        length=length,
        target_length=target_length,
        content=content
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"摘要创建过程中出现错误: {str(e)}"

# ================================
# 审核Agent工具
# ================================

@mcp.tool()
def evaluate_content_quality(content: str) -> str:
    """评估内容质量并提供详细分析"""
    prompt = config.prompts['agent_prompts']['evaluate_content_quality'].format(content=content)
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"质量评估过程中出现错误: {str(e)}"

@mcp.tool()
def check_accuracy(content: str, topic: str) -> str:
    """检查内容的准确性"""
    prompt = config.prompts['agent_prompts']['check_accuracy'].format(
        topic=topic,
        content=content
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"准确性检查过程中出现错误: {str(e)}"

@mcp.tool()
def analyze_readability(content: str, target_audience: str = "一般读者") -> str:
    """分析内容的可读性"""
    prompt = config.prompts['agent_prompts']['analyze_readability'].format(
        target_audience=target_audience,
        content=content
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"可读性分析过程中出现错误: {str(e)}"

@mcp.tool()
def suggest_improvements(content: str, quality_issues: str) -> str:
    """基于质量问题提供改进建议"""
    prompt = config.prompts['agent_prompts']['suggest_improvements'].format(
        content=content,
        quality_issues=quality_issues
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"改进建议生成过程中出现错误: {str(e)}"

# ================================
# 润色Agent工具
# ================================

@mcp.tool()
def polish_content(content: str, review_feedback: str) -> str:
    """根据审核反馈润色内容"""
    prompt = config.prompts['agent_prompts']['polish_content'].format(
        content=content,
        review_feedback=review_feedback
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"内容润色过程中出现错误: {str(e)}"

@mcp.tool()
def improve_language(content: str, style: str = "专业") -> str:
    """改进内容的语言表达"""
    prompt = config.prompts['agent_prompts']['improve_language'].format(
        content=content,
        style=style
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"语言改进过程中出现错误: {str(e)}"

@mcp.tool()
def optimize_structure(content: str) -> str:
    """优化内容的结构组织"""
    prompt = config.prompts['agent_prompts']['optimize_structure'].format(content=content)
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"结构优化过程中出现错误: {str(e)}"

@mcp.tool()
def final_quality_check(content: str) -> str:
    """进行最终质量检查"""
    prompt = config.prompts['agent_prompts']['final_quality_check'].format(content=content)
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"质量检查过程中出现错误: {str(e)}"

@mcp.tool()
def enhance_readability(content: str, target_audience: str = "一般读者") -> str:
    """增强内容的可读性"""
    prompt = config.prompts['agent_prompts']['enhance_readability'].format(
        target_audience=target_audience,
        content=content
    )
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"可读性优化过程中出现错误: {str(e)}"

# ================================
# 资源定义
# ================================

@mcp.resource("multi-agent://workflow")
def get_workflow_info() -> str:
    """获取多Agent协作工作流信息"""
    return """
# 多Agent协作工作流

## 工作流程
1. 研究阶段：使用研究Agent工具进行主题分析和信息收集
2. 写作阶段：使用写作Agent工具创作内容
3. 审核阶段：使用审核Agent工具评估质量
4. 润色阶段：使用润色Agent工具优化内容

## Agent工具分类
- 研究Agent: analyze_topic, collect_background_info, identify_key_concepts, research_trends
- 写作Agent: create_article, generate_title, structure_content, create_summary
- 审核Agent: evaluate_content_quality, check_accuracy, analyze_readability, suggest_improvements
- 润色Agent: polish_content, improve_language, optimize_structure, final_quality_check, enhance_readability

## 使用建议
1. 按照工作流程顺序使用工具
2. 每个阶段的输出作为下一阶段的输入
3. 根据具体需求选择合适的工具
4. 注意保持内容的一致性和连贯性
"""

if __name__ == "__main__":
    print("🚀 启动统一MCP服务器")
    print("=" * 60)
    print("📋 研究Agent工具: analyze_topic, collect_background_info, identify_key_concepts, research_trends")
    print("📋 写作Agent工具: create_article, generate_title, structure_content, create_summary")
    print("📋 审核Agent工具: evaluate_content_quality, check_accuracy, analyze_readability, suggest_improvements")
    print("📋 润色Agent工具: polish_content, improve_language, optimize_structure, final_quality_check, enhance_readability")
    print("📚 可用资源: multi-agent://workflow")
    print("=" * 60)
    print("🔗 传输方式: stdio")
    print("💡 现在可以运行客户端: python mcp_client.py")
    print("=" * 60)
    mcp.run()