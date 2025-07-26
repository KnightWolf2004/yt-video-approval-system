## StreamForge: Secure Video Review & Publishing Backend (FastAPI + PostgreSQL)

A complete backend platform to manage video uploads, approvals, secure streaming, and YouTube publishing — built from scratch with FastAPI, PostgreSQL, and JWT-based role access.

##  Features

-  **Role-Based Auth**: Admins and Editors with JWT-secured access
-  **Editor Uploads**: Upload actual video files (not just links)
-  **Admin Review Workflow**: Approve or reject submissions
-  **Editor Dashboard**: View status of all uploads
-  **Secure Streaming**: Signed URLs + range requests = seeking, buffering, browser-native controls
-  **YouTube API Integration**: Push videos directly to YouTube channels (authenticated)
-  **Modular Architecture**: Clean separation via services, routers, and models
-  **Swagger/OpenAPI UI**: Built-in testing for all endpoints

## 🧱 Tech Stack

- **FastAPI** – async Python backend framework
- **SQLModel** – ORM built on SQLAlchemy + Pydantic
- **PostgreSQL** – production-grade relational DB
- **JWT (PyJWT)** – secure token-based authentication
- **Google API (YouTube Data API v3)** – for YouTube uploads

## 📌 Notes

-  Built **frontend-agnostic** – can be consumed by any frontend
-  Signed streaming URLs **expire** for added security
-  Everything is testable via **Swagger UI**

## 🎯 Goals

🔥Why This Project Stands Out
-  Prove competence in **real-world FastAPI systems**
-  Showcase full-stack backend logic (auth, DB, streaming, external APIs)
-  Create a portfolio-ready project that's **modular, scalable, and production-aware**
