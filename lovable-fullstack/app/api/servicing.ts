// 保单服务 API
import { createServerFn } from "@tanstack/start";
import { qwenChat } from "../../lib/qwen";
import { buildAgentPrompt } from "../../lib/agents";
import { searchKB, formatKBForPrompt } from "../../lib/kb";
import { consumeQuota } from "../../lib/quota";

export const processServicing = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { text, requestType, clientName, policyNumber, userId } = data;
    await consumeQuota(userId);

    const kbResults = await searchKB(`${text} ${requestType || ""} 服务 COI`, userId, 3);
    const kbContext = formatKBForPrompt(kbResults);

    const { system, user } = buildAgentPrompt("servicing", text, { requestType, clientName, policyNumber }, kbContext);
    const output = await qwenChat([
      { role: "system", content: system },
      { role: "user", content: user },
    ]);

    return { success: true, markdown: output, kbSources: kbResults.map((r) => ({ category: r.category, source: r.source, score: r.similarity })) };
  });
