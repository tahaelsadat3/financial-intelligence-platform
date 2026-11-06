# Enterprise AI-Powered Financial Intelligence Platform

A production-grade, ERP-agnostic financial automation microservice engineered for autonomous invoice processing, deterministic accounting validation, and human-in-the-loop audit compliance.

---

## Key Architecture & Core Principles

1. **Deterministic Financial Engine (Zero AI Math Hallucinations):** 
   All math validation, double-entry balanced line generation ($Total\ Debits = Total\ Credits$), and ZATCA 15% VAT compliance are enforced strictly via Python `Decimal` logic.
2. **Human-Controlled Posting Guardrail (State-Machine Enforced):**
   AI generates financial entries in `Pending Review` state only. The `PostingEngine` enforces Role-Based Access Control (RBAC) and permanently blocks auto-posting to ERPs without verified human authorization (`UnauthorizedPostingError`).
3. **ERP-Agnostic Connectivity (Odoo Bridge Implemented):**
   Standardized `BaseERPConnector` architecture allowing instant integration with Odoo, SAP, Oracle NetSuite, and Microsoft Dynamics.
4. **Multi-Tenant Schema Support:**
   Isolated database architecture built for high-throughput enterprise SaaS deployments.

---

## Directory Structure

```text
financial-intelligence-platform/
├── src/
│   ├── api/                 # FastAPI REST Endpoints & Schemas
│   ├── ai_layer/            # Gemini & LLM Provider Adapters
│   ├── connectors/          # Odoo & ERP Integration Bridges
│   ├── core/                # PostingEngine, RBAC & Audit Trails
│   ├── database/            # Multi-tenant DB Schemas & ORM Models
│   ├── financial_engine/    # Deterministic Validators & VAT Engine
│   └── modules/             # Business Logic (Accounts Payable / Invoice Processor)
├── tests/                   # Automated Pytest Suite (15 Test Cases)
├── main.py                  # End-to-End Orchestrator Demo
├── Dockerfile               # Container Environment Specification
├── docker-compose.yml       # Production Multi-Service Infrastructure
└── requirements.txt         # Project Dependencies
