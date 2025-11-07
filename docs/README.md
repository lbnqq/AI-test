# GitHub Pages 部署指南

## 📖 概述

本目录包含Portable PsyAgent项目的GitHub Pages部署文件，为项目提供专业的在线展示页面。

## 🚀 快速部署

### 方法一：通过GitHub仓库设置（推荐）

1. **进入GitHub仓库设置**
   - 访问你的GitHub仓库
   - 点击 "Settings" 选项卡
   - 在左侧菜单中找到 "Pages"

2. **配置Pages源**
   - 在 "Source" 部分选择 "Deploy from a branch"
   - Branch: 选择 `main` 分支
   - Folder: 选择 `/docs` 文件夹
   - 点击 "Save"

3. **等待部署**
   - GitHub会自动构建和部署网站
   - 几分钟后，你的网站将可以在 `https://[username].github.io/AgentPsyAssessment` 访问

### 方法二：使用GitHub Actions（可选）

创建 `.github/workflows/deploy.yml` 文件：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '16'

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs
```

## 📁 文件结构

```
docs/
├── index.html          # 主页面文件
├── .nojekyll           # 禁用Jekyll处理
└── README.md          # 本说明文件
```

## 🎨 页面特性

### 📱 响应式设计
- 支持桌面、平板、手机等多种设备
- 自适应布局，提供最佳浏览体验

### 🎯 多标签页结构
- **快速开始**: 新手指南和快速命令示例
- **测评工具**: 完整的测评工具库介绍
- **应用场景**: 企业应用和教育研究案例
- **技术架构**: 系统架构和技术特性说明
- **Claude Code技能**: 技能系统使用指南

### 🌈 现代化UI
- 使用Tailwind CSS构建
- 渐变色背景和卡片式布局
- Font Awesome图标库
- 交互式悬停效果

### 📊 可视化展示
- 项目统计数据
- 测评工具分类展示
- 行业解决方案图标

## 🔧 自定义配置

### 修改品牌信息
在 `index.html` 中修改以下部分：

```html
<!-- 页头信息 -->
<h1>Portable PsyAgent</h1>
<p>AI Agent心理评估与人格化分析平台</p>

<!-- 页脚信息 -->
<strong>作者：</strong>pTreezh / Dr Zhang
<strong>邮箱：</strong>3061176@qq.com
<strong>网站：</strong>https://cn.agentpsy.com
<strong>机构：</strong>AI人格实验室
```

### 更新项目链接
```html
<a href="https://github.com/ptreezh/AgentPsyAssessment" class="...">
    <i class="fab fa-github mr-2"></i>GitHub
</a>
<a href="https://cn.agentpsy.com" class="...">
    <i class="fas fa-globe mr-2"></i>AI人格实验室
</a>
```

### 修改配色方案
在 `<style>` 部分修改颜色变量：

```css
.gradient-bg {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

## 📊 内容管理

### 添加新的测评工具
在"测评工具"标签页中添加新的工具卡片：

```html
<div class="assessment-card">
    <h5 class="font-bold mb-2">新测评工具</h5>
    <p class="text-sm text-gray-600 mb-3">
        <strong>文件：</strong>new-assessment.json<br>
        <strong>题目：</strong>XX题<br>
        <strong>维度：</strong>维度说明
    </p>
    <div class="flex flex-wrap">
        <span class="tag tag-blue">标签1</span>
        <span class="tag tag-green">标签2</span>
    </div>
</div>
```

### 更新统计数据
修改首页的统计数字：

```html
<div class="text-3xl font-bold text-blue-600">30+</div>
<div class="text-gray-600">专业测评工具</div>
```

## 🚀 部署验证

部署完成后，检查以下功能：

1. ✅ 页面正常加载
2. ✅ 标签页切换正常
3. ✅ 响应式布局正常
4. ✅ 链接跳转正常
5. ✅ 图片和图标显示正常

## 🔍 SEO优化

页面已包含基本的SEO元素：

- `<title>` 标签
- Meta描述
- 结构化HTML标签
- 语义化的内容结构

## 📞 技术支持

如需帮助或遇到问题，请联系：

- **作者**: pTreezh / Dr Zhang
- **邮箱**: 3061176@qq.com
- **网站**: https://cn.agentpsy.com

---

## 📄 许可证

本文档遵循项目的开源许可证。