// 新业务 API
import { createServerFn } from "@tanstack/start";
import { qwenChat } from "../../lib/qwen";
import { buildAgentPrompt } from "../../lib/agents";
import { searchKB, formatKBForPrompt } from "../../lib/kb";
import { consumeQuota } from "../../lib/quota";

export const analyzeNewBusiness = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { text, additionalNotes, userId } = data;
    await consumeQuota(userId);

    const kbResults = await searchKB(`${text} 投保 新业务`, userId, 4);
    const kbContext = formatKBForPrompt(kbResults);

    const { system, user } = buildAgentPrompt("new-business", text, { additionalNotes }, kbContext);
    const output = await qwenChat([
      { role: "system", content: system },
      { role: "user", content: user },
    ]);

    return { success: true, markdown: output, kbSources: kbResults.map((r) => ({ category: r.category, source: r.source, score: r.similarity })) };
  });
