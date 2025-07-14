## Video Approval System – FastAPI Backend

A secure backend system where editors can upload videos and admins can approve or reject them. Built with FastAPI, SQLModel, PostgreSQL, and JWT-based authentication.

##  Features

-  JWT Authentication with role-based access (Admin / Editor)
-  Video URL upload
-  Admin review & status updates (Pending / Approved / Rejected)
-  Editors can view their submissions
-  Clean service-layer architecture
-  Swagger/OpenAPI UI for testing

## 🧱 Tech Stack

- **FastAPI** – modern Python web framework
- **SQLModel** – combines pydantic + SQLAlchemy with great developer ergonomics
- **PostgreSQL** – reliable relational database
- **JWT** – secure token-based authentication

## 📌 Notes

-  All endpoints tested via Swagger UI
-  Currently no frontend — designed to be frontend-agnostic
-  Video streaming is not implemented; URLs are assumed to be remote

## 🎯 Goals

This project was built as a backend-focused portfolio project to:
-  Demonstrate real-world FastAPI usage
-  Showcase authentication, authorization, and database design
-  Build a production-like system with role-based access
