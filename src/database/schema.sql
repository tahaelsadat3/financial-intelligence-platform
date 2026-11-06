-- PostgreSQL Multi-Tenant Database Initial Schema
-- Financial Intelligence Platform

-- Enable UUID extension for secure unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. TENANTS TABLE (المستأجرين / العملاء المشتركين)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. COMPANIES TABLE (الشركات والكيانات القانونية)
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    legal_name_ar VARCHAR(255) NOT NULL,
    legal_name_en VARCHAR(255) NOT NULL,
    vat_number VARCHAR(50) UNIQUE, -- الرقم الضريبي للهيئة (ZATCA)
    currency_code VARCHAR(3) DEFAULT 'SAR',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. CHART OF ACCOUNTS TABLE (شجرة الحسابات)
CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    account_code VARCHAR(50) NOT NULL,
    account_name_ar VARCHAR(255) NOT NULL,
    account_name_en VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- Asset, Liability, Equity, Revenue, Expense
    parent_id UUID REFERENCES chart_of_accounts(id),
    is_reconcilable BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_company_account_code UNIQUE (company_id, account_code)
);

-- 4. JOURNAL ENTRIES TABLE (رأس قيد اليومية / المسودة)
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    entry_number VARCHAR(100),
    entry_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft Prepared', -- Received, Extracted, Validated, Matched, Draft Prepared, Pending Review, Approved, Posted
    source_document_ref VARCHAR(255),
    description TEXT,
    created_by_ai BOOLEAN DEFAULT TRUE,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    posted_to_erp BOOLEAN DEFAULT FALSE,
    erp_reference_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. JOURNAL ENTRY LINES TABLE (بنود قيد اليومية - المدين والدائن)
CREATE TABLE journal_entry_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES chart_of_accounts(id),
    debit_amount NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    credit_amount NUMERIC(15, 4) NOT NULL DEFAULT 0.0000,
    memo TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. AUDIT LOGS TABLE (سجل التدقيق للحركات والقرارات)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    entity_type VARCHAR(50) NOT NULL, -- e.g., 'journal_entry', 'invoice'
    entity_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL, -- e.g., 'AI_EXTRACTED', 'VALIDATED', 'HUMAN_APPROVED', 'ERP_POSTED'
    performed_by VARCHAR(255) NOT NULL, -- User ID or AI Agent Name
    payload JSONB, -- Details of the event / raw response
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
