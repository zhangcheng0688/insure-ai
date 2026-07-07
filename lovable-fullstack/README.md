# InsureAI — Lovable 全栈部署指南

## 文件说明

这个目录 (`lovable-fullstack/`) 包含完整的 TypeScript 后端代码，用于在 Lovable 项目中实现全栈功能。

## 目录结构

```
lovable-fullstack/
├── app/
│   ├── api/              # Server Functions (API 路由)
│   │   ├── claims.ts          # 理赔分析
│   │   ├── underwriting.ts    # 核保分析
│   │   ├── new-business.ts    # 新业务
│   │   ├── policy-issuance.ts # 保单出单
│   │   ├── servicing.ts       # 保单服务
│   │   ├── renewal.ts         # 续保
│   │   ├── kb-upload.ts       # 知识库上传
│   │   ├── kb-search.ts       # 知识库搜索
│   │   └── quota.ts           # 配额查询
│   └── lib/              # 核心库
│       ├── qwen.ts       # 千问 API 封装
│       ├── agents.ts     # Agent Prompts
│       ├── kb.ts         # Supabase pgvector 知识库
│       ├── parser.ts     # 文本解析/切片
│       └── quota.ts      # 配额管理
└── supabase/
    └── migrations/
        └── 001_init.sql  # 数据库初始化
```

## 部署步骤

### 第 1 步：Supabase 配置

1. 打开 Supabase 项目 → SQL Editor
2. 执行 `supabase/migrations/001_init.sql`
3. 确认表已创建：`knowledge_base`, `profiles`, `documents`
4. 确认 pgvector 扩展已启用

### 第 2 步：环境变量

在 Lovable 项目的环境变量中添加：

```
VITE_SUPABASE_URL=https://你的项目.supabase.co
VITE_SUPABASE_ANON_KEY=你的anon_key
VITE_SUPABASE_SERVICE_ROLE_KEY=你的service_role_key
VITE_QWEN_API_KEY=sk-你的千问key
```

### 第 3 步：复制代码到 Lovable

把 `app/lib/` 和 `app/api/` 下的所有文件复制到 Lovable 项目对应位置。

### 第 4 步：前端调用

在 Lovable 前端页面中调用 Server Functions：

```typescript
import { analyzeClaim } from "@/app/api/claims";

const result = await analyzeClaim({ data: {
  text: "理赔描述...",
  policyWording: "保单条款...",
  claimType: "Property Damage",
  userId: currentUser.id
}});

console.log(result.markdown); // AI 分析结果
```

### 第 5 步：种子数据

在 Supabase SQL Editor 中执行：

```sql
-- 插入公共知识库种子数据（从 Python 版本的 seed_knowledge.py 转换）
-- 或使用 API 上传
```

## 与 Python 后端的区别

| 功能 | Python 后端 | Lovable 全栈 |
|---|---|---|
| AI 调用 | LiteLLM | 直接 fetch 千问 API |
| 知识库 | ChromaDB | Supabase pgvector |
| 文件解析 | PyMuPDF | 前端/Server Function 处理 |
| PDF 生成 | WeasyPrint | 需要额外方案 |
| 部署 | Railway/Docker | Vercel (Lovable 自动部署) |

## 注意事项

1. **PDF 解析**：当前版本使用简单文本提取。如需完整 PDF 解析，建议在 Server Function 中使用 `pdf-parse` npm 包。
2. **PDF 生成**：当前返回 Markdown。如需 PDF 输出，可以使用 `puppeteer` 或调用外部 API。
3. **千问 API Key**：放在服务端环境变量中，不要暴露到前端。
