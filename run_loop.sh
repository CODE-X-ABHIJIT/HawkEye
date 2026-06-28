#!/data/data/com.termux/files/usr/bin/bash
# Keep Android CPU awake during execution
termux-wake-lock

echo "Starting 5-minute loop... [Press Ctrl+C to stop]"

while true; do
    python check_urls.py
    sleep 300
done

