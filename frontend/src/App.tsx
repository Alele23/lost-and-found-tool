import { useState } from "react"
import { UploadScreen } from "./components/UploadScreen"
import type { ItemFields } from "./types"

function App() {
  const [extracted, setExtracted] = useState<ItemFields | null>(null)

  if (extracted) {
    // Temporary stand-in until the review screen is built next.
    return (
      <main className="min-h-screen bg-slate-50 p-4">
        <h1 className="mb-2 text-lg font-semibold">Extracted (review screen goes here next)</h1>
        <pre className="whitespace-pre-wrap rounded-lg bg-white p-4 text-sm shadow">
          {JSON.stringify(extracted, null, 2)}
        </pre>
      </main>
    )
  }

  return <UploadScreen onExtracted={setExtracted} />
}

export default App
