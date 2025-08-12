# Webhook 实时同步设置指南

要实现"上游有更新就立即同步"的效果，需要配置GitHub webhook。

## 🎯 目标效果

- 上游仓库 `Blackoutta/ai-engineer-training` 有任何push操作
- 立即触发你的fork仓库同步
- **延迟时间：通常1-5分钟内**

## 🔧 设置步骤

### 1. 获取你的仓库webhook URL

在你的fork仓库中，webhook URL格式为：
```
https://api.github.com/repos/YOUR_USERNAME/ai-engineer-training/dispatches
```

### 2. 创建Personal Access Token

1. 进入 GitHub Settings → Developer settings → Personal access tokens
2. 选择 "Tokens (classic)"
3. 生成新token，勾选 `repo` 权限
4. 复制token（只显示一次！）

### 3. 配置上游仓库的webhook

由于你无法直接在上游仓库配置webhook，可以使用以下替代方案：

#### 方案A：使用GitHub Actions的定时检查（已配置）
- **频率**: 每30分钟检查一次
- **延迟**: 最多30分钟
- **优点**: 无需额外配置
- **缺点**: 不是真正的实时

#### 方案B：使用第三方服务监控
可以使用如 [IFTTT](https://ifttt.com/) 或 [Zapier](https://zapier.com/) 监控上游仓库变化

#### 方案C：手动触发
在Actions页面手动运行同步工作流

## 📊 当前配置效果

```yaml
schedule:
  - cron: '*/30 * * * *'  # 每30分钟检查
```

- **检查频率**: 每30分钟
- **最大延迟**: 30分钟
- **资源消耗**: 较低
- **可靠性**: 高

## 🚀 进一步优化建议

如果希望更频繁的检查，可以调整cron表达式：

```yaml
# 每15分钟检查
- cron: '*/15 * * * *'

# 每10分钟检查  
- cron: '*/10 * * * *'

# 每5分钟检查
- cron: '*/5 * * * *'
```

**注意**: 过于频繁的检查可能触发GitHub的速率限制，建议不要低于5分钟间隔。

## ✅ 推荐配置

对于大多数使用场景，**每30分钟检查一次**已经足够：
- 平衡了实时性和资源消耗
- 避免了GitHub API限制
- 提供了良好的用户体验
