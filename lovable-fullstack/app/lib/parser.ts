// 文件解析 — 纯文本 + base64 PDF（简单版）
// 在浏览器/Server Function 中，PDF 解析需要特殊处理

export async function extractTextFromFile(file: File | Blob): Promise<string> {
  // 如果是文本文件，直接读取
  if (file.type.startsWith("text/") || file.type === "application/json") {
    return await file.text();
  }

  // 如果是 PDF，我们返回 base64，让前端或后端用其他方式处理
  // 在 Lovable 中，可以用 pdf-parse 库（Node.js）或在浏览器用 pdfjs-dist
  if (file.type === "application/pdf") {
    // 简单方案：提示用户 PDF 解析需要额外处理
    // 实际项目中，可以在 Server Function 中用 pdf-parse
    return "[PDF文件已上传，内容提取中...]";
  }

  // DOCX 同理
  if (file.type.includes("word") || file.type.includes("docx")) {
    return "[Word文件已上传，内容提取中...]";
  }

  return await file.text();
}

// 文本切片
export function chunkText(text: string, maxSize = 800, overlap = 100): string[] {
  const sections = text.split(/\n(?=#{1,3}\s|【[^】]+】|\d+[\.\、])/);
  const chunks: string[] = [];

  for (const section of sections) {
    const s = section.trim();
    if (!s) continue;
    if (s.length <= maxSize) {
      chunks.push(s);
    } else {
      const paragraphs = s.split("\n\n");
      let current = "";
      for (const para of paragraphs) {
        const p = para.trim();
        if (!p) continue;
        if (current.length + p.length < maxSize) {
          current += p + "\n\n";
        } else {
          if (current) chunks.push(current.trim());
          current = p.length > maxSize ? p.slice(0, maxSize) + "..." : p + "\n\n";
        }
      }
      if (current.trim()) chunks.push(current.trim());
    }
  }

  return chunks.length ? chunks : [text.slice(0, maxSize)];
}
