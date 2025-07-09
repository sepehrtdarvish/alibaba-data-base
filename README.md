# 🎫 Alibaba Ticket Reservation Backend API

This repository contains the backend implementation of **Alibaba**, an online ticket reservation and sales platform. It provides a robust, secure, and scalable RESTful API for managing users, reservations, payments, and reporting.

---

## 🚀 Core Features

- 🔐 **User Authentication** via OTP (One-Time Password)
- 🚌 **Ticketing System** with vehicle and station management
- 📅 **Reservation Workflow** with refund and cancellation support
- 🧾 **Company Owner Registration** and trip management
- 💰 **Wallet-based Payments** and transaction tracking
- 📊 **Report Generation** for admins and company owners
- ⚡ **High-Performance Caching** using Redis (e.g., OTPs, profile data)

---

## 🧱 Technology Stack

| Component       | Description                          |
|----------------|--------------------------------------|
| **Django** + **DRF** | Backend web framework & RESTful API |
| **PostgreSQL**  | Primary relational database         |
| **Redis**       | In-memory caching for performance   |
| **Celery**      | Asynchronous task queue (e.g., OTP expiry) |
| **JWT**         | Secure token-based authentication   |
| **Docker**      | Containerized deployment & services |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sepehrtdarvish/alibaba-data-base.git
cd alibaba-data-base

