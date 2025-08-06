-- Vocelio Complete Database Schema for Supabase
-- Comprehensive schema for all microservices
-- Run this in your Supabase SQL editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create custom types/enums
CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'manager', 'user', 'viewer');
CREATE TYPE agent_status AS ENUM ('active', 'inactive', 'training', 'optimizing', 'maintenance');
CREATE TYPE campaign_status AS ENUM ('draft', 'active', 'paused', 'completed', 'archived');
CREATE TYPE call_status AS ENUM ('initiated', 'ringing', 'in_progress', 'completed', 'failed', 'no_answer', 'busy');
CREATE TYPE voice_provider AS ENUM ('elevenlabs', 'ramble_ai', 'piper_tts', 'custom');
CREATE TYPE voice_quality AS ENUM ('standard', 'pro', 'ultra');
CREATE TYPE industry_type AS ENUM ('solar_energy', 'real_estate', 'insurance', 'healthcare', 'finance', 'education', 'retail', 'technology', 'automotive', 'other');
CREATE TYPE compliance_type AS ENUM ('gdpr', 'ccpa', 'tcpa', 'dnc', 'hipaa');

-- Organizations table
CREATE TABLE organizations (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name text NOT NULL,
    industry industry_type DEFAULT 'other',
    size text DEFAULT 'small',
    website text,
    phone text,
    address jsonb DEFAULT '{}',
    billing_email text,
    subscription_tier text DEFAULT 'free',
    settings jsonb DEFAULT '{}',
    compliance_requirements text[] DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Users table (extends auth.users)
CREATE TABLE users (
    id uuid REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email text UNIQUE NOT NULL,
    first_name text,
    last_name text,
    phone text,
    role user_role DEFAULT 'user',
    organization_id uuid REFERENCES organizations(id) ON DELETE SET NULL,
    is_active boolean DEFAULT true,
    profile_image text,
    last_login timestamptz,
    preferences jsonb DEFAULT '{}',
    subscription_tier text DEFAULT 'free',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Agents table
CREATE TABLE agents (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name text NOT NULL,
    description text,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    industry industry_type DEFAULT 'other',
    voice_id text,
    voice_provider voice_provider DEFAULT 'piper_tts',
    language text DEFAULT 'en',
    accent text DEFAULT 'american',
    personality_traits text[] DEFAULT '{}',
    status agent_status DEFAULT 'inactive',
    performance_score decimal(5,2) DEFAULT 0.0,
    total_calls integer DEFAULT 0,
    success_rate decimal(5,2) DEFAULT 0.0,
    avg_call_duration decimal(8,2) DEFAULT 0.0,
    revenue_generated decimal(12,2) DEFAULT 0.0,
    script_template text,
    objection_handlers jsonb DEFAULT '[]',
    optimization_settings jsonb DEFAULT '{}',
    is_template boolean DEFAULT false,
    template_category text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Agent templates table
CREATE TABLE agent_templates (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name text NOT NULL,
    description text,
    industry industry_type DEFAULT 'other',
    use_case text,
    template_data jsonb DEFAULT '{}',
    expected_performance jsonb DEFAULT '{}',
    is_premium boolean DEFAULT false,
    price decimal(8,2) DEFAULT 0.0,
    downloads integer DEFAULT 0,
    rating decimal(3,2) DEFAULT 0.0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Campaigns table
CREATE TABLE campaigns (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name text NOT NULL,
    description text,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    agent_id uuid REFERENCES agents(id) ON DELETE SET NULL,
    status campaign_status DEFAULT 'draft',
    industry industry_type DEFAULT 'other',
    target_audience jsonb DEFAULT '{}',
    schedule jsonb DEFAULT '{}',
    prospect_list jsonb DEFAULT '[]',
    script text,
    goals jsonb DEFAULT '{}',
    performance_metrics jsonb DEFAULT '{}',
    ai_optimization jsonb DEFAULT '{}',
    a_b_testing jsonb DEFAULT '{}',
    compliance_settings jsonb DEFAULT '{}',
    budget_settings jsonb DEFAULT '{}',
    tags text[] DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Prospects table
CREATE TABLE prospects (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    campaign_id uuid REFERENCES campaigns(id) ON DELETE CASCADE,
    name text,
    phone text NOT NULL,
    email text,
    address jsonb DEFAULT '{}',
    additional_data jsonb DEFAULT '{}',
    status text DEFAULT 'pending',
    call_attempts integer DEFAULT 0,
    last_called timestamptz,
    conversion_value decimal(10,2),
    notes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Calls table
CREATE TABLE calls (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    campaign_id uuid REFERENCES campaigns(id) ON DELETE SET NULL,
    agent_id uuid REFERENCES agents(id) ON DELETE SET NULL,
    prospect_id uuid REFERENCES prospects(id) ON DELETE SET NULL,
    phone_number text NOT NULL,
    caller_id text,
    status call_status DEFAULT 'initiated',
    twilio_call_sid text UNIQUE,
    duration decimal(8,2) DEFAULT 0.0,
    cost decimal(8,4) DEFAULT 0.0,
    recording_url text,
    transcript text,
    sentiment_analysis jsonb DEFAULT '{}',
    conversion_result boolean,
    conversion_value decimal(10,2),
    hang_up_reason text,
    ai_insights jsonb DEFAULT '{}',
    quality_score decimal(3,2),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Conversations table
CREATE TABLE conversations (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    call_id uuid REFERENCES calls(id) ON DELETE CASCADE,
    messages jsonb DEFAULT '[]',
    flow_path text[] DEFAULT '{}',
    objections_handled text[] DEFAULT '{}',
    key_moments jsonb DEFAULT '[]',
    decision_points jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Voices table
CREATE TABLE voices (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    voice_id text UNIQUE NOT NULL,
    name text NOT NULL,
    provider voice_provider DEFAULT 'piper_tts',
    quality voice_quality DEFAULT 'standard',
    gender text DEFAULT 'female',
    age text DEFAULT 'young',
    accent text DEFAULT 'american',
    language text DEFAULT 'en',
    description text,
    use_case text,
    category text DEFAULT 'premade',
    performance_metrics jsonb DEFAULT '{}',
    settings jsonb DEFAULT '{}',
    preview_url text,
    cost_per_character decimal(8,6) DEFAULT 0.0,
    available_tiers text[] DEFAULT '{}',
    is_active boolean DEFAULT true,
    usage_count integer DEFAULT 0,
    rating decimal(3,2) DEFAULT 0.0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Voice clones table
CREATE TABLE voice_clones (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    name text NOT NULL,
    description text,
    source_audio_url text NOT NULL,
    cloned_voice_id text,
    provider voice_provider DEFAULT 'elevenlabs',
    quality_score decimal(3,2) DEFAULT 0.0,
    training_status text DEFAULT 'pending',
    training_progress decimal(5,2) DEFAULT 0.0,
    cost decimal(8,2) DEFAULT 0.0,
    usage_restrictions jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Phone numbers table
CREATE TABLE phone_numbers (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    phone_number text UNIQUE NOT NULL,
    friendly_name text,
    provider text DEFAULT 'twilio',
    provider_sid text,
    country_code text,
    region text,
    capabilities text[] DEFAULT '{}',
    status text DEFAULT 'active',
    monthly_cost decimal(8,2) DEFAULT 0.0,
    usage_cost decimal(8,2) DEFAULT 0.0,
    campaign_assignments text[] DEFAULT '{}',
    verification_status text DEFAULT 'pending',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Flows table
CREATE TABLE flows (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    name text NOT NULL,
    description text,
    industry industry_type DEFAULT 'other',
    nodes jsonb DEFAULT '[]',
    edges jsonb DEFAULT '[]',
    version integer DEFAULT 1,
    is_production boolean DEFAULT false,
    performance_metrics jsonb DEFAULT '{}',
    optimization_suggestions text[] DEFAULT '{}',
    tags text[] DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Flow templates table
CREATE TABLE flow_templates (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name text NOT NULL,
    description text,
    industry industry_type DEFAULT 'other',
    category text,
    template_data jsonb DEFAULT '{}',
    expected_performance jsonb DEFAULT '{}',
    is_premium boolean DEFAULT false,
    price decimal(8,2) DEFAULT 0.0,
    downloads integer DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Analytics metrics table
CREATE TABLE analytics_metrics (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    metric_type text NOT NULL,
    metric_value decimal(12,4) NOT NULL,
    dimensions jsonb DEFAULT '{}',
    timestamp timestamptz DEFAULT now(),
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

-- Dashboard widgets table
CREATE TABLE dashboard_widgets (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    widget_type text NOT NULL,
    title text NOT NULL,
    configuration jsonb DEFAULT '{}',
    position jsonb DEFAULT '{}',
    is_visible boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Billing accounts table
CREATE TABLE billing_accounts (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    stripe_customer_id text,
    payment_method_id text,
    billing_email text,
    billing_address jsonb DEFAULT '{}',
    current_plan text DEFAULT 'free',
    billing_cycle text DEFAULT 'monthly',
    auto_pay boolean DEFAULT true,
    credit_balance decimal(10,2) DEFAULT 0.0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Usage logs table
CREATE TABLE usage_logs (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    usage_type text NOT NULL,
    quantity decimal(10,4) DEFAULT 0.0,
    unit_cost decimal(8,4) DEFAULT 0.0,
    total_cost decimal(10,4) DEFAULT 0.0,
    resource_id text,
    billing_period text,
    metadata jsonb DEFAULT '{}',
    timestamp timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now()
);

-- Invoices table
CREATE TABLE invoices (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    invoice_number text UNIQUE NOT NULL,
    billing_period_start timestamptz NOT NULL,
    billing_period_end timestamptz NOT NULL,
    subtotal decimal(10,2) DEFAULT 0.0,
    tax_amount decimal(10,2) DEFAULT 0.0,
    total_amount decimal(10,2) DEFAULT 0.0,
    status text DEFAULT 'draft',
    due_date timestamptz,
    paid_date timestamptz,
    line_items jsonb DEFAULT '[]',
    stripe_invoice_id text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Team members table
CREATE TABLE team_members (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    role user_role DEFAULT 'user',
    permissions text[] DEFAULT '{}',
    invited_by uuid REFERENCES users(id),
    invitation_status text DEFAULT 'pending',
    last_active timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(user_id, organization_id)
);

-- Permissions table
CREATE TABLE permissions (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name text UNIQUE NOT NULL,
    description text,
    resource text NOT NULL,
    action text NOT NULL,
    scope text DEFAULT 'organization',
    created_at timestamptz DEFAULT now()
);

-- Compliance rules table
CREATE TABLE compliance_rules (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    rule_type compliance_type NOT NULL,
    name text NOT NULL,
    description text,
    configuration jsonb DEFAULT '{}',
    is_active boolean DEFAULT true,
    enforcement_level text DEFAULT 'strict',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Do not call entries table
CREATE TABLE dnc_entries (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    phone_number text NOT NULL,
    reason text,
    source text DEFAULT 'manual',
    expiry_date timestamptz,
    notes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(organization_id, phone_number)
);

-- Consent records table
CREATE TABLE consent_records (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    prospect_phone text NOT NULL,
    consent_type text NOT NULL,
    consent_given boolean DEFAULT false,
    consent_date timestamptz DEFAULT now(),
    consent_method text,
    recording_url text,
    expiry_date timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Integrations table
CREATE TABLE integrations (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    provider text NOT NULL,
    name text NOT NULL,
    configuration jsonb DEFAULT '{}',
    credentials jsonb DEFAULT '{}',
    status text DEFAULT 'inactive',
    last_sync timestamptz,
    sync_frequency text DEFAULT 'daily',
    field_mappings jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Webhooks table
CREATE TABLE webhooks (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    name text NOT NULL,
    url text NOT NULL,
    events text[] DEFAULT '{}',
    secret text NOT NULL,
    is_active boolean DEFAULT true,
    retry_count integer DEFAULT 3,
    timeout integer DEFAULT 30,
    last_triggered timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- White label configurations table
CREATE TABLE white_label_configs (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
    brand_name text,
    logo_url text,
    primary_color text DEFAULT '#3B82F6',
    secondary_color text DEFAULT '#1F2937',
    custom_domain text,
    email_templates jsonb DEFAULT '{}',
    custom_css text,
    support_email text,
    terms_url text,
    privacy_url text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- API keys table
CREATE TABLE api_keys (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    organization_id uuid REFERENCES organizations(id) ON DELETE CASCADE,
    name text NOT NULL,
    key_hash text UNIQUE NOT NULL,
    permissions text[] DEFAULT '{}',
    rate_limit integer DEFAULT 1000,
    is_active boolean DEFAULT true,
    last_used timestamptz,
    expires_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- API usage table
CREATE TABLE api_usage (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    api_key_id uuid REFERENCES api_keys(id) ON DELETE CASCADE,
    endpoint text NOT NULL,
    method text NOT NULL,
    status_code integer DEFAULT 200,
    response_time decimal(8,4) DEFAULT 0.0,
    ip_address text,
    user_agent text,
    timestamp timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_agents_user_id ON agents(user_id);
CREATE INDEX idx_agents_organization_id ON agents(organization_id);
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_organization_id ON campaigns(organization_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_calls_campaign_id ON calls(campaign_id);
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_created_at ON calls(created_at);
CREATE INDEX idx_prospects_campaign_id ON prospects(campaign_id);
CREATE INDEX idx_prospects_phone ON prospects(phone);
CREATE INDEX idx_usage_logs_organization_id ON usage_logs(organization_id);
CREATE INDEX idx_usage_logs_billing_period ON usage_logs(billing_period);
CREATE INDEX idx_analytics_metrics_user_id ON analytics_metrics(user_id);
CREATE INDEX idx_analytics_metrics_timestamp ON analytics_metrics(timestamp);
CREATE INDEX idx_dnc_phone ON dnc_entries(phone_number);
CREATE INDEX idx_api_usage_timestamp ON api_usage(timestamp);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_calls_updated_at BEFORE UPDATE ON calls FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_flows_updated_at BEFORE UPDATE ON flows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE prospects ENABLE ROW LEVEL SECURITY;
ALTER TABLE flows ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_metrics ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own organization's data
CREATE POLICY "Users can view own organization data" ON organizations FOR SELECT USING (
    id IN (SELECT organization_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Users can view own data" ON users FOR SELECT USING (
    id = auth.uid() OR organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Users can manage own agents" ON agents FOR ALL USING (
    user_id = auth.uid() OR organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Users can manage own campaigns" ON campaigns FOR ALL USING (
    user_id = auth.uid() OR organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid())
);

-- Insert default permissions
INSERT INTO permissions (name, description, resource, action, scope) VALUES
('agents.read', 'View agents', 'agents', 'read', 'organization'),
('agents.write', 'Create and edit agents', 'agents', 'write', 'organization'),
('agents.delete', 'Delete agents', 'agents', 'delete', 'organization'),
('campaigns.read', 'View campaigns', 'campaigns', 'read', 'organization'),
('campaigns.write', 'Create and edit campaigns', 'campaigns', 'write', 'organization'),
('campaigns.delete', 'Delete campaigns', 'campaigns', 'delete', 'organization'),
('calls.read', 'View call logs', 'calls', 'read', 'organization'),
('billing.read', 'View billing information', 'billing', 'read', 'organization'),
('billing.admin', 'Manage billing', 'billing', 'admin', 'organization'),
('team.read', 'View team members', 'team', 'read', 'organization'),
('team.admin', 'Manage team members', 'team', 'admin', 'organization'),
('analytics.read', 'View analytics', 'analytics', 'read', 'organization'),
('settings.admin', 'Manage organization settings', 'settings', 'admin', 'organization');

-- Insert sample voice data
INSERT INTO voices (voice_id, name, provider, quality, gender, age, accent, language, description, use_case, cost_per_character, available_tiers) VALUES
('rachel_professional', 'Rachel - Professional', 'piper_tts', 'standard', 'female', 'young', 'american', 'en', 'Calm, professional female voice perfect for business calls', 'business', 0.000133, ARRAY['free', 'starter', 'pro', 'enterprise']),
('bella_sales', 'Bella - Warm Sales', 'ramble_ai', 'pro', 'female', 'young', 'american', 'en', 'Friendly, warm female voice excellent for sales calls', 'sales', 0.0003, ARRAY['starter', 'pro', 'enterprise']),
('adam_executive', 'Adam - Executive', 'elevenlabs', 'ultra', 'male', 'middle_aged', 'american', 'en', 'Professional male voice for executive communications', 'executive', 0.000583, ARRAY['pro', 'enterprise']),
('sofia_spanish', 'Sofia - Spanish Native', 'ramble_ai', 'pro', 'female', 'young', 'spanish', 'es', 'Native Spanish speaker for Spanish campaigns', 'multilingual', 0.0003, ARRAY['pro', 'enterprise']);

-- Insert sample agent templates
INSERT INTO agent_templates (name, description, industry, use_case, template_data, expected_performance, is_premium) VALUES
('Solar Lead Generator', 'High-converting solar appointment setter', 'solar_energy', 'lead_generation', 
 '{"personality": ["confident", "technical", "persuasive"], "objection_handlers": ["cost", "timing", "spouse"]}',
 '{"conversion_rate": 34.2, "avg_call_duration": 4.5}', false),
('Real Estate Qualifier', 'Pre-qualifies real estate leads', 'real_estate', 'qualification',
 '{"personality": ["professional", "empathetic", "detailed"], "objection_handlers": ["market_conditions", "timing", "financing"]}',
 '{"conversion_rate": 29.8, "avg_call_duration": 6.2}', false),
('Insurance Consultant', 'Insurance needs assessment agent', 'insurance', 'consultation',
 '{"personality": ["caring", "detailed", "trustworthy"], "objection_handlers": ["current_coverage", "cost", "complexity"]}',
 '{"conversion_rate": 28.9, "avg_call_duration": 7.1}', true);

COMMENT ON TABLE organizations IS 'Customer organizations using the Vocelio platform';
COMMENT ON TABLE users IS 'Platform users with role-based access';
COMMENT ON TABLE agents IS 'AI voice agents for making calls';
COMMENT ON TABLE campaigns IS 'Calling campaigns with target audiences';
COMMENT ON TABLE calls IS 'Individual call records and outcomes';
COMMENT ON TABLE voices IS 'Available voice options from different providers';
COMMENT ON TABLE flows IS 'Conversation flow designs';
COMMENT ON TABLE usage_logs IS 'Usage tracking for billing';
COMMENT ON TABLE analytics_metrics IS 'Performance metrics and analytics';
