# Zora Web MVP

Web MVP interface for Zora Brain - Theory of Everything assistant.

## Features

- Chat interface for querying Zora Brain
- Source citations with confidence tags
- Claim type indicators (Proven/Derived/Modeled/Conjectural/Narrative)
- Beautiful, modern UI

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Make sure Zora Brain backend is running on port 8001:
```bash
cd ../zora-brain-backend
python zora_brain_api.py
```

4. Open http://localhost:3000 in your browser

## Build for Production

```bash
npm run build
npm start
```

## Tech Stack

- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS
- Axios (for API calls)

## API Integration

The web app connects to the Zora Brain backend API at `http://localhost:8001/query`.

See `zora-brain-backend/README.md` for API documentation.
