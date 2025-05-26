"use server";

import { cookies } from "next/headers";

export async function getMessageLimits() {
  const cookieStore = await cookies();
  const lastResetTime = cookieStore.get("lastMessageResetTime")?.value;
  const remainingMessages = cookieStore.get("remainingMessages")?.value;
  return { lastResetTime, remainingMessages };
}

export async function updateMessageLimits(remainingMessages: number) {
  const cookieStore = await cookies();
  cookieStore.set("remainingMessages", remainingMessages.toString(), {
    path: "/", 
    maxAge: 5 * 60 * 60,
    secure: process.env.NODE_ENV === "production",
    httpOnly: true,
  });
  cookieStore.set("lastMessageResetTime", Date.now().toString(), {
    path: "/",
    maxAge: 5 * 60 * 60,
    secure: process.env.NODE_ENV === "production",
    httpOnly: true,
  });
}
