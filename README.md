# 🦅 HawkEye - Automated Server Monitoring

## Overview

HawkEye is a lightweight server monitoring solution that periodically checks the availability of critical web applications using GitHub Actions. The workflow is triggered automatically by FastCron every five minutes, allowing continuous monitoring without maintaining any dedicated infrastructure.

Whenever a monitored website becomes unavailable or returns an unexpected HTTP status code, HawkEye generates a CSV report and sends an email notification with the affected URLs.

---

# Features

* Automated health checks every 5 minutes
* Serverless execution using GitHub Actions
* Concurrent URL monitoring using Python AsyncIO
* Email alerts with detailed status report
* CSV report generation
* Secure credential management using GitHub Secrets
* Proxy support for region-specific monitoring
* Cost-effective architecture (GitHub Actions + FastCron Free)

---

# Architecture

```text
                   +----------------------+
                   |      FastCron        |
                   |  Every 5 Minutes     |
                   +----------+-----------+
                              |
                              |
                   repository_dispatch
                              |
                              v
                +---------------------------+
                |      GitHub Repository    |
                |         HawkEye           |
                +-------------+-------------+
                              |
                              |
                     GitHub Actions
                              |
                              v
                  monitor.yml Workflow
                              |
                              |
               Install Python Dependencies
                              |
                              |
                    Execute check_urls.py
                              |
             +----------------+----------------+
             |                                 |
             |                                 |
      Check Multiple URLs               Read GitHub Secrets
     (Async HTTP Requests)      (Email & Proxy Configuration)
             |                                 |
             +----------------+----------------+
                              |
                              v
                 Are Any URLs Down?
                      /           \
                    Yes            No
                     |              |
                     |              |
           Generate CSV Report      |
                     |              |
                     |      Print "All links healthy"
                     |              
                     v              
             Send Email Alert 
```

---

# Workflow

1. FastCron triggers GitHub every 5 minutes.
2. GitHub receives a `repository_dispatch` event.
3. GitHub Actions starts the monitoring workflow.
4. Python dependencies are installed.
5. `check_urls.py` executes.
6. URLs are checked asynchronously using `aiohttp`.
7. Results are analyzed.
8. If every URL returns HTTP 200:

   * No CSV is generated.
   * No email is sent.
9. If any URL fails:

   * CSV report is created.
   * Email notification is sent with the CSV attachment.

---

# Project Structure

```text
HawkEye/
│
├── .github/
│   └── workflows/
│       └── monitor.yml
│
├── check_urls.py
├── run_loop.sh
└── README.md
```

---

# Technologies Used

* Python 3.11
* AsyncIO
* aiohttp
* GitHub Actions
* GitHub Secrets
* FastCron
* SMTP (Gmail)
* CSV Reporting

---

# GitHub Secrets

The following secrets must be configured:

| Secret       | Purpose            |
| ------------ | ------------------ |
| GMAIL_USER   | Sender Email       |
| GMAIL_PASS   | Gmail App Password |
| INDIAN_PROXY | HTTP/HTTPS Proxy   |

---

# FastCron Configuration

* Method: POST
* Interval: Every 5 Minutes
* Endpoint:

```
https://api.github.com/repos/CODE-X-ABHIJIT/HawkEye/dispatches
```

Headers:

```text
Authorization: Bearer <GitHub PAT>
Accept: application/vnd.github+json
Content-Type: application/json
```

Body:

```json
{
    "event_type": "trigger-monitor"
}
```

---

# GitHub Actions Workflow

Trigger:

```yaml
on:
  repository_dispatch:
    types:
      - trigger-monitor
```

Execution Steps:

* Checkout repository
* Setup Python
* Install dependencies
* Execute monitoring script

---

# Email Notification

When one or more URLs fail:

* CSV report is generated.
* Failed URLs are listed in the email body.
* Timestamp is recorded in IST.
* CSV file is attached.

If all monitored services are healthy:

```text
All links healthy (200 OK). Skipping save and email.
```

---

# Monitoring Logic

```
Start
   │
   ▼
Receive Trigger
   │
   ▼
Check URLs Concurrently
   │
   ▼
Collect HTTP Status
   │
   ▼
Any Failed?
 ┌───────┴────────┐
 │                │
Yes              No
 │                │
 ▼                ▼
Generate CSV   Print Success
 │
 ▼
Send Email
 │
 ▼
Finish
```

---

# Future Enhancements

* Slack Notifications
* Microsoft Teams Integration
* SMS Alerts
* Response Time Dashboard
* Database Logging
* Grafana Visualization
* Kubernetes Deployment
* AWS Lambda Migration
* Retry & Exponential Backoff
* Daily Health Reports

---

# Author

**Abhijit Sahu**

AWS | Kubernetes | Docker | Jenkins | Git 
---

# License

This project is intended for educational, learning, and infrastructure monitoring purposes.
