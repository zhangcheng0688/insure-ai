// 续保 API
import { createServerFn } from "@tanstack/start";
import { qwenChat } from "../../lib/qwen";
import { buildAgentPrompt } from "../../lib/agents";
import { searchKB, formatKBForPrompt } from "../../lib/kb";
import { consumeQuota } from "../../lib/quota";

export const analyzeRenewal = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { text, expiringPremium, renewalDate, userId } = data;
    await consumeQuota(userId);

    const kbResults = await searchKB(`${text} 续保 损失率`, userId, 5);
    const kbContext = formatKBForPrompt(kbResults);

    const { system, user } = buildAgentPrompt("renewal", text, { expiringPremium, renewalDate }, kbContext);
    const output = await qwenChat([
      { role: "system", content: system },
      { role: "user", content: user },
    ]);

    return { success: true, markdown: output, kbSources: kbResults.map((r) => ({ category: r.category, source: r.source, score: r.similarity })) };
  });
