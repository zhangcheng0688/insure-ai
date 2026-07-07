// 保单出单 API
import { createServerFn } from "@tanstack/start";
import { qwenChat } from "../../lib/qwen";
import { buildAgentPrompt } from "../../lib/agents";
import { searchKB, formatKBForPrompt } from "../../lib/kb";
import { consumeQuota } from "../../lib/quota";

export const generatePolicyDocs = createServerFn({ method: "POST" })
  .handler(async ({ data }: { data: any }) => {
    const { text, policyNumber, namedInsured, userId } = data;
    await consumeQuota(userId);

    const kbResults = await searchKB(`${text} 保单 出单 COI`, userId, 4);
    const kbContext = formatKBForPrompt(kbResults);

    const { system, user } = buildAgentPrompt("policy-issuance", text, { policyNumber, namedInsured }, kbContext);
    const output = await qwenChat([
      { role: "system", content: system },
      { role: "user", content: user },
    ]);

    return { success: true, markdown: output, kbSources: kbResults.map((r) => ({ category: r.category, source: r.source, score: r.similarity })) };
  });
