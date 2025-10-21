# 基于LangGraph和MCP的多Agent协作系统

一个基于LangGraph工作流编排和MCP协议的智能多Agent协作系统，使用通义千问大语言模型，实现研究、写作、审核、润色的完整内容创作流程。

## 🚀 系统特性

- **🔄 工作流编排**: 使用LangGraph实现复杂的多Agent协作流程
- **🤖 多Agent协作**: 研究Agent、写作Agent、审核Agent、润色Agent分工协作
- **📡 MCP协议**: 基于Model Context Protocol实现Agent间通信
- **🧠 智能模型**: 集成通义千问大语言模型
- **⚡ 高效处理**: 支持并行处理和流式响应

## 📋 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户请求      │───▶│  LangGraph      │───▶│   MCP服务器     │
│   User Request  │    │  工作流编排     │    │   Agent工具     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   最终结果      │◀───│  通义千问模型   │◀───│   工具调用      │
│  Final Result   │    │  ChatTongyi     │    │  Tool Calls     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ 工作流程

1. **🔍 研究阶段**: 使用研究Agent分析主题、收集信息、识别关键概念
2. **✍️ 写作阶段**: 基于研究结果，使用写作Agent创作高质量内容
3. **🔍 审核阶段**: 使用审核Agent评估内容质量、准确性和可读性
4. **✨ 润色阶段**: 根据审核反馈，使用润色Agent优化内容

## 📦 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd multi-agent

# 安装依赖
pip install -r requirements.txt
```

## ⚙️ 配置设置

### 1. API Key配置

```bash
# 方法1: 环境变量
export DASHSCOPE_API_KEY="your_dashscope_api_key"

# 方法2: .env文件
echo "DASHSCOPE_API_KEY=your_dashscope_api_key" > .env
```

## 🚀 使用方法

### 交互式模式

```bash
python main.py
```

### 单次请求模式

```bash
python main.py --request "写一篇关于人工智能发展趋势的文章"
```

### 系统检查

```bash
python main.py --check
```

## 📝 使用示例

### 示例1: 技术文章创作

```bash
python main.py --request "写一篇关于区块链技术应用前景的深度分析文章"
```

### 示例2: 研究报告

```bash
python main.py --request "创作一份关于量子计算发展现状的研究报告"
```

### 示例3: 科普文章

```bash
python main.py --request "写一篇面向大众的机器学习科普文章"
```

## 🔧 核心组件

### 1. 主程序 (main.py)
- 系统入口点
- 命令行参数处理
- 环境检查和初始化

### 2. 配置管理 (app_config.py)
- 统一的系统配置
- API Key管理
- 模型参数配置

### 3. MCP客户端 (mcp_client.py)
- LangGraph工作流实现
- 多Agent协作逻辑
- 请求处理和结果整合

### 4. MCP服务器 (unified_mcp_server.py)
- 统一的Agent工具服务器
- 17个专业工具函数
- 基于FastMCP框架

## 🛠️ Agent工具

### 研究Agent工具
- `analyze_topic`: 深入分析指定主题
- `collect_background_info`: 收集背景信息
- `identify_key_concepts`: 识别关键概念
- `research_trends`: 研究发展趋势

### 写作Agent工具
- `create_article`: 创作高质量文章
- `generate_title`: 生成合适标题
- `structure_content`: 结构化内容
- `create_summary`: 创建内容摘要

### 审核Agent工具
- `evaluate_content_quality`: 评估内容质量
- `check_accuracy`: 检查准确性
- `analyze_readability`: 分析可读性
- `suggest_improvements`: 提供改进建议

### 润色Agent工具
- `polish_content`: 根据反馈润色内容
- `improve_language`: 改进语言表达
- `optimize_structure`: 优化内容结构
- `final_quality_check`: 最终质量检查
- `enhance_readability`: 增强可读性

## 📊 系统要求

- Python 3.8+
- 8GB+ RAM (推荐)
- 网络连接 (访问通义千问API)

## 🔍 故障排除

### 常见问题

1. **API Key错误**
   ```
   解决方案: 检查DASHSCOPE_API_KEY环境变量设置
   ```

2. **依赖包缺失**
   ```
   解决方案: pip install -r requirements.txt
   ```

3. **MCP连接失败**
   ```
   解决方案: 检查unified_mcp_server.py是否可正常运行
   ```