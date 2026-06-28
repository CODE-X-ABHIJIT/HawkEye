import asyncio
import aiohttp
import csv
import smtplib
import os  # Added to pull environmental values securely
from datetime import datetime
from http import HTTPStatus
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURATION FROM SECRETS ---
SENDER_EMAIL = os.environ.get("GMAIL_USER")
SENDER_PASSWORD = os.environ.get("GMAIL_PASS")
RECEIVER_EMAIL = "abhijitsahu570@gmail.com"

# Your exact URLs kept completely intact
URLS = [
    "https://shivalik.bank.in/",
    "https://netbanking.shivalik.bank.in/",
    "https://smeib.shivalik.bank.in/#/login",
    "https://matm.shivalikbank.com/GreenPinWeb/",
    "https://shivalik.bank.in/open-account",
    "https://shivalik.bank.in/unclaimed-deposits",
]

async def check_url(session, url, retries=2):
    target_url = url if url.startswith(("http://", "https://")) else f"https://{url}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for attempt in range(retries + 1):
        try:
            # Staggered pacing delay to stop bank firewalls from blocking Termux
            if attempt > 0:
                await asyncio.sleep(2.0 * attempt)
                
            async with session.get(target_url, timeout=12, headers=headers, allow_redirects=True) as response:
                code = response.status
                try:
                    meaning = HTTPStatus(code).phrase
                except ValueError:
                    meaning = "Unknown Status Code"
                return url, code, meaning
                
        except (aiohttp.ClientConnectorError, aiohttp.ClientConnectorDNSNameError) as dns_err:
            if attempt < retries:
                continue  # Retry to handle temporary DNS lookup stumbles
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
    # Modified Subject Line to be neutral
    msg['Subject'] = f"Server Monitor Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    body = "Hello,\n\nThe following monitored website(s) are reporting status anomalies:\n\n"
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
        # Paced task processing to prevent sudden connection drop blocking
        tasks = [check_url(session, url) for url in URLS]
        results = await asyncio.gather(*tasks)

        # Filters targets where the status is not a standard 200
        broken_links = [item for item in results if item[1] != 200]

        if len(broken_links) > 0:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[{current_time}] Status change detected. Generating log...")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'url_status_{timestamp}.csv'
            file_path = f'./{filename}'

            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Status Code', 'Meaning'])
                writer.writerows(results)

            print(f"Results saved locally to: {file_path}")
            send_email(file_path, filename, broken_links)
        else:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[{current_time}] All links healthy (200 OK). Skipping save and email.")

# Run the async loop
asyncio.run(main())
