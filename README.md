# 🦅 HawkEye - Website Monitoring & Alerting Platform

## Overview

HawkEye is an automated website monitoring platform that continuously checks the health and availability of critical web applications.

The solution combines **GitHub Actions**, **FastCron**, **Prometheus**, **Blackbox Exporter**, and **Grafana** to provide:

- Automated health checks
- Real-time monitoring
- Email alerts
- Historical metrics
- Interactive dashboards

The monitoring workflow executes every 5 minutes through FastCron while Prometheus continuously probes the same endpoints for visualization in Grafana.

---

# Features

- Automated website health monitoring
- GitHub Actions based serverless execution
- FastCron scheduling
- Concurrent URL monitoring using Python AsyncIO
- Email alerts with CSV attachment
- Prometheus metrics collection
- Blackbox Exporter HTTP probing
- Grafana dashboards
- Historical uptime visualization
- Secure secret management using GitHub Secrets
- Proxy support for region-specific monitoring
- Lightweight and cost-effective deployment

---

# System Architecture

```text
                      +--------------------+
                      |     FastCron       |
                      | Every 5 Minutes    |
                      +---------+----------+
                                |
                                |
                    repository_dispatch
                                |
                                ▼
                    +----------------------+
                    | GitHub Repository    |
                    |      HawkEye         |
                    +----------+-----------+
                               |
                               ▼
                    GitHub Actions Workflow
                               |
                    Execute check_urls.py
                               |
              +----------------+----------------+
              |                                 |
              |                                 |
       Check Multiple URLs             Read GitHub Secrets
       using AsyncIO                  Email / Proxy Config
              |                                 |
              +----------------+----------------+
                               |
                               ▼
                     Any Website Down?
                     /              \
                   Yes              No
                    |                |
                    ▼                ▼
            Generate CSV        Log Success
            Send Email Alert

------------------------------------------------------------

                 Local Monitoring Stack

                 +---------------------+
                 |  Blackbox Exporter  |
                 +----------+----------+
                            |
                            |
                  HTTP Probes Every 30s
                            |
                            ▼
                    +---------------+
                    | Prometheus    |
                    +-------+-------+
                            |
                            ▼
                    +---------------+
                    | Grafana       |
                    +---------------+

          Dashboards • Metrics • Availability
```

---

# Monitoring Components

## 1. GitHub Actions

Responsible for:

- Running every 5 minutes
- Checking website availability
- Sending email alerts
- Generating CSV reports

---

## 2. FastCron

Triggers GitHub Actions every 5 minutes using Repository Dispatch API.

---

## 3. Prometheus

Continuously scrapes Blackbox Exporter to collect:

- Website availability
- Response time
- HTTP status
- SSL metrics

---

## 4. Blackbox Exporter

Performs HTTP endpoint probing for all monitored URLs.

Collected metrics include:

- probe_success
- probe_http_status_code
- probe_duration_seconds
- probe_ssl_earliest_cert_expiry
- probe_dns_lookup_time_seconds

---

## 5. Grafana

Visualizes Prometheus metrics through interactive dashboards.

Dashboard includes:

- Website Status
- HTTP Status Code
- Response Time
- Historical Availability
- Uptime Monitoring

---

# Workflow

## Alerting Workflow

```text
FastCron
    │
    ▼
GitHub Actions
    │
    ▼
check_urls.py
    │
    ▼
Check URLs
    │
    ▼
Any Failed?
 ┌──────┴──────┐
 │             │
Yes           No
 │             │
 ▼             ▼
CSV Report   Exit
 │
 ▼
Email Alert
```

---

## Monitoring Workflow

```text
Prometheus
      │
      ▼
Blackbox Exporter
      │
      ▼
Probe URLs
      │
      ▼
Store Metrics
      │
      ▼
Grafana Dashboard
```

---

# Project Structure

```text
HawkEye/
│
├── .github/
│   └── workflows/
│       └── monitor.yml
│
├── images/
│
├── check_urls.py
├── docker-compose.yml
├── prometheus.yml
├── run_loop.sh
└── README.md
```

---

# Technologies Used

- Python 3.11
- AsyncIO
- aiohttp
- GitHub Actions
- FastCron
- Prometheus
- Blackbox Exporter
- Grafana
- Docker
- Docker Compose
- SMTP (Gmail)

---

# GitHub Secrets

| Secret | Description |
|----------|-------------|
| GMAIL_USER | Sender email |
| GMAIL_PASS | Gmail App Password |
| INDIAN_PROXY | HTTP/HTTPS Proxy |

---

# Prometheus Targets

Current monitored URLs include:

- https://shivalik.bank.in/
- https://shivalik.bank.in/open-account
- https://shivalik.bank.in/unclaimed-deposits
- https://netbanking.shivalik.bank.in/
- https://matm.shivalikbank.com/GreenPinWeb/

---

# FastCron Configuration

Method

```
POST
```

Endpoint

```
https://api.github.com/repos/CODE-X-ABHIJIT/HawkEye/dispatches
```

Headers

```text
Authorization: Bearer <GitHub PAT>
Accept: application/vnd.github+json
Content-Type: application/json
```

Body

```json
{
  "event_type": "trigger-monitor"
}
```

---

# Grafana Dashboard

The Grafana dashboard displays:

- Website Availability
- HTTP Status Codes
- Probe Success
- Response Time
- Historical Trends
- Uptime Monitoring

---

# Email Notifications

If any monitored website fails:

- Email notification is sent
- Failed URLs are listed
- Timestamp included
- CSV report attached

When all services are healthy:

```
All links healthy (200 OK). Skipping save and email.
```

---

# Future Enhancements

- Slack Notifications
- Microsoft Teams Alerts
- Telegram Bot
- SMS Alerts
- Daily Health Reports
- Kubernetes Deployment
- AWS ECS Deployment
- AWS Lambda Monitoring
- SSL Certificate Expiry Alerts
- Multi-region Monitoring
- Retry with Exponential Backoff

---

# Author

**Abhijit Sahu**

AWS | Kubernetes | Docker | Jenkins | Git | Prometheus | Grafana

---

# License

This project is intended for educational purposes, DevOps learning, and infrastructure monitoring.
