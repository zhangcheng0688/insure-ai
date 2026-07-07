// 配额查询 API
import { createServerFn } from "@tanstack/start";
import { getQuota } from "../../lib/quota";

export const checkQuota = createServerFn({ method: "GET" })
  .handler(async ({ data }: { data: any }) => {
    const { userId } = data;
    return await getQuota(userId);
  });
