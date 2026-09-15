import { useState, type FormEvent } from "react"
import { createItem } from "../api"
import { CATEGORIES, STATUSES, type ItemFields } from "../types"

interface ReviewScreenProps {
  item: ItemFields
  onSaved: (item: ItemFields) => void
}

const fieldClass = "rounded-lg border border-slate-300 p-2"
const labelClass = "flex flex-col gap-1 text-sm text-slate-600"

export function ReviewScreen({ item, onSaved }: ReviewScreenProps) {
  const [fields, setFields] = useState<ItemFields>(item)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function update<K extends keyof ItemFields>(key: K, value: ItemFields[K]) {
    setFields((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setIsSaving(true)
    setError(null)
    try {
      const saved = await createItem(fields)
      onSaved(saved)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center gap-4 bg-slate-50 p-4">
      <h1 className="text-2xl font-semibold text-slate-800">Review Item</h1>

      <form onSubmit={handleSubmit} className="flex w-full max-w-sm flex-col gap-3">
        <label className={labelClass}>
          Description
          <textarea
            required
            rows={3}
            value={fields.item_description}
            onChange={(e) => update("item_description", e.target.value)}
            className={fieldClass}
          />
        </label>

        <label className={labelClass}>
          Category
          <select
            value={fields.category}
            onChange={(e) => update("category", e.target.value as ItemFields["category"])}
            className={fieldClass}
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <label className={labelClass}>
          Date Found
          <input
            type="date"
            required
            value={fields.date_found}
            onChange={(e) => update("date_found", e.target.value)}
            className={fieldClass}
          />
        </label>

        <label className={labelClass}>
          Location
          <input
            type="text"
            value={fields.location}
            onChange={(e) => update("location", e.target.value)}
            className={fieldClass}
          />
        </label>

        <label className={labelClass}>
          Status
          <select
            value={fields.status}
            onChange={(e) => update("status", e.target.value as ItemFields["status"])}
            className={fieldClass}
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label className={labelClass}>
          Reported By
          <input
            type="text"
            value={fields.reported_by}
            onChange={(e) => update("reported_by", e.target.value)}
            className={fieldClass}
          />
        </label>

        <label className={labelClass}>
          Contact
          <input
            type="text"
            placeholder="Name/info found on the item, if any"
            value={fields.contact}
            onChange={(e) => update("contact", e.target.value)}
            className={fieldClass}
          />
        </label>

        <label className={labelClass}>
          Remarks
          <textarea
            rows={2}
            value={fields.remarks}
            onChange={(e) => update("remarks", e.target.value)}
            className={fieldClass}
          />
        </label>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={isSaving}
          className="w-full rounded-lg bg-slate-800 py-3 font-medium text-white disabled:opacity-40"
        >
          {isSaving ? "Saving…" : "Confirm"}
        </button>
      </form>
    </main>
  )
}
