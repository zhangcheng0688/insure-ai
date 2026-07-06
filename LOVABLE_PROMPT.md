# InsureAI — Lovable 完整建站提示词（中文版）

## 一、整体设计风格

Build a clean, bright, and professional insurance AI SaaS website. The design should feel trustworthy, modern, and premium — like a professional fintech/insurtech platform.

**Design System:**
- Primary color: Deep navy blue (#1A365D) for headers and trust elements
- Accent color: Bright blue (#2563EB) for buttons, links, active states
- Success color: Emerald green (#059669) for completed/success states
- Background: Pure white (#FFFFFF) with very light gray (#F8FAFC) alternating sections
- Cards: White with subtle shadow (shadow-sm or shadow-md), border-radius 12px
- Typography: Inter font family, clean hierarchy
- Spacing: Generous white space, 24px-48px section gaps
- Icons: Use Lucide React icons throughout
- Overall feel: Minimalist but warm — like Apple meets a professional insurance firm

**Key Design Rules:**
1. No dark mode — keep everything light and bright
2. Lots of white space between sections
3. Rounded corners on all cards (12px) and buttons (8px)
4. Subtle gradients on hero/CTA sections only
5. Professional illustrations or clean icon-based graphics (no cartoon style)
6. Responsive: mobile-first, max-width 1280px centered

---

## 二、页面清单和功能

### 1. Landing Page (首页 /)

**Hero Section:**
- Large headline: "AI-Powered Insurance Document Processing"
- Subheadline: "Automate underwriting memos, claim adjudication, renewal proposals, and more. Covering the full insurance lifecycle."
- Two CTA buttons: "Start Free" (primary) and "See How It Works" (secondary, scrolls down)
- Right side: A clean dashboard preview illustration or screenshot mockup showing a document analysis result
- Trust badges below: "500+ Insurance Professionals", "Open Source", "Multi-LLM Support"

**Features Grid (6 cards, 3x2):**
Each card has an emoji icon + title + description:
1. 📋 New Business — Read ACORD forms, extract risk details, populate worksheets
2. 🔍 Underwriting — Analyze loss runs, check carrier appetite, draft memos
3. 📄 Policy Issuance — Generate dec pages, endorsements, COI templates
4. 🔄 Servicing — Draft renewal letters, COI requests, mid-term endorsements
5. ⚠️ Claims ⭐ — FNOL summarization, policy cross-reference, adjudication memos
6. 📈 Renewal — Prior-year loss analysis, renewal applications, tailored proposals

**How It Works (3 steps):**
Step 1: Upload your insurance document (PDF, DOCX, or text)
Step 2: AI analyzes and processes the document
Step 3: Download professional reports (PDF/DOCX/Markdown)

**Pricing Preview Section:**
Brief 3-tier pricing teaser with "View Full Pricing" link

**Footer:**
- Logo + short description
- Links: Features, Pricing, Documentation, GitHub, Contact
- Copyright notice

---

### 2. Pricing Page (/pricing)

Three-tier pricing cards:

**Free Tier (¥0/month):**
- 3 document analyses per day
- Single page up to 5 pages
- Markdown output only
- Community support
- Button: "Get Started Free"

**Pro Tier (¥39/month) — Highlighted/Recommended:**
- 50 analyses per day
- Unlimited document pages
- PDF + DOCX + Markdown output
- Priority processing
- Email support
- Button: "Start Pro Trial" (prominent, filled)

**Enterprise Tier (¥199/month):**
- 5 team accounts
- 500 analyses per day
- API access
- Custom templates
- Priority support
- Button: "Contact Sales"

**Payment Integration:**
- Use Lemon Squeezy for payment processing
- Create Lemon Squeezy checkout links for Pro and Enterprise plans
- After successful payment, redirect to dashboard with upgraded account
- Store subscription status in Supabase user metadata

---

### 3. Authentication Pages

**Login Page (/auth/login):**
- Clean centered card layout
- Email + password fields
- "Log In" button
- "Don't have an account? Sign Up" link
- Social login optional (Google)

**Register Page (/auth/register):**
- Email + password + confirm password
- "Create Account" button
- "Already have an account? Log In" link
- After registration: redirect to onboarding or dashboard

---

### 4. Dashboard (/dashboard) — Requires Auth

**Layout:**
- Left sidebar navigation (collapsible)
- Main content area

**Sidebar Navigation:**
- 🏠 Dashboard (home)
- 📋 New Business
- 🔍 Underwriting
- 📄 Policy Issuance
- 🔄 Servicing
- ⚠️ Claims
- 📈 Renewal
- 📊 History
- ⚙️ Settings
- Bottom: User avatar + email + Logout

**Dashboard Main Content:**
- Welcome message: "Welcome back, [User Name]"
- Stats row (4 cards):
  - Documents Processed (number)
  - Remaining Today (X/50 for Pro, X/3 for Free)
  - Active Plan (Free / Pro / Enterprise)
  - API Calls This Month (number)
- "Quick Actions" section: 6 icon buttons linking to each tool
- "Recent Documents" table: filename, stage, date, status, download link
- Usage chart (simple bar chart of last 7 days usage)

---

### 5. Insurance Tool Pages (6 pages, same layout pattern)

Each tool page follows this pattern:

**Page Layout: Left Panel (input) | Right Panel (result)**

**Left Panel (40% width):**
- Stage icon + title at top
- Brief description of what this tool does
- File upload area (drag & drop zone, supports PDF/DOCX/TXT/PNG/JPG)
- OR paste text directly into a textarea
- Optional context fields (varies by stage, see below)
- "Start Analysis" button (prominent, primary color, full width)
- Processing state: animated progress indicator while waiting

**Right Panel (60% width):**
- Tab bar: "Preview" | "Markdown" | "Download"
- Preview tab: Rendered markdown with nice typography
- Markdown tab: Raw markdown text (copyable)
- Download tab: PDF, DOCX, Markdown download buttons
- Empty state before analysis: "Your analysis result will appear here" with gentle illustration

**Each tool's specific context fields:**

Claims Page:
- Policy Wording textarea (optional)
- Claim Type dropdown: Property Damage, Liability, Workers Comp, Auto, Professional Liability
- Reserve Authority input (optional)

Underwriting Page:
- Carrier Guidelines textarea (optional)
- Prior Year Premium input (optional)

New Business Page:
- Additional Notes textarea (optional)

Policy Issuance Page:
- Policy Number input (optional)
- Named Insured input (optional)

Servicing Page:
- Request Type dropdown: COI Request, Endorsement, Policy Change, Renewal Letter, Other
- Client Name input (optional)
- Policy Number input (optional)

Renewal Page:
- Expiring Premium input (optional)
- Renewal Date input (optional)

**API Integration:**
All tool pages call the InsureAI backend API:
- Base URL: https://your-api-domain.com/api/v1
- POST /claims/analyze, /underwriting/analyze, /new-business/analyze, etc.
- Form data with file upload + text fields
- Display returned markdown in the result panel

---

### 6. History Page (/history)

- Table of all past document analyses
- Columns: Date, Filename, Stage, Status, Actions (View/Download)
- Pagination (20 per page)
- Filter by stage (dropdown)
- Search by filename

---

### 7. Settings Page (/settings)

**Profile Section:**
- Display name, email (read-only from auth)
- Avatar upload (optional)

**API Configuration:**
- LLM Provider dropdown: OpenAI, DeepSeek, Qwen (通义千问), Anthropic
- Model selector (changes based on provider)
- API Key input (masked, optional override)

**Plan Section:**
- Current plan badge (Free/Pro/Enterprise)
- Usage stats: X/50 remaining today
- Upgrade button (links to pricing)

**Danger Zone:**
- Delete Account button (with confirmation dialog)
- Export Data button

---

### 8. API Documentation Page (/docs) — Optional

- Simple documentation for developers
- Authentication: API Key in header
- Endpoint list with example curl commands
- Rate limits by plan

---

## 三、技术集成要求

**Authentication:**
- Use Supabase Auth for user management
- Email/password authentication
- Store user plan and usage count in Supabase profiles table

**Payment (Lemon Squeezy):**
- Create products in Lemon Squeezy dashboard
- Use Lemon Squeezy.js for checkout overlay
- After payment success webhook → update Supabase user plan
- Show subscription status in dashboard

**API Calls to InsureAI Backend:**
- All insurance processing goes to our Python FastAPI backend
- Include user's plan limits check before calling AI
- Show loading states during processing
- Handle errors gracefully with toast notifications

**State Management:**
- React Context or Zustand for global state
- React Query (TanStack Query) for server state and caching

---

## 四、要在 Lovable 中使用的确切提示词

Copy and paste the entire content below into Lovable:

---

BUILD THE FOLLOWING INSURANCE AI SAAS WEBSITE:

DESIGN: Clean, bright, professional. Primary blue #1A365D, accent #2563EB. White backgrounds, generous spacing. Inter font. Lucide icons. Cards with 12px border radius and subtle shadows. No dark mode. Minimalist and premium feel — like Stripe meets an insurance platform.

PAGES TO BUILD:

1. LANDING PAGE (/):
- Hero: "AI-Powered Insurance Document Processing" with subtitle about automating the full insurance lifecycle
- 2 CTA buttons: "Start Free" and "See How It Works"
- 6 feature cards in 3x2 grid for insurance stages (New Business, Underwriting, Policy Issuance, Servicing, Claims, Renewal)
- Each card has emoji icon, title, description
- How It Works section (3 steps: Upload → AI Analyze → Download)
- Pricing preview section
- Footer with links

2. PRICING PAGE (/pricing):
- 3 cards: Free (¥0, 3/day), Pro (¥39/mo, 50/day, highlighted), Enterprise (¥199/mo, 5 seats, 500/day)
- Lemon Squeezy payment buttons for Pro and Enterprise
- Feature comparison table below cards

3. AUTH PAGES:
- /auth/login: Clean centered card, email+password, link to register
- /auth/register: Email+password+confirm, link to login
- Use Supabase Auth

4. DASHBOARD (/dashboard) — Requires authentication:
- Left sidebar with navigation to all 6 tools + History + Settings
- Stats cards: Documents processed, remaining today, active plan, monthly API calls
- Quick actions grid (6 icon cards linking to tools)
- Recent documents table
- Weekly usage bar chart

5. TOOL PAGES (6 pages, same layout):
- /tools/claims — Left panel: file upload + textarea + policy wording + claim type dropdown. Right panel: tabs (Preview/Markdown/Download) showing API result
- /tools/underwriting — Same layout, context fields: carrier guidelines + prior premium
- /tools/new-business — Same layout, context fields: additional notes
- /tools/policy-issuance — Same layout, context fields: policy number + named insured
- /tools/servicing — Same layout, context fields: request type + client name
- /tools/renewal — Same layout, context fields: expiring premium + renewal date
- Each calls our backend API at POST {API_BASE}/api/v1/{stage}/analyze with multipart form data

6. HISTORY PAGE (/history):
- Paginated table: date, filename, stage, status, actions
- Filter by stage, search by filename

7. SETTINGS PAGE (/settings):
- Profile section (name, email)
- LLM configuration (provider dropdown, model, API key)
- Plan info with upgrade button
- Delete account button

TECHNICAL:
- Next.js 14 with App Router
- Tailwind CSS for styling
- Supabase for auth and user data
- Lemon Squeezy for payments
- React Query for API calls
- Zustand for state management
- shadcn/ui components where applicable
- All API calls go to environment variable NEXT_PUBLIC_API_BASE_URL

Start building from the landing page. Make it look incredibly professional and polished.
