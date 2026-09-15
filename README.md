# Lost & Found Intake Tool

A photo-based intake tool for a campus lost & found desk. Staff photograph a
found item, an AI vision model extracts the key details, staff reviews and
edits the result, and the confirmed record is logged straight to a Google
Sheet — no more manually transcribing a pile of sticky notes at the end of a
shift.

## How it works

1. Staff upload a photo of a found item.
2. The photo (kept in memory, never written to disk) is sent to the backend.
3. The backend sends it to the **Google Gemini API**, which extracts a short
   description and a category.
4. The extracted fields, plus sensible defaults (today's date, status
   "Found"), are shown on an editable review screen.
5. Staff confirm or correct the fields and submit.
6. The backend appends the confirmed record as a new row in a **Google
   Sheet**.

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS |
| Backend | Python 3.13 + FastAPI |
| AI / vision | Google Gemini API (`google-genai`) |
| Data store | Google Sheets (`gspread`, service-account auth) |
| Auth | Shared `X-API-Key` header (internal staff tool, not user-level auth) |

## Project structure

```
backend/
  app/
    routers/    # HTTP endpoints (/upload, /items)
    services/   # Gemini and Google Sheets integrations
    models.py   # Shared data shapes (Pydantic)
    config.py   # Typed settings, loaded from .env
    auth.py     # API-key dependency
  tests/
frontend/
  src/
    components/ # UploadScreen, ReviewScreen
    api.ts      # Backend API client
    types.ts    # Shared data shapes (TypeScript)
```

## Running it locally

### Backend

```
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in the values below
uvicorn app.main:app --reload --port 8001
```

`.env` needs:
- `API_SECRET_KEY` — any random string; the frontend must send the same value
- `GEMINI_API_KEY` — from [Google AI Studio](https://aistudio.google.com/apikey)
- `GOOGLE_CREDENTIALS_FILE` — path to a Google service-account JSON key (must have edit access to the target sheet)
- `SHEET_ID` — the target Google Sheet's ID (from its URL)

### Frontend

```
cd frontend
npm install
cp .env.example .env   # VITE_API_KEY must match the backend's API_SECRET_KEY
npm run dev
```

## Status

The core flow above is fully working end to end. Not yet built: persistent
photo storage, a history/search view, authentication beyond the shared API
key, and deployment — all tracked as deliberate next steps, not oversights.
