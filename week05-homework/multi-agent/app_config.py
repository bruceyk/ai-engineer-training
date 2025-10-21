"""
配置管理 - 统一的系统配置
基于LangGraph和MCP架构
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置管理"""
    
    def __init__(self):
        # ==================== API配置 ====================
        # 通义千问API配置
        self.dashscope_api_key = os.getenv('DASHSCOPE_API_KEY') or "your_dashscope_api_key_here"
        
        # ==================== LangGraph配置 ====================
        self.langgraph_config = {
            'checkpointer': 'memory',  # 检查点存储类型
            'thread_id': 'multi_agent_thread',  # 线程ID
            'max_iterations': 10,  # 最大迭代次数
        }
        
        # ==================== 统一MCP服务器配置 ====================
        self.mcp_servers = {
            'multi_agent': {
                'name': 'multi_agent',
                'transport': 'stdio',
                'description': '统一多Agent服务器',
                'command': 'python',
                'args': ['unified_mcp_server.py'],
            }
        }
        
        # ==================== 通义千问模型配置 ====================
        self.tongyi_config = {
            'model_name': 'qwen-max',  # 可选: qwen-turbo, qwen-plus, qwen-max
            'temperature': 0.7,
            'max_tokens': 2000,
            'top_p': 0.9,
        }
        
        # ==================== 工作流配置 ====================
        self.workflow_config = {
            'enable_research': True,
            'enable_review': True, 
            'enable_editing': True,
            'parallel_processing': False,
        }
        
        # ==================== 系统配置 ====================
        self.system_config = {
            'max_retries': 3,
            'timeout': 30,
            'log_level': 'INFO',
        }
        
        # ==================== 提示词配置 ====================
        self.prompts = {
            # 系统级提示词
            'system_prompt': """你是一个智能的多Agent协作系统协调器。
你可以调用不同的Agent工具来完成复杂的内容创作任务。

工作流程：
1. 研究阶段：分析主题，收集背景信息
2. 写作阶段：基于研究结果创作内容
3. 审核阶段：评估内容质量，提供改进建议
4. 润色阶段：根据反馈优化内容

请根据用户需求，合理调用各个Agent工具，确保输出高质量的内容。""",
            
            # 工作流阶段提示词
            'research_stage_prompt': """请使用研究Agent的工具对以下主题进行深入分析：

用户需求：{user_request}

请按以下步骤进行：
1. 使用 analyze_topic 工具分析主题
2. 使用 collect_background_info 工具收集背景信息
3. 使用 identify_key_concepts 工具识别关键概念
4. 使用 research_trends 工具研究发展趋势

请提供全面的研究分析报告。""",
            
            'writing_stage_prompt': """基于以下研究结果，请使用写作Agent的工具创作高质量内容：

原始需求：{user_request}

研究结果：
{research_result}

请按以下步骤进行：
1. 使用 create_article 工具创作文章
2. 使用 generate_title 工具生成标题
3. 使用 structure_content 工具优化结构

请创作完整、专业的内容。""",
            
            'review_stage_prompt': """请使用审核Agent的工具对以下内容进行全面评估：

待审核内容：
{writing_result}

请按以下步骤进行：
1. 使用 evaluate_content_quality 工具评估内容质量
2. 使用 check_accuracy 工具检查准确性
3. 使用 analyze_readability 工具分析可读性
4. 使用 suggest_improvements 工具提供改进建议

请提供详细的审核报告。""",
            
            'editing_stage_prompt': """请使用润色Agent的工具根据审核反馈优化内容：

原始内容：
{writing_result}

审核反馈：
{review_result}

请按以下步骤进行：
1. 使用 polish_content 工具根据反馈润色内容
2. 使用 improve_language 工具改进语言表达
3. 使用 optimize_structure 工具优化结构
4. 使用 final_quality_check 工具进行最终检查

请提供最终优化后的内容。""",
            
            # Agent工具提示词模板
            'agent_prompts': {
                # 研究Agent工具提示词
                'analyze_topic': """作为专业的研究分析专家，请对以下主题进行深入分析：

主题：{topic}

请从以下角度进行分析：
1. 主题定义和核心概念
2. 发展历史和现状
3. 主要特点和优势
4. 面临的挑战和问题
5. 未来发展趋势
6. 相关技术和应用领域

请提供结构化、专业的分析报告。""",
                
                'collect_background_info': """作为专业的信息收集专家，请收集关于"{topic}"的详细背景信息{focus_text}。

请包含以下内容：
1. 基础概念和定义
2. 发展历程和重要里程碑
3. 关键人物和组织
4. 重要事件和案例
5. 相关统计数据和趋势
6. 国内外发展对比
7. 参考资料和信息来源

请确保信息准确、全面、有条理。""",
                
                'identify_key_concepts': """作为专业的概念分析专家，请识别和解释与"{topic}"相关的关键概念和术语。

请按以下格式整理：
1. 核心概念（5-8个最重要的概念）
2. 技术术语（相关的专业术语）
3. 相关理论（支撑的理论基础）
4. 应用领域（主要应用场景）
5. 发展阶段（不同发展阶段的特征）

每个概念请提供：
- 准确定义
- 重要性说明
- 与主题的关联性""",
                
                'research_trends': """作为专业的趋势研究专家，请分析"{topic}"的最新发展趋势和前沿动态。

请从以下角度分析：
1. 技术发展趋势
2. 市场发展趋势
3. 政策环境变化
4. 行业应用趋势
5. 国际发展对比
6. 未来发展预测
7. 机遇与挑战

请提供基于事实的分析，避免过度推测。""",
                
                # 写作Agent工具提示词
                'create_article': """作为专业的内容创作专家，请基于以下研究内容创作一篇关于"{topic}"的{article_type}。

研究内容：
{research_content}

创作要求：
1. 文章结构清晰，逻辑性强
2. 内容准确，表达专业
3. 语言流畅，易于理解
4. 包含引言、正文、结论
5. 适当使用小标题组织内容
6. 字数控制在1500-2500字

请确保文章质量达到专业水准。""",
                
                'generate_title': """作为专业的标题创作专家，请为以下内容生成{style}风格的标题。

内容摘要：
{content}

要求：
1. 标题准确反映内容主题
2. 具有吸引力和可读性
3. 长度适中（10-25字）
4. 符合{style}风格
5. 提供3-5个备选标题

请按优先级排序提供标题选项。""",
                
                'structure_content': """作为专业的内容结构专家，请将以下原始内容按照{target_structure}进行重新组织。

原始内容：
{raw_content}

结构化要求：
1. 逻辑层次清晰
2. 段落划分合理
3. 使用适当的标题和小标题
4. 确保内容连贯性
5. 突出重点信息
6. 优化阅读体验

请提供结构化后的完整内容。""",
                
                'create_summary': """作为专业的摘要写作专家，请为以下内容创建{length}摘要（{target_length}）。

原始内容：
{content}

摘要要求：
1. 准确概括主要内容
2. 保持逻辑清晰
3. 语言简洁明了
4. 突出核心观点
5. 字数控制在{target_length}

请提供高质量的内容摘要。""",
                
                # 审核Agent工具提示词
                'evaluate_content_quality': """作为专业的内容质量评估专家，请对以下内容进行全面的质量评估。

待评估内容：
{content}

评估维度：
1. 内容准确性（信息是否准确可靠）
2. 逻辑清晰度（结构是否合理，逻辑是否清晰）
3. 语言表达（用词是否准确，表达是否流畅）
4. 完整性（内容是否完整，是否有遗漏）
5. 专业性（是否达到专业水准）
6. 可读性（是否易于理解和阅读）

请为每个维度打分（1-10分）并提供具体的评估意见和改进建议。""",
                
                'check_accuracy': """作为专业的事实核查专家，请检查以下关于"{topic}"的内容的准确性。

待检查内容：
{content}

检查要点：
1. 事实陈述的准确性
2. 数据和统计信息的可靠性
3. 概念定义的准确性
4. 时间线和历史事件的正确性
5. 技术术语的使用是否恰当
6. 引用和参考的合理性

请指出发现的任何不准确或可疑的信息，并提供正确的信息或建议。""",
                
                'analyze_readability': """作为专业的可读性分析专家，请分析以下内容对于{target_audience}的可读性。

待分析内容：
{content}

分析要点：
1. 语言难度是否适合目标读者
2. 句子长度和复杂度
3. 专业术语的使用频率和解释
4. 段落结构和组织
5. 逻辑流程的清晰度
6. 阅读体验的友好程度

请提供可读性评分（1-10分）和具体的改进建议。""",
                
                'suggest_improvements': """作为专业的内容改进顾问，请基于发现的质量问题为以下内容提供具体的改进建议。

原始内容：
{content}

发现的质量问题：
{quality_issues}

请提供：
1. 针对每个问题的具体改进建议
2. 改进的优先级排序
3. 实施改进的具体方法
4. 预期的改进效果
5. 需要注意的事项

请确保建议具体、可操作、有效。""",
                
                # 润色Agent工具提示词
                'polish_content': """作为专业的内容润色专家，请根据审核反馈对以下内容进行全面润色。

原始内容：
{content}

审核反馈：
{review_feedback}

润色要求：
1. 根据反馈意见进行针对性改进
2. 提升语言表达的准确性和流畅性
3. 优化内容结构和逻辑组织
4. 增强内容的专业性和可读性
5. 确保信息的完整性和准确性
6. 保持原有内容的核心观点

请提供润色后的完整内容，并简要说明主要改进点。""",
                
                'improve_language': """作为专业的语言改进专家，请改进以下内容的语言表达，使其达到{style}水准。

原始内容：
{content}

改进要求：
1. 用词更加准确、恰当
2. 句式更加多样、流畅
3. 表达更加简洁、有力
4. 语法更加规范、正确
5. 风格符合{style}要求
6. 保持原意不变

请提供语言改进后的内容。""",
                
                'optimize_structure': """作为专业的结构优化专家，请优化以下内容的结构组织。

原始内容：
{content}

优化要求：
1. 逻辑层次更加清晰
2. 段落划分更加合理
3. 标题使用更加恰当
4. 内容过渡更加自然
5. 重点信息更加突出
6. 整体结构更加完善

请提供结构优化后的内容。""",
                
                'final_quality_check': """作为专业的质量检查专家，请对以下润色后的内容进行最终质量检查。

润色后内容：
{content}

检查要点：
1. 内容准确性和完整性
2. 语言表达的流畅性
3. 结构组织的合理性
4. 逻辑关系的清晰性
5. 专业术语的准确性
6. 格式规范的统一性

请提供：
1. 质量检查结果（通过/需要微调/需要重大修改）
2. 发现的问题（如有）
3. 最终改进建议（如需要）
4. 质量评分（0-10分）
5. 内容亮点总结

请确保检查全面、客观、专业。""",
                
                'enhance_readability': """作为专业的可读性优化专家，请针对{target_audience}优化以下内容的可读性。

原始内容：
{content}

目标受众：{target_audience}

优化要求：
1. 调整语言难度适合目标受众
2. 优化句子长度和复杂度
3. 增加必要的解释和说明
4. 改进段落组织和格式
5. 使用更友好的表达方式
6. 保持专业性和准确性

请提供可读性优化后的内容。"""
            }
        }
    
    def validate(self) -> bool:
        """验证配置是否完整"""
        if not self.dashscope_api_key or self.dashscope_api_key == "your_dashscope_api_key_here":
            print("❌ 错误: DASHSCOPE_API_KEY 未正确配置")
            print("请在config.py中设置您的API Key:")
            print("  self.dashscope_api_key = 'your_actual_api_key'")
            print("或设置环境变量:")
            print("  export DASHSCOPE_API_KEY='your_actual_api_key'")
            return False
        return True
    
    def get_mcp_client_config(self) -> Dict[str, Dict[str, Any]]:
        """获取MCP客户端配置"""
        import os
        return {
            "multi_agent": {
                "transport": "stdio",
                "command": "python",
                "args": ["unified_mcp_server.py"],
                "cwd": os.getcwd()
            }
        }
    
    def get_server_ports(self) -> list:
        """获取所有服务器端口"""
        ports = []
        for server in self.mcp_servers.values():
            url = server['url']
            port = int(url.split(':')[2].split('/')[0])
            ports.append(port)
        return ports
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("📋 系统配置摘要:")
        print(f"  • 模型: {self.tongyi_config['model_name']}")
        print(f"  • API Key: {'已配置' if self.dashscope_api_key and self.dashscope_api_key != 'your_dashscope_api_key_here' else '未配置'}")
        print(f"  • MCP服务器: 统一服务器 (stdio)")
        print(f"  • LangGraph线程ID: {self.langgraph_config['thread_id']}")

# 全局配置实例
config = Config()