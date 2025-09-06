🚀 RunPod API Startup Checklist

1. Port not reachable
   • Issue: Server bound only to 127.0.0.1, so external HTTP Service didn’t work.
   • Fix: Always bind to 0.0.0.0.

python3 -m uvicorn app:app --host 0.0.0.0 --port 8000

⸻

2. Missing environment variable
   • Issue: ValueError: BTW_DOC_READER_API_KEY environment variable is required
   • Fix: Export without spaces, or set it in RunPod Template → Environment Variables.

export BTW_DOC_READER_API_KEY="doc-reader-api"

Or in start.sh:

export BTW_DOC_READER_API_KEY="doc-reader-api"

⸻

3. Address already in use
   • Issue: Old uvicorn process was still running on port 8000.
   • Fix: Find and kill it.

ss -ltnp | grep :8000
kill -9 <PID>

⸻

4. Background run & logging
   • Good practice: Run uvicorn with nohup so it survives terminal exit, and log output.

nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 >server.log 2>&1 &
tail -f server.log

⸻

5. Robust start.sh script

Create a startup script to set env vars, kill old processes, and start cleanly:

#!/bin/bash
export BTW_DOC_READER_API_KEY="doc-reader-api"

# kill old uvicorns if any

PIDS=$(lsof -t -i:8000)
if [ ! -z "$PIDS" ]; then
kill -9 $PIDS
fi

# start server

exec python3 -m uvicorn app:app --host 0.0.0.0 --port 8000

Make it executable:

chmod +x start.sh
./start.sh
