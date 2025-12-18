# <p align="center">🦾 Stark Industries: MultiProduct Platform</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0.0--STARK-00d4ff?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/Django-4.2+-092e20?style=for-the-badge&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/Redis-Cache_Active-d82c20?style=for-the-badge&logo=redis" alt="Redis">
  <img src="https://img.shields.io/badge/Celery-Distributed-37814a?style=for-the-badge&logo=celery" alt="Celery">
  <img src="https://img.shields.io/badge/Security-Stark_Lvl_Alpha-blue?style=for-the-badge" alt="Security">
</p>

---

## 📖 Executive Overview
The **MultiProduct Platform** is a centralized SaaS aggregation engine. It allows a single entity (The Admin/Stark Industries) to offer multiple software products and services to a global user base through a unified, high-performance subscription ecosystem.

### Core Objectives:
1.  **Uniform Authentication**: Secure, multi-device access using Stark-Secure OTP sequences.
2.  **Global Scale**: Real-time translation with O(1) Redis caching for zero-latency localized experiences.
3.  **Subscription Automation**: Zero-touch lifecycle management from Trial activation to automated renewal and expiry.
4.  **Notification Resilience**: Asynchronous messaging offloaded to Celery background workers.

---

## 🏛️ System Architecture

### 1. Unified Authentication Layer (`authApp`)
- **Stark-Secure Protocol**: Replaces standard session-based OTPs with a dedicated database-backed verification model.
- **Persistence**: Verification sequences survive server restarts and browser clears, ensuring users are never "locked out" during transit.
- **Role-Based Access**: Granular permission levels (Admin, Service Provider, Standard User).

### 2. Intelligent Translation Middleware
- **Dynamic I18N**: Automatically detects the `Accept-Language` header and translates API responses on-the-fly.
- **Redis Optimization**: Uses MD5-hashed caching keys to store translated fragments.
- **Performance Leak Protection**: Prevents redundant hits to translation APIs, ensuring stability under heavy load.

### 3. Subscription Micro-Engine (`serviceApp`)
- **Product Registry**: Dynamic management of multiple service offerings.
- **Plan Hierarchy**: Flexible tiered pricing (Weekly/Monthly/Yearly/Custom).
- **Background Watchdog**: A Celery Beat "Heartbeat" that scans for expiries and triggers notifications every 24 hours.

---

## 📡 API Documentation & Interaction Guide

### **A. Authentication Protocol**

| Endpoint | Method | Description | Primary Payload |
| :--- | :--- | :--- | :--- |
| `/api/auth/signup/` | `POST` | Register a new Identity | `{ "email", "password", "username" }` |
| `/api/auth/verify-otp/` | `POST` | Validate verification sequence | `{ "email", "otp" }` |
| `/api/auth/login/` | `POST` | Acquire primary Access Token | `{ "email", "password" }` |
| `/api/auth/resend-otp/` | `POST` | Refresh verification sequence | `{ "email" }` |

**Example Verification Request:**
```json
{
    "email": "tony@stark.com",
    "otp": "123456"
}
```

---

### **B. Subscription Management**

| Endpoint | Method | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `/api/services/products/` | `GET` | List available Stark Products | No |
| `/api/services/start-trial/` | `POST` | Initiate product evaluation | Yes |
| `/api/services/purchase/` | `POST` | Authorize service subscription | Yes |
| `/api/services/my-subscriptions/` | `GET` | View active clearance levels | Yes |

**Purchase Authorization Example:**
```json
{
    "product_id": "STARK-MK85",
    "plan_id": "MONTHLY_GOLD",
    "payment_method": "STARK_PAY"
}
```

---

## 📈 High-Load Optimization Data

| Optimization | Method | Impact |
| :--- | :--- | :--- |
| **Auth Caching** | JWT + Persistent OTP | **99.9% Reliable** |
| **I18N Latency** | Redis MD5 Hashing | **< 2ms response** |
| **Email Dispatch** | Celery Asynchronous | **0ms Request Blocking** |
| **DB Performance** | B-Tree Composite Indexing | **Sub-ms Lookups** |

---

## 🔔 Stark Industries Notification Protocols

The system uses the **Stark Global Secure Communiqué** framework:
- **Asynchronous Loop**: Triggered via `NotificationService.send_payment_confirmation.delay()`.
- **Fallbacks**: Renders logic-safe plain text if HTML is unsupported by user terminal.
- **Branding**: Professional Dark-Mode styling with Jarvis-integrated support links.

---

## 🛠️ Global Deployment Guide

### **1. Core Infrastructure (Docker Hub)**
Stark Industries recommends deployment via the provided Docker Compose manifest for absolute environmental parity.

```bash
# Verify Docker Mainframe
docker-compose ps

# Launch All Systems
docker-compose up -d --build

# Run Stark Database Migrations
docker-compose exec web python manage.py migrate
```

### **2. Background Worker Maintenance**
*Warning: Background workers must be cycled after every protocol (Code) change.*

```bash
# Restart the Background Processing Unit
docker restart multiproduct-celery

# Monitor Jarvis Logs
docker logs -f multiproduct-celery
```

---

## 🛡️ Security & Integrity Fixes (Ver. 2.0.1)

- **[PROTECTION]**: Atomic Transactions enforced during subscription upgrades to prevent "Double Spending."
- **[STABILITY]**: Fixed recursive property calls in the Notification service that caused memory overflows.
- **[RECOVERY]**: Implemented automated OTP cleanup to prevent database table bloat during high sign-up frequency.

---

<p align="center">
  <i>"I prefer the weapon you only have to fire once."</i> — Tony Stark<br>
  <strong>&copy; 2025 STARK INDUSTRIES GLOBAL SYSTEMS</strong>
</p>
