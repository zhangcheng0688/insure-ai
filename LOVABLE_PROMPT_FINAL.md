# InsureAI — Lovable 最终完整提示词

## 使用方式
把这个完整提示词粘贴到 Lovable 的现有项目中（Update mode），它会覆盖整个网站。

---

COPY AND PASTE EVERYTHING BELOW INTO LOVABLE:

---

COMPLETE WEBSITE REDESIGN AND UPDATE. Apply ALL of the following:

## DESIGN SYSTEM (inspired by premium design portfolios like haoqi.design):

**Core aesthetic:** Dark, minimal, premium — like a high-end design studio built an insurance platform.

**Colors:**
- Background: Deep black (#0A0A0B) for main surfaces, slightly lighter (#141416) for cards
- Text: White (#FFFFFF) primary, #A1A1A6 secondary, #6E6E73 muted
- Accent: A single vibrant accent color — use a warm amber/gold (#F5A623) for CTAs and highlights, OR a clean blue (#3B82F6) for trust. Pick one and use it SPARINGLY — only on primary buttons, active links, and key highlights.
- Borders: Very subtle — rgba(255,255,255,0.06) on cards, rgba(255,255,255,0.1) on inputs
- Selection/hover: accent color at 15% opacity

**Typography:**
- Primary font: Inter or system sans-serif
- Monospace font: JetBrains Mono or SF Mono for data/metrics/API keys
- Large display text uses viewport-relative sizing (clamp or vw units) for hero headlines
- Everything uses proper font-weight hierarchy: 700 for headlines, 500 for subheads, 400 for body
- Letter-spacing: -0.02em on large headlines for tight premium feel

**Layout:**
- 12-column CSS grid system
- Generous padding: 64px horizontal on desktop, 24px on mobile
- Section vertical spacing: 120-160px between major sections
- Full viewport height hero sections
- Sticky header with backdrop-blur
- No visible scrollbars (use CSS to hide but keep scrollability)

**Cards & Surfaces:**
- Background: #141416
- Border: 1px solid rgba(255,255,255,0.06)
- Border-radius: 16px
- No box-shadow — use subtle borders instead of shadows
- Hover: border color shifts to rgba(255,255,255,0.15)

**Buttons:**
- Primary: accent color background, black text, 8px radius, subtle scale animation on hover (scale: 1.02)
- Secondary: transparent, white border, white text, same radius
- Ghost: transparent, no border, white text, underline on hover
- All buttons have transition: all 200ms ease-out

**Animations:**
- Page transitions: subtle fade-in (opacity 0→1, 300ms)
- Card hover: border lightens, slight translateY(-2px)
- Loading states: shimmer/skeleton with subtle pulse
- Scroll-triggered reveals: elements fade up as they enter viewport
- Motion-reduce: respect prefers-reduced-motion — disable all animations

**Navigation:**
- Fixed top header with backdrop-blur(20px)
- Left: Logo (just text "InsureAI" in bold, or a simple shield icon + text)
- Center/Right: 工作台 | 定价 | 文档 | 登录
- Mobile: hamburger → fullscreen overlay menu with large typography

---

## ALL PAGES — CHINESE AS PRIMARY LANGUAGE:

Default language is Chinese. Add a subtle language toggle (中 | EN) in the header. When English is selected, all text switches to English. Store preference in localStorage.

### 1. LANDING PAGE (/):

**Hero Section (full viewport height):**
- Large headline: "让 AI 处理保险文档" (3-5 words, very large, tight letter-spacing)
- Subtitle in muted text: "覆盖保险全生命周期——自动生成核保备忘录、理赔裁定、续保方案。像呼吸一样自然。"
- Two buttons: "免费试用 7 天" (primary, accent color) / "了解详情 ↓" (ghost)
- Background: subtle animated gradient or dot-grid pattern, very dark
- Trust line below: "已处理 10,000+ 份保险文档 · 开源 · 支持多家大模型"

**Features Section:**
- Section title: "六大环节，一站式覆盖"
- 6 cards in a 3x2 grid, each dark card with:
  - A single emoji or simple icon at top (not colored, use white at 60% opacity)
  - Title (bold, white)
  - One-line description (muted)
  - Hover: border lightens, card lifts slightly

**How It Works:**
- "三步开始"
- 3 numbered steps in a row: ① 上传文档 → ② AI 分析 → ③ 下载报告
- Each step: large number (monospace), title, brief description

**Pricing Preview (teaser):**
- "简单透明的定价"
- 3 plan cards: 7天试用 (highlighted with accent border), 专业版, 企业版
- Each shows: price / month, key features (3-4 bullet points)
- CTA on trial card: "免费开始试用" (prominent)
- Link: "查看完整定价 →"

**Footer:**
- Dark, minimal
- Logo + tagline
- Links: 产品 / 定价 / 文档 / GitHub / 联系
- Copyright: © 2026 InsureAI

### 2. PRICING PAGE (/pricing):

Full pricing with detailed comparison table:

**Three plans:**

| | 免费试用 | 专业版 Pro | 企业版 Enterprise |
|---|---|---|---|
| 价格 | ¥0 / 7天 | ¥39 / 月 | ¥199 / 月 |
| 每日次数 | 100次 | 50次 | 500次 |
| 输出格式 | PDF+DOCX+MD | PDF+DOCX+MD | PDF+DOCX+MD |
| 知识库 | 只读 | 只读 | 可上传 |
| 账号数 | 1 | 1 | 5 |
| API接入 | ❌ | ❌ | ✅ |
| 支持 | 社区 | 邮件 | 优先 |

After trial: auto-downgrade to Free (3/day, MD only)

**Payment buttons:**
- Pro card: Lemon Squeezy checkout link → "升级专业版"
- Enterprise card: Lemon Squeezy checkout link → "升级企业版"
- After payment: call POST {VITE_API_BASE_URL}/api/v1/auth/plan/upgrade

**Feature comparison table below cards** — all features listed with checkmarks.

### 3. AUTH PAGES (/auth/login, /auth/register):

Clean centered card on dark background.
- Title: "登录" / "注册"
- Fields: 邮箱 + 密码 (+ 确认密码 for register)
- Submit button: accent color
- Link: "还没有账号？免费试用7天 →" / "已有账号？登录 →"
- After register: auto-register on backend, redirect to dashboard with trial active
- Supabase Auth for email/password

### 4. DASHBOARD (/dashboard) — Protected, requires auth:

**Layout:** Left sidebar (collapsible) + main content

**Sidebar (dark, #0A0A0B):**
- Top: "InsureAI" logo/text
- Nav items with icons: 工作台 / 新业务 / 核保 / 出单 / 服务 / 理赔 / 续保 / 历史 / 知识库 / 设置
- Active item: accent color left border + lighter background
- Bottom: user avatar + email + plan badge + 退出

**Main Content:**
- Welcome: "你好，[用户名]" + trial days left badge
- Trial banner (if on trial): "🎉 试用期还剩 X 天 — 升级专业版，解锁永久访问" with "升级 →" button

- 4 stat cards in a row:
  - 已处理文档 (total_requests)
  - 今日剩余 (remaining_today / daily_limit)
  - 当前套餐 (plan name with colored badge: 金色试用 / 蓝色Pro / 紫色企业 / 灰色免费)
  - 试用剩余天数 (trial_days_left, only shown during trial)

- Quick Actions: 6 square icon buttons linking to each tool

- Recent Documents table (fetched from documents history):
  - Columns: 文件名 / 环节 / 日期 / 状态 / 操作
  - Status badges: 完成 / 处理中 / 失败

- Weekly usage bar chart (Recharts)

**Data from backend:**
- GET {API_BASE}/api/v1/auth/quota → stats + trial info
- Sync user on first login: POST {API_BASE}/api/v1/auth/register

### 5. TOOL PAGES (same layout for all 6):

**Page: Left Panel (35%) | Right Panel (65%)**

**Left Panel:**
- Stage icon + title
- One-line description
- File drop zone: dashed border, "拖拽文件或点击上传" (PDF/DOCX/TXT/PNG)
- OR textarea: "或直接粘贴文本..."
- Stage-specific optional fields (same as before)
- "开始分析" button (accent, full-width)
- Processing: animated skeleton loader with "AI 分析中..." text

**Right Panel:**
- Tabs: 预览 | Markdown原文 | 下载
- Preview: rendered markdown with dark-themed typography
- Markdown: raw text in monospace, copy button
- Download: PDF / DOCX / MD buttons
- Empty state: "分析结果将在此显示" with subtle icon

**API call:**
POST {API_BASE}/api/v1/{stage}/analyze
Authorization: Bearer {supabase_jwt}
FormData: file + text + context fields + provider + model

**Error handling:**
- 429 (quota exceeded): show upgrade modal with "今日次数已用完" + pricing link
- 401: redirect to login
- Network error: "网络连接失败，请重试" toast
- File too large: "文件大小超过限制" toast

### 6. KNOWLEDGE BASE PAGE (/knowledge-base) — Protected:

Three tabs: 投喂知识 | 检索测试 | 统计

**Tab 1 — Upload:**
- File upload zone (+ PDF/DOCX/TXT/MD)
- Category dropdown: 保单条款库 / 核保指南库 / 理赔规则库 / 监管法规库 / 行业基准库
- Source label input
- "投喂到知识库" button
- Success: show "✅ 已添加 X 个知识块"
- Also: text area for direct paste + "添加到知识库" button

**Tab 2 — Search Test:**
- Search input + category filter
- Results: cards showing category, relevance score, content, source
- "这是 Agent 实际使用的检索能力"

**Tab 3 — Stats:**
- 5 metric cards (one per category)
- Total knowledge chunks count
- "重新注入种子数据" button (calls seed endpoint)

**API calls:**
- Upload: POST {API_BASE}/api/v1/kb/upload
- Add text: POST {API_BASE}/api/v1/kb/add-text
- Search: POST {API_BASE}/api/v1/kb/search
- Stats: GET {API_BASE}/api/v1/kb/stats

### 7. HISTORY PAGE (/history):
- Paginated table: 日期 | 文件名 | 环节 | 状态 | 操作
- Filter by stage, search by filename
- Download past results

### 8. SETTINGS PAGE (/settings):
- Profile: name (editable), email (read-only), avatar
- Plan: current plan badge + trial days left + "升级套餐" → /pricing
- API Keys: generate/manage
- LLM Config: provider dropdown (千问/DeepSeek/OpenAI/Claude) + model + API key override
- Danger: "删除账号" with confirmation modal

---

## GLOBAL ELEMENTS:

**Language Toggle:** 中 | EN in header. Toggles all text between Chinese and English. Persists to localStorage.

**Trial Banner:** On dashboard (and subtly on tool pages): "🎉 试用期剩余 X 天" with countdown feel. When trial ends: show upgrade prompt.

**Quota Modal:** When user hits daily limit, show modal: "今日次数已用完" with plan comparison and upgrade CTA.

**Footer:** Every page has a minimal dark footer.

---

## TECHNICAL:

- TanStack Start (React 19 + Vite) — keep existing architecture
- Tailwind CSS for styling
- Supabase Auth for authentication
- Lemon Squeezy for payment processing
- React Query for server state
- Zustand for client state (language preference, UI state)
- shadcn/ui dark theme components
- All API calls to: {VITE_API_BASE_URL}
- i18n: use a simple React Context + JSON translation files (zh.json, en.json). Do NOT use next-intl or complex i18n libraries. Store strings in a single translations object.

Start building from the landing page. Make it look incredibly premium — dark, minimal, with the single accent color used sparingly for maximum impact.
