// 千问 API 封装 — 统一调用大模型
const QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1";

export async function qwenChat(
  messages: { role: string; content: string }[],
  model = "qwen-max",
  temperature = 0.3,
  maxTokens = 4096
) {
  const apiKey = process.env.VITE_QWEN_API_KEY || process.env.QWEN_API_KEY;
  if (!apiKey) throw new Error("QWEN_API_KEY not configured");

  const resp = await fetch(`${QWEN_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model, messages, temperature, max_tokens: maxTokens }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Qwen API error: ${resp.status} ${err}`);
  }

  const data = await resp.json();
  return data.choices?.[0]?.message?.content || "";
}

export async function qwenEmbed(texts: string[], model = "text-embedding-v2") {
  const apiKey = process.env.VITE_QWEN_API_KEY || process.env.QWEN_API_KEY;
  if (!apiKey) throw new Error("QWEN_API_KEY not configured");

  const allEmbeddings: number[][] = [];
  const batchSize = 10;

  for (let i = 0; i < texts.length; i += batchSize) {
    const batch = texts.slice(i, i + batchSize);
    const resp = await fetch(`${QWEN_BASE_URL}/embeddings`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ model, input: batch }),
    });

    if (!resp.ok) throw new Error(`Embed error: ${resp.status}`);
    const data = await resp.json();
    const batchEmbeds = data.data
      .sort((a: any, b: any) => a.index - b.index)
      .map((d: any) => d.embedding);
    allEmbeddings.push(...batchEmbeds);
  }

  return allEmbeddings;
}
