// Supabase pgvector 知识库封装
import { createClient } from "@supabase/supabase-js";
import { qwenEmbed } from "./qwen";

const supabaseUrl = process.env.VITE_SUPABASE_URL!;
const supabaseKey = process.env.VITE_SUPABASE_SERVICE_ROLE_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);

export interface KnowledgeChunk {
  id?: string;
  content: string;
  source: string;
  category: string;
  user_id: string | null; // null = 公共库
  embedding?: number[];
}

export async function addToKB(chunks: KnowledgeChunk[]) {
  const embeddings = await qwenEmbed(chunks.map((c) => c.content));

  const rows = chunks.map((c, i) => ({
    content: c.content,
    source: c.source,
    category: c.category,
    user_id: c.user_id,
    embedding: embeddings[i],
  }));

  const { error } = await supabase.from("knowledge_base").insert(rows);
  if (error) throw error;
  return rows.length;
}

export async function searchKB(
  query: string,
  userId: string | null,
  topK = 5,
  category?: string
) {
  const queryEmbedding = (await qwenEmbed([query]))[0];

  // 先搜用户私有库
  let privateResults: any[] = [];
  if (userId) {
    const { data } = await supabase.rpc("match_knowledge", {
      query_embedding: queryEmbedding,
      match_threshold: 0.3,
      match_count: topK,
      filter_user_id: userId,
      filter_category: category || null,
    });
    privateResults = data || [];
  }

  // 再搜公共库
  const { data: publicData } = await supabase.rpc("match_knowledge", {
    query_embedding: queryEmbedding,
    match_threshold: 0.3,
    match_count: topK,
    filter_user_id: null,
    filter_category: category || null,
  });
  const publicResults = publicData || [];

  // 合并、去重、排序
  const combined = [...privateResults, ...publicResults];
  const seen = new Set();
  const unique = combined
    .filter((r) => {
      const key = r.content.slice(0, 100);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, topK);

  return unique;
}

export function formatKBForPrompt(results: any[]) {
  if (!results.length) return "";
  let lines = ["## 📚 知识库检索结果\n"];
  results.forEach((r, i) => {
    const isPrivate = r.user_id ? "【私有】" : "【公共】";
    lines.push(`### [${i + 1}] ${r.category} ${isPrivate}（相关度: ${(r.similarity * 100).toFixed(0)}%）`);
    lines.push(`> 来源: ${r.source}`);
    lines.push(r.content);
    lines.push("");
  });
  lines.push("---\n");
  return lines.join("\n");
}

export async function getKBStats(userId?: string) {
  let query = supabase.from("knowledge_base").select("category, count", { count: "exact" });
  if (userId) {
    query = query.or(`user_id.eq.${userId},user_id.is.null`);
  }
  const { data, error } = await query;
  if (error) throw error;
  return data;
}
