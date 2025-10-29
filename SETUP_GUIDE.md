# OpsGuide Backend - Quick Start for Demo

## Prerequisites
- Python 3.11+ installed (`python3 --version`)
- Terminal/Command line access

## Setup & Run (3 steps)

1. **Install dependencies** (one-time setup):
   ```bash
   ./start-server.sh
   ```
   The script will automatically:
   - Create a virtual environment
   - Install required packages (pydantic)
   - Start the server

2. **Server will start on**: `http://localhost:8093`

3. **Test it works**:
   ```bash
   curl http://localhost:8093/health
   ```
   Should return: `{"status": "healthy", ...}`

## What to Expect
- Server runs in the foreground (keep terminal open)
- Press `Ctrl+C` to stop
- Server handles operational requests like:
  - `cancel case CASE-2024-TEST-001`
  - `cancel order ORDER-2024-001`
  - `change order status to completed`

## Troubleshooting

**Port 8093 already in use?**
```bash
lsof -ti:8093 | xargs kill -9
```

**Python not found?**
```bash
brew install python3  # macOS
# or download from python.org
```

---

**Next Step**: Start the UI (see `ops-guide-ui` repo)

