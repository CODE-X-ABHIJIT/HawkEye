import asyncio
import time
import subprocess

def run_script():
    print("⏰ Triggering 5-minute automated bank health check...")
    # This runs your exact async script seamlessly
    subprocess.run(["python", "check_urls.py"])

if __name__ == "__main__":
    while True:
        run_script()
        print("💤 Check complete. Sleeping for 300 seconds...")
        time.sleep(300)
      
