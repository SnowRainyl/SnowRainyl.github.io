# SnowRainyl's Blog

个人双语博客，中英文自动互译，无需手动操作。

**线上地址：** https://snowrainyl.github.io
**GitHub：** https://github.com/SnowRainyl/SnowRainyl.github.io

---

## 技术栈

| 用途 | 工具 |
|------|------|
| 静态站点生成 | [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) 主题 |
| 托管 & 部署 | GitHub Pages + GitHub Actions |
| 后台管理 | [Sveltia CMS](https://github.com/sveltia/sveltia-cms)（访问 `/admin`） |
| CMS OAuth 认证 | Cloudflare Workers |
| 自动翻译 | Google Gemini API（`gemini-3-flash-preview`） |
| 评论 & 点赞 | [Giscus](https://giscus.app/)（基于 GitHub Discussions） |

---

## 已实现功能

### 双语自动同步
- 在 CMS 中发布**中文文章** → GitHub Actions 自动调用 Gemini API 翻译成英文并发布
- 在 CMS 中发布**英文文章** → 同样自动翻译成中文并发布
- 在 CMS 中**删除任意一篇** → 对应语言版本自动同步删除
- 全程无需使用 git 命令行

### 评论 & 点赞共享
- 中英文两个版本的文章共用同一个 Giscus 评论区和点赞
- 无论读者在哪个语言版本留言，另一版本也能看到

### 自动部署
- 推送到 `main` 分支后自动构建并部署到 GitHub Pages
- 翻译完成后再次触发部署，确保译文同步上线

---

## 目录结构

```
.
├── content/
│   ├── zh/posts/       # 中文文章
│   └── en/posts/       # 英文文章（自动生成）
├── layouts/
│   └── partials/
│       └── comments.html   # Giscus 评论配置
├── scripts/
│   └── translate.py    # 翻译 & 删除同步脚本
├── static/
│   └── admin/          # Sveltia CMS 后台
│       ├── index.html
│       └── config.yml
├── .github/workflows/
│   ├── auto-translate.yml  # 翻译触发 & 删除同步
│   └── deploy.yml          # 构建 & 部署到 GitHub Pages
└── hugo.yaml           # Hugo 站点配置
```

---

## 工作流程

```
CMS 发布文章
    │
    ├─► auto-translate.yml 触发
    │       └─► translate.py 调用 Gemini API 翻译
    │               └─► 翻译失败自动重试（最多 3 次，间隔 20s/40s）
    │
    └─► deploy.yml 触发（auto-translate 完成后再次触发，确保译文已就位）
            └─► Hugo 构建 → 部署到 GitHub Pages
```

---

## 本地开发

```bash
# 安装 Hugo（需要 extended 版本）
brew install hugo

# 启动本地预览
hugo server -D

# 访问后台（需要先启动本地服务）
open http://localhost:1313/admin
```

---

## 环境变量 / Secrets

在 GitHub 仓库的 Settings → Secrets 中配置：

| Secret | 说明 |
|--------|------|
| `GEMINI_API_KEY` | Google Gemini API 密钥，用于自动翻译 |
