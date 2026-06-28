import asyncio
import aiohttp
import csv
import smtplib
import os  # Added to pull environmental values securely
from datetime import datetime, timedelta, timezone # Updated for IST timezone tracking
from http import HTTPStatus
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURATION FROM SECRETS ---
SENDER_EMAIL = os.environ.get("GMAIL_USER")
SENDER_PASSWORD = os.environ.get("GMAIL_PASS")
RECEIVER_EMAIL = "abhijitsahu570@gmail.com"
INDIAN_PROXY = os.environ.get("INDIAN_PROXY") # Added to pull your secure proxy configuration

# Your exact URLs kept completely intact
URLS = [
    "https://shivalik.bank.in/",
    "https://netbanking.shivalik.bank.in/",
    "https://smeib.shivalik.bank.in/",
    "https://matm.shivalikbank.com/GreenPinWeb/",
    "https://shivalik.bank.in/open-account",
    "https://shivalik.bank.in/unclaimed-deposits",
]

# Helper function to get the current time in IST (GMT+5:30)
def get_ist_time():
    ist_zone = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist_zone)

async def check_url(session, url, retries=2):
    target_url = url if url.startswith(("http://", "https://")) else f"https://{url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                await asyncio.sleep(2.0 * attempt)
                
            # Request line passing your Indian Proxy configuration seamlessly
            async with session.get(target_url, timeout=12, headers=headers, proxy=INDIAN_PROXY, allow_redirects=True) as response:
                code = response.status
                try:
                    meaning = HTTPStatus(code).phrase
                except ValueError:
                    meaning = "Unknown Status Code"
                return url, code, meaning
                
        except (aiohttp.ClientConnectorError, aiohttp.ClientConnectorDNSNameError):
            if attempt < retries:
                continue
            return url, "DNS_Error", "DNS Lookup Failed (Check VPN/Private DNS)"
        except asyncio.TimeoutError:
            if attempt < retries:
                continue
            return url, "Timeout", "Server took too long to respond"
        except Exception as e:
            if attempt < retries:
                continue
            error_msg = str(e) if str(e) else type(e).__name__
            return url, "Error", f"Connection failed ({error_msg})"

def send_email(file_path, filename, broken_links):
    print("Preparing to send email...")
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    current_ist = get_ist_time()
    msg['Subject'] = f"Server Monitor Update: {current_ist.strftime('%Y-%m-%d %H:%M')} IST"

    body = f"Hello,\n\nThe following monitored website(s) are reporting status anomalies (Checked at {current_ist.strftime('%H:%M:%S')} IST):\n\n"
    for url, code, meaning in broken_links:
        body += f"🛑 URL: {url}\n"
        body += f"   Status Code: {code}\n"
        body += f"   Meaning: {meaning}\n\n"

    body += "Please see the attached CSV file for the complete status report log."
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Success! Update email sent to your inbox.")
    except Exception as e:
        print(f"Failed to send email: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [check_url(session, url) for url in URLS]
        results = await asyncio.gather(*tasks)

        broken_links = [item for item in results if item[1] != 200]
        
        current_ist = get_ist_time()

        if len(broken_links) > 0:
            print(f"[{current_ist.strftime('%H:%M:%S')} IST] Status change detected. Generating log...")

            timestamp = current_ist.strftime("%Y%m%d_%H%M%S")
            filename = f'url_status_{timestamp}.csv'
            file_path = f'./{filename}'

            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Status Code', 'Meaning'])
                writer.writerows(results)

            print(f"Results saved locally to: {file_path}")
            send_email(file_path, filename, broken_links)
        else:
            print(f"[{current_ist.strftime('%H:%M:%S')} IST] All links healthy (200 OK). Skipping save and email.")

# Run the async loop
if __name__ == "__main__":
    asyncio.run(main())
    
