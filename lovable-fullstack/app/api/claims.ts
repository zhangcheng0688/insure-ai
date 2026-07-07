// 理赔 API — Claims Agent + RAG
import { createServerFn } from "@tanstack/start";
import { qwenChat } from "../../lib/qwen";
import { buildAgentPrompt } from "../../lib/agents";
import { searchKB, formatKBForPrompt } from "../../lib/kb";
import { consumeQuota } from "../../lib/quota";

export const analyzeClaim = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { text, policyWording, claimType, userId } = data;

    // 1. 检查配额
    await consumeQuota(userId);

    // 2. 知识库检索
    const kbResults = await searchKB(
      `${text} ${claimType || ""} 理赔`,
      userId,
      5
    );
    const kbContext = formatKBForPrompt(kbResults);

    // 3. 构建 Prompt
    const { system, user } = buildAgentPrompt(
      "claims",
      text,
      { policyWording, claimType },
      kbContext
    );

    // 4. 调用千问
    const output = await qwenChat([
      { role: "system", content: system },
      { role: "user", content: user },
    ]);

    return {
      success: true,
      markdown: output,
      kbSources: kbResults.map((r) => ({
        category: r.category,
        source: r.source,
        score: r.similarity,
      })),
    };
  });
