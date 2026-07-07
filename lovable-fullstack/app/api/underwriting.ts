// 核保 API — Underwriting Agent + RAG
import { createServerFn } from "@tanstack/start";
import { qwenChat } from "../../lib/qwen";
import { buildAgentPrompt } from "../../lib/agents";
import { searchKB, formatKBForPrompt } from "../../lib/kb";
import { consumeQuota } from "../../lib/quota";

export const analyzeUnderwriting = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { text, carrierGuidelines, priorYearPremium, userId } = data;

    await consumeQuota(userId);

    const kbResults = await searchKB(
      `${text} 核保 承保`,
      userId,
      5
    );
    const kbContext = formatKBForPrompt(kbResults);

    const { system, user } = buildAgentPrompt(
      "underwriting",
      text,
      { carrierGuidelines, priorYearPremium },
      kbContext
    );

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
