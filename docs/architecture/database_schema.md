# Multi-Tenant Database Architecture & Entity Schema

This document defines the core relational database schema for PostgreSQL, supporting strict multi-tenancy, hierarchical accounting, and automated workflow states.

## 1. Multi-Tenant Organization Hierarchy

All tables enforce tenant boundary using mandatory foreign keys:

`Tenant` (1) ───< `Company` (N) ───< `Branch` (N)

- **`tenants`**: Top-level platform subscriber.
- **`companies`**: Independent legal entity with distinct tax numbers (ZATCA VAT) and COA.
- **`branches`**: Operating branches associated with a company.

## 2. Core Accounting Entities

### 2.1 Chart of Accounts (`chart_of_accounts`)
| Column Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY | Unique account identifier |
| `tenant_id` | UUID | FK -> tenants.id | Tenant context |
| `company_id` | UUID | FK -> companies.id | Company context |
| `account_code` | VARCHAR(50) | NOT NULL | Standard GL Code (e.g., 101001) |
| `account_name_ar` | VARCHAR(255)| NOT NULL | Arabic Account Name |
| `account_name_en` | VARCHAR(255)| NOT NULL | English Account Name |
| `account_type` | VARCHAR(50) | CHECK | Asset, Liability, Equity, Revenue, Expense |
| `parent_id` | UUID | FK -> self.id | Parent account for tree hierarchy |
| `is_reconcilable` | BOOLEAN | DEFAULT FALSE | Enables AP/AR auto-matching |

### 2.2 Journal Entry Drafts & Ledger (`journal_entries` & `journal_entry_lines`)
Stores both AI-generated drafts and final posted accounting entries.

- **`journal_entries`**: Header table holding entry number, date, period, approval state, and original document reference.
- **`journal_entry_lines`**: Line item table enforcing double-entry validation ($Debit = Credit$).

## 3. Workflow State Model

Transactions move sequentially through the enforced state machine:

`Received` ──> `Extracted` ──> `Validated` ──> `Matched` ──> `Draft Prepared` ──> `Pending Review` ──> `Approved` ──> `Posted`

> **NON-NEGOTIABLE RULE:** No automated process or AI agent can update state to `Posted`. The transition to `Posted` requires authenticated human action and valid authorization credentials.

## 4. Document Lineage & Audit Trail (`audit_logs`)
Every financial transaction preserves immutable relationships to:
1. Source PDF/Image File Hash.
2. AI Extracted Data & Confidence Score.
3. Deterministic Validation Audit Output.
4. User Approval Signature & Timestamp.
5. ERP Post Confirmation Reference ID.
