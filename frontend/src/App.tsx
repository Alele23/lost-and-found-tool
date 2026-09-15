import { useState } from "react"
import { ReviewScreen } from "./components/ReviewScreen"
import { UploadScreen } from "./components/UploadScreen"
import type { ItemFields } from "./types"

type Screen =
  | { name: "upload" }
  | { name: "review"; item: ItemFields }
  | { name: "saved"; item: ItemFields }

function App() {
  const [screen, setScreen] = useState<Screen>({ name: "upload" })

  if (screen.name === "review") {
    return (
      <ReviewScreen
        item={screen.item}
        onSaved={(item) => setScreen({ name: "saved", item })}
      />
    )
  }

  if (screen.name === "saved") {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 p-4">
        <p className="text-xl font-semibold text-slate-800">Saved ✓</p>
        <p className="text-sm text-slate-600">{screen.item.item_description}</p>
        <button
          type="button"
          onClick={() => setScreen({ name: "upload" })}
          className="w-full max-w-sm rounded-lg bg-slate-800 py-3 font-medium text-white"
        >
          Log Another Item
        </button>
      </main>
    )
  }

  return <UploadScreen onExtracted={(item) => setScreen({ name: "review", item })} />
}

export default App
