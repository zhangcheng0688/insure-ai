# InsureAI 部署指南

## 一、整体架构

```
用户浏览器 → Lovable网站(Vercel) → InsureAI后端(你的服务器)
                  ↓                        ↓
            Supabase Auth             DeepSeek LLM
            Lemon Squeezy支付         文件解析+PDF生成
```

## 二、你需要准备的账号

| 服务 | 用途 | 注册链接 | 费用 |
|---|---|---|---|
| **Lovable** | 生成网站代码 | lovable.dev | 免费开始 |
| **Vercel** | 部署网站 | vercel.com | 免费 |
| **Supabase** | 用户认证+数据库 | supabase.com | 免费 |
| **Lemon Squeezy** | 收钱（支持支付宝） | lemonsqueezy.com | 免费注册 |
| **服务器** | 跑 InsureAI 后端 | 阿里云/腾讯云/Railway | ~¥50/月 |

## 三、部署步骤

### Step 1: Lovable 生成网站

1. 打开 lovable.dev，注册/登录
2. 新建项目 → 粘贴 `LOVABLE_PROMPT.md` 里的英文提示词
3. Lovable 会自动生成完整网站
4. 在 Lovable 里预览，微调不满意的地方
5. 连接 GitHub，导出代码

### Step 2: 配置 Supabase

1. 在 supabase.com 创建新项目
2. 开启 Email Auth（不需要邮箱验证，开发阶段）
3. 创建 `profiles` 表：
```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  email TEXT,
  plan TEXT DEFAULT 'free',
  daily_requests INTEGER DEFAULT 0,
  total_requests INTEGER DEFAULT 0,
  request_date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```
4. 复制 Supabase URL 和 anon key，设为 Lovable 项目的环境变量

### Step 3: 配置 Lemon Squeezy

1. 注册 lemonsqueezy.com
2. 创建两个产品：
   - **InsureAI Pro** — $5.99/mo (≈¥39)
   - **InsureAI Enterprise** — $29.99/mo (≈¥199)
3. 在 Settings → Webhooks 添加：
   - URL: `https://你的后端域名/api/v1/auth/lemon-squeezy-webhook`
   - Events: `order_created`, `subscription_updated`, `subscription_cancelled`
4. 复制 API key，设为 Lovable 项目环境变量

### Step 4: 部署后端

```bash
# 在服务器上
git clone https://github.com/YOUR_USERNAME/insure-ai.git
cd insure-ai
cp .env.example .env
# 编辑 .env 填写 DeepSeek API Key

# 用 Docker
docker compose up -d

# 或直接运行
pip install -r backend/requirements.txt
PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

建议用 Railway (railway.app) 或 Fly.io 一键部署，省去服务器运维。

### Step 5: 连接前后端

在 Lovable 项目/Vercel 设置环境变量：
```
NEXT_PUBLIC_API_BASE_URL=https://你的后端域名
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_LEMON_SQUEEZY_STORE_ID=xxx
```

### Step 6: 部署网站到 Vercel

1. Lovable → Deploy → Vercel
2. 配置域名（可选）
3. 网站上线！

## 四、用户支付流程

```
1. 用户注册 → Supabase 创建账号
2. 用户点击"升级Pro" → 跳转 Lemon Squeezy 支付页
3. 用户支付宝扫码付款 ¥39
4. Lemon Squeezy 回调你的后端 → 升级 plan=pro
5. 用户回到网站 → 自动显示 Pro 权益（50次/天）
```

## 五、环境变量清单

**Lovable 前端 (Vercel):**
```
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxxx...
NEXT_PUBLIC_LEMON_SQUEEZY_STORE_ID=xxxxx
```

**InsureAI 后端 (.env):**
```
DEEPSEEK_API_KEY=sk-xxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_LLM_MODEL=deepseek-chat
DATABASE_URL=sqlite:///./insure_ai.db
REDIS_URL=redis://localhost:6379/0
```
