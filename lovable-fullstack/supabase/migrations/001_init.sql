-- Supabase 数据库初始化 — 知识库 + 用户配额

-- 1. 启用 pgvector 扩展（在 Supabase SQL Editor 里执行）
-- create extension if not exists vector;

-- 2. 知识库表
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    source TEXT DEFAULT 'manual',
    category TEXT DEFAULT 'policy_clauses',
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 为知识库创建向量索引
CREATE INDEX IF NOT EXISTS idx_kb_embedding
ON knowledge_base
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 4. 为用户私有知识创建索引
CREATE INDEX IF NOT EXISTS idx_kb_user_id ON knowledge_base(user_id);
CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_base(category);

-- 5. 向量相似度搜索函数
CREATE OR REPLACE FUNCTION match_knowledge(
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT,
    filter_user_id UUID,
    filter_category TEXT
)
RETURNS TABLE(
    id UUID,
    content TEXT,
    source TEXT,
    category TEXT,
    user_id UUID,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        kb.id,
        kb.content,
        kb.source,
        kb.category,
        kb.user_id,
        1 - (kb.embedding <=> query_embedding) AS similarity
    FROM knowledge_base kb
    WHERE
        (filter_user_id IS NULL OR kb.user_id = filter_user_id)
        AND (filter_category IS NULL OR kb.category = filter_category)
        AND 1 - (kb.embedding <=> query_embedding) > match_threshold
    ORDER BY kb.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 6. profiles 表（扩展 Supabase auth.users）
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT,
    plan TEXT DEFAULT 'trial',
    daily_requests INT DEFAULT 0,
    total_requests INT DEFAULT 0,
    request_date DATE DEFAULT CURRENT_DATE,
    trial_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. profiles 触发器 — 注册时自动创建
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, plan, trial_start)
    VALUES (NEW.id, NEW.email, 'trial', NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 8. 文档历史表
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT,
    stage TEXT,
    input_text TEXT,
    output_markdown TEXT,
    kb_sources JSONB,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. 行级安全策略 (RLS)
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 用户只能看到自己的私有知识 + 公共知识
CREATE POLICY "Users can view their own and public knowledge"
ON knowledge_base FOR SELECT
TO authenticated
USING (user_id = auth.uid() OR user_id IS NULL);

-- 用户只能上传自己的知识
CREATE POLICY "Users can insert their own knowledge"
ON knowledge_base FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());

-- 用户只能看到自己的 profile
CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
TO authenticated
USING (id = auth.uid());

CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
TO authenticated
USING (id = auth.uid());

-- 用户只能看到自己的文档
CREATE POLICY "Users can view own documents"
ON documents FOR SELECT
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can insert own documents"
ON documents FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());
