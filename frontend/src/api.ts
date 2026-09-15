import type { ItemFields } from "./types"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
const API_KEY = import.meta.env.VITE_API_KEY

export async function uploadPhoto(file: File): Promise<ItemFields> {
  const formData = new FormData()
  formData.append("photo", file)

  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    headers: { "X-API-Key": API_KEY },
    body: formData,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Upload failed (${res.status})`)
  }

  return res.json()
}
