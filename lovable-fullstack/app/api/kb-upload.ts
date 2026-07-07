// 知识库上传 API
import { createServerFn } from "@tanstack/start";
import { addToKB } from "../../lib/kb";
import { chunkText } from "../../lib/parser";

export const uploadToKB = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { text, category, source, userId } = data;

    const chunks = chunkText(text, 800);
    const kbChunks = chunks.map((c) => ({
      content: c,
      source: source || "manual",
      category: category || "policy_clauses",
      user_id: userId,
    }));

    const count = await addToKB(kbChunks);

    return {
      status: "ok",
      chunksAdded: count,
      category,
      textLength: text.length,
    };
  });
