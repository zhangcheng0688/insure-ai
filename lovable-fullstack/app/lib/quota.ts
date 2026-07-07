// 配额管理 — 基于 Supabase
import { supabase } from "./kb";

export const PLANS = {
  trial: { name: "7天免费试用", dailyLimit: 100, formats: ["markdown", "pdf", "docx"] },
  free: { name: "免费版", dailyLimit: 3, formats: ["markdown"] },
  pro: { name: "专业版 Pro", dailyLimit: 50, formats: ["markdown", "pdf", "docx"] },
  enterprise: { name: "企业版 Enterprise", dailyLimit: 500, formats: ["markdown", "pdf", "docx"] },
};

export const TRIAL_DAYS = 7;

export async function getQuota(userId: string) {
  const { data: user } = await supabase
    .from("profiles")
    .select("plan, daily_requests, request_date, trial_start, total_requests")
    .eq("id", userId)
    .single();

  if (!user) throw new Error("User not found");

  // 检查试用是否过期
  let plan = user.plan;
  let trialDaysLeft = 0;

  if (plan === "trial" && user.trial_start) {
    const daysElapsed = Math.floor(
      (Date.now() - new Date(user.trial_start).getTime()) / (1000 * 60 * 60 * 24)
    );
    trialDaysLeft = Math.max(0, TRIAL_DAYS - daysElapsed);
    if (trialDaysLeft <= 0) {
      plan = "free";
      await supabase.from("profiles").update({ plan: "free" }).eq("id", userId);
    }
  }

  // 重置每日计数
  const today = new Date().toISOString().split("T")[0];
  if (user.request_date !== today) {
    await supabase
      .from("profiles")
      .update({ daily_requests: 0, request_date: today })
      .eq("id", userId);
    user.daily_requests = 0;
  }

  const planConfig = PLANS[plan as keyof typeof PLANS] || PLANS.free;

  return {
    plan,
    planName: planConfig.name,
    dailyLimit: planConfig.dailyLimit,
    usedToday: user.daily_requests || 0,
    remainingToday: Math.max(0, planConfig.dailyLimit - (user.daily_requests || 0)),
    totalRequests: user.total_requests || 0,
    formats: planConfig.formats,
    trialDaysLeft,
    isTrial: plan === "trial",
  };
}

export async function consumeQuota(userId: string) {
  const quota = await getQuota(userId);

  if (quota.remainingToday <= 0) {
    throw new Error(
      quota.isTrial
        ? `试用期每天${quota.dailyLimit}次，今日已用完。`
        : `今日${quota.dailyLimit}次已用完，升级Pro解锁每日50次。`
    );
  }

  const { error } = await supabase
    .from("profiles")
    .update({
      daily_requests: quota.usedToday + 1,
      total_requests: quota.totalRequests + 1,
    })
    .eq("id", userId);

  if (error) throw error;

  return {
    consumed: true,
    remainingToday: quota.dailyLimit - quota.usedToday - 1,
    totalRequests: quota.totalRequests + 1,
    trialDaysLeft: quota.trialDaysLeft,
  };
}
