# NDR Console — Frontend

React + TypeScript dashboard for the **First To Win NDR** project. Built with Vite, Tailwind, TanStack Query, Recharts, and React Hook Form + Zod.

## Run locally

```bash
cd frontend
npm install
cp .env.example .env   # leave VITE_USE_MOCK=true to work without backend
npm run dev
```

Open <http://localhost:3000>. With `VITE_USE_MOCK=true` the app ships with realistic SOC data — alerts, sensors, rules, logs and a simulated real-time stream.

When the backend is up, set `VITE_USE_MOCK=false`. The dev server proxies `/api/*` to `http://localhost:8000` (configured in `vite.config.ts`).

## Structure

```
src/
  components/      # Layout, UI primitives, charts, domain widgets
  contexts/        # AuthProvider, ToastProvider
  hooks/           # useRealtimeAlerts (SSE / mock)
  lib/             # cn(), date helpers, validators
  pages/           # Login, Register, Dashboard, Alerts, Rules, Sensors, Logs
  services/        # axios client + per-resource API + mock fallback
  types/           # Shared TS types matching the backend contract
```

## What's wired up

- **Login / register** with JWT token persistence and protected routes
- **Dashboard** — KPI cards, alerts-over-time area chart, severity pie, top noisy IPs, recent alerts feed
- **Alerts** — paginated table with filters (severity, status, free-text), detail drawer with OSINT enrichment, acknowledge / resolve
- **Rules** — CRUD with Zod validation (IPv4/CIDR, port 0–65535)
- **Sensors** — register with one-time API-key reveal, status badges, packet counters
- **Logs** — raw log viewer with pagination + filter
- **Real-time** — `useRealtimeAlerts` connects to `/api/alerts/stream` (SSE) in production; emits a synthetic alert every 12s in mock mode

## Backend contract used

Matches `NDR_Plan_Projektu.docx` §6:
- `POST /api/auth/login`, `POST /api/auth/register`
- `GET/POST /api/sensors`, `DELETE /api/sensors/:id`
- `GET /api/logs` (paginated)
- `GET/POST/PUT/DELETE /api/rules`
- `GET /api/alerts`, `PATCH /api/alerts/:id`, `GET /api/alerts/:id/osint`
- `GET /api/dashboard/stats`
- `GET /api/alerts/stream` (SSE, optional)

## Build for production

```bash
npm run build       # outputs to dist/
npm run preview     # serve the build locally
```

A `Dockerfile` (multi-stage, Nginx) and `nginx.conf` are included for the docker-compose setup.
