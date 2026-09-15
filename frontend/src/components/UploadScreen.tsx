import { useEffect, useState, type ChangeEvent } from "react"
import { uploadPhoto } from "../api"
import type { ItemFields } from "../types"

interface UploadScreenProps {
  onExtracted: (item: ItemFields) => void
}

export function UploadScreen({ onExtracted }: UploadScreenProps) {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!file) return
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setError(null)
    setFile(e.target.files?.[0] ?? null)
  }

  async function handleExtract() {
    if (!file) return
    setIsUploading(true)
    setError(null)
    try {
      const item = await uploadPhoto(file)
      onExtracted(item)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 p-4">
      <h1 className="text-2xl font-semibold text-slate-800">Log a Found Item</h1>

      <label className="flex w-full max-w-sm cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-white p-6 text-slate-500">
        <span>{file ? file.name : "Tap to take or choose a photo"}</span>
        <input
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleFileChange}
        />
      </label>

      {previewUrl && (
        <img
          src={previewUrl}
          alt="Selected item"
          className="w-full max-w-sm rounded-xl object-cover"
        />
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="button"
        disabled={!file || isUploading}
        onClick={handleExtract}
        className="w-full max-w-sm rounded-lg bg-slate-800 py-3 font-medium text-white disabled:opacity-40"
      >
        {isUploading ? "Extracting…" : "Extract Details"}
      </button>
    </main>
  )
}
