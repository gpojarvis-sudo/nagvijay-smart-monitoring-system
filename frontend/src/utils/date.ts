import { todayIST, timeIST } from "@/utils/date"
export function todayIST(): string {
  const now = new Date()
  const ist = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" }))
  return ist.toISOString().slice(0,10)
}

export function timeIST(): string {
  return new Date().toLocaleTimeString("en-IN", {
    timeZone: "Asia/Kolkata",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  })
}
