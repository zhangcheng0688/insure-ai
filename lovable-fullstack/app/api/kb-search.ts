// 知识库搜索 API
import { createServerFn } from "@tanstack/start";
import { searchKB } from "../../lib/kb";

export const searchKnowledge = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { query, category, userId, topK = 5 } = data;

    const results = await searchKB(query, userId, topK, category);

    return {
      query,
      totalFound: results.length,
      results: results.map((r) => ({
        content: r.content,
        source: r.source,
        category: r.category,
        score: r.similarity,
        isPrivate: !!r.user_id,
      })),
    };
  });
