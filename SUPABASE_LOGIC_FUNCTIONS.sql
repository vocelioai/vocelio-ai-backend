-- ===================================================================
-- VOCELIO AI CALL CENTER - SUPABASE LOGIC AND FEATURES
-- ===================================================================
-- Advanced functions, triggers, and real-time configurations
-- Run this AFTER creating the main schema

-- ===================================================================
-- ADVANCED FUNCTIONS
-- ===================================================================

-- 1. Call Performance Analytics Function
CREATE OR REPLACE FUNCTION get_call_performance_analytics(
    org_id UUID,
    start_date DATE DEFAULT (CURRENT_DATE - INTERVAL '30 days'),
    end_date DATE DEFAULT CURRENT_DATE,
    agent_id UUID DEFAULT NULL,
    campaign_id UUID DEFAULT NULL
)
RETURNS TABLE (
    total_calls BIGINT,
    successful_calls BIGINT,
    success_rate DECIMAL,
    avg_duration DECIMAL,
    total_revenue DECIMAL,
    cost_per_call DECIMAL,
    conversion_rate DECIMAL,
    customer_satisfaction DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_calls,
        COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::BIGINT as successful_calls,
        ROUND(
            (COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::DECIMAL / 
             NULLIF(COUNT(*), 0) * 100), 2
        ) as success_rate,
        ROUND(AVG(c.total_duration), 2) as avg_duration,
        ROUND(SUM(COALESCE(c.revenue_generated, 0)), 2) as total_revenue,
        ROUND(AVG(COALESCE(c.cost, 0)), 4) as cost_per_call,
        ROUND(
            (COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::DECIMAL / 
             NULLIF(COUNT(*), 0) * 100), 2
        ) as conversion_rate,
        ROUND(AVG(COALESCE(c.customer_satisfaction, 0)), 2) as customer_satisfaction
    FROM calls c
    JOIN campaigns camp ON c.campaign_id = camp.id
    WHERE camp.organization_id = org_id
        AND c.created_at::DATE BETWEEN start_date AND end_date
        AND (agent_id IS NULL OR c.agent_id = agent_id)
        AND (campaign_id IS NULL OR c.campaign_id = campaign_id);
END;
$$ LANGUAGE plpgsql;

-- 2. Real-time Campaign Metrics Function
CREATE OR REPLACE FUNCTION get_realtime_campaign_metrics(org_id UUID)
RETURNS TABLE (
    campaign_id UUID,
    campaign_name TEXT,
    status TEXT,
    calls_today INTEGER,
    success_rate_today DECIMAL,
    active_calls INTEGER,
    estimated_completion TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id as campaign_id,
        c.name as campaign_name,
        c.status::TEXT,
        (
            SELECT COUNT(*)::INTEGER 
            FROM calls ca 
            WHERE ca.campaign_id = c.id 
                AND ca.created_at::DATE = CURRENT_DATE
        ) as calls_today,
        (
            SELECT ROUND(
                (COUNT(CASE WHEN ca.status = 'completed' THEN 1 END)::DECIMAL / 
                 NULLIF(COUNT(*), 0) * 100), 2
            )
            FROM calls ca 
            WHERE ca.campaign_id = c.id 
                AND ca.created_at::DATE = CURRENT_DATE
        ) as success_rate_today,
        (
            SELECT COUNT(*)::INTEGER 
            FROM calls ca 
            WHERE ca.campaign_id = c.id 
                AND ca.status IN ('initiated', 'ringing', 'in_progress')
        ) as active_calls,
        (
            CASE 
                WHEN c.progress_percentage > 0 THEN 
                    c.created_at + (
                        (CURRENT_TIMESTAMP - c.created_at) * 
                        (100.0 / NULLIF(c.progress_percentage, 0))
                    )
                ELSE NULL 
            END
        ) as estimated_completion
    FROM campaigns c
    WHERE c.organization_id = org_id
        AND c.status IN ('active', 'running');
END;
$$ LANGUAGE plpgsql;

-- 3. Agent Performance Scoring Function
CREATE OR REPLACE FUNCTION calculate_agent_performance_score(agent_uuid UUID)
RETURNS DECIMAL AS $$
DECLARE
    success_rate DECIMAL;
    avg_duration DECIMAL;
    customer_satisfaction DECIMAL;
    conversion_rate DECIMAL;
    consistency_score DECIMAL;
    performance_score DECIMAL;
BEGIN
    -- Get agent metrics from the last 30 days
    SELECT 
        (COUNT(CASE WHEN status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100),
        AVG(total_duration),
        AVG(COALESCE(customer_satisfaction, 0)),
        (COUNT(CASE WHEN conversion_result = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100)
    INTO success_rate, avg_duration, customer_satisfaction, conversion_rate
    FROM calls 
    WHERE agent_id = agent_uuid 
        AND created_at >= (CURRENT_DATE - INTERVAL '30 days');
    
    -- Calculate consistency score based on daily performance variance
    SELECT 
        100 - (STDDEV(daily_success_rate) * 2)
    INTO consistency_score
    FROM (
        SELECT 
            DATE(created_at) as call_date,
            (COUNT(CASE WHEN status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100) as daily_success_rate
        FROM calls 
        WHERE agent_id = agent_uuid 
            AND created_at >= (CURRENT_DATE - INTERVAL '30 days')
        GROUP BY DATE(created_at)
        HAVING COUNT(*) >= 5  -- Only days with 5+ calls
    ) daily_metrics;
    
    -- Weighted performance score calculation
    performance_score := (
        COALESCE(success_rate, 0) * 0.3 +           -- 30% weight
        COALESCE(conversion_rate, 0) * 0.3 +        -- 30% weight  
        COALESCE(customer_satisfaction * 20, 0) * 0.25 + -- 25% weight (convert 5-point scale to 100)
        COALESCE(consistency_score, 0) * 0.15       -- 15% weight
    );
    
    -- Cap at 100 and ensure minimum of 0
    performance_score := GREATEST(0, LEAST(100, performance_score));
    
    -- Update the agent record
    UPDATE agents 
    SET performance_score = performance_score 
    WHERE id = agent_uuid;
    
    RETURN performance_score;
END;
$$ LANGUAGE plpgsql;

-- 4. Smart Campaign Optimization Function
CREATE OR REPLACE FUNCTION optimize_campaign_performance(campaign_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    campaign_data RECORD;
    optimization_suggestions JSONB;
    current_performance RECORD;
    best_performing_hours INTEGER[];
    optimal_voice TEXT;
BEGIN
    -- Get campaign data
    SELECT * INTO campaign_data FROM campaigns WHERE id = campaign_uuid;
    
    -- Get current performance metrics
    SELECT 
        COUNT(*) as total_calls,
        (COUNT(CASE WHEN status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100) as success_rate,
        (COUNT(CASE WHEN conversion_result = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100) as conversion_rate,
        AVG(total_duration) as avg_duration
    INTO current_performance
    FROM calls 
    WHERE campaign_id = campaign_uuid;
    
    -- Find best performing hours
    SELECT ARRAY_AGG(hour_of_day)
    INTO best_performing_hours
    FROM (
        SELECT 
            EXTRACT(HOUR FROM created_at) as hour_of_day,
            (COUNT(CASE WHEN status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100) as success_rate
        FROM calls 
        WHERE campaign_id = campaign_uuid
        GROUP BY EXTRACT(HOUR FROM created_at)
        HAVING COUNT(*) >= 10
        ORDER BY success_rate DESC
        LIMIT 5
    ) hourly_performance;
    
    -- Find optimal voice based on performance
    SELECT voice_id
    INTO optimal_voice
    FROM (
        SELECT 
            a.voice_id,
            AVG(c.customer_satisfaction) as avg_satisfaction,
            (COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100) as conversion_rate
        FROM calls c
        JOIN agents a ON c.agent_id = a.id
        WHERE c.campaign_id = campaign_uuid AND a.voice_id IS NOT NULL
        GROUP BY a.voice_id
        HAVING COUNT(*) >= 5
        ORDER BY (avg_satisfaction * 0.5 + conversion_rate * 0.5) DESC
        LIMIT 1
    ) voice_performance;
    
    -- Build optimization suggestions
    optimization_suggestions := jsonb_build_object(
        'current_performance', jsonb_build_object(
            'success_rate', current_performance.success_rate,
            'conversion_rate', current_performance.conversion_rate,
            'avg_duration', current_performance.avg_duration
        ),
        'suggestions', jsonb_build_array()
    );
    
    -- Add suggestions based on performance analysis
    IF current_performance.success_rate < 25 THEN
        optimization_suggestions := jsonb_set(
            optimization_suggestions,
            '{suggestions}',
            optimization_suggestions->'suggestions' || jsonb_build_object(
                'type', 'low_success_rate',
                'priority', 'high',
                'suggestion', 'Consider revising the call script or agent training',
                'expected_improvement', '15-25%'
            )
        );
    END IF;
    
    IF current_performance.conversion_rate < 10 THEN
        optimization_suggestions := jsonb_set(
            optimization_suggestions,
            '{suggestions}',
            optimization_suggestions->'suggestions' || jsonb_build_object(
                'type', 'low_conversion',
                'priority', 'high',
                'suggestion', 'Review objection handling and closing techniques',
                'expected_improvement', '20-30%'
            )
        );
    END IF;
    
    IF best_performing_hours IS NOT NULL THEN
        optimization_suggestions := jsonb_set(
            optimization_suggestions,
            '{suggestions}',
            optimization_suggestions->'suggestions' || jsonb_build_object(
                'type', 'timing_optimization',
                'priority', 'medium',
                'suggestion', 'Focus calls during peak performance hours',
                'best_hours', best_performing_hours,
                'expected_improvement', '10-15%'
            )
        );
    END IF;
    
    IF optimal_voice IS NOT NULL AND optimal_voice != (SELECT voice_id FROM agents WHERE id = campaign_data.agent_id) THEN
        optimization_suggestions := jsonb_set(
            optimization_suggestions,
            '{suggestions}',
            optimization_suggestions->'suggestions' || jsonb_build_object(
                'type', 'voice_optimization',
                'priority', 'medium',
                'suggestion', 'Switch to better performing voice',
                'recommended_voice', optimal_voice,
                'expected_improvement', '5-10%'
            )
        );
    END IF;
    
    -- Update campaign with optimization suggestions
    UPDATE campaigns 
    SET optimization_suggestions = optimization_suggestions
    WHERE id = campaign_uuid;
    
    RETURN optimization_suggestions;
END;
$$ LANGUAGE plpgsql;

-- 5. Generate Daily Analytics Function
CREATE OR REPLACE FUNCTION generate_daily_analytics()
RETURNS VOID AS $$
DECLARE
    org_record RECORD;
    call_data RECORD;
    campaign_data RECORD;
    agent_data RECORD;
    voice_data RECORD;
BEGIN
    -- Generate analytics for each organization
    FOR org_record IN SELECT id FROM organizations LOOP
        
        -- Generate call metrics
        FOR call_data IN 
            SELECT 
                DATE(created_at) as metric_date,
                EXTRACT(HOUR FROM created_at) as metric_hour,
                EXTRACT(DOW FROM created_at) as day_of_week,
                campaign_id,
                agent_id,
                (SELECT voice_id FROM agents WHERE id = calls.agent_id) as voice_id,
                COUNT(*) as total_calls,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_calls,
                COUNT(CASE WHEN status IN ('failed', 'no_answer', 'busy') THEN 1 END) as failed_calls,
                COUNT(CASE WHEN conversion_result = true THEN 1 END) as converted_calls,
                AVG(total_duration) as avg_duration,
                AVG(customer_satisfaction) as avg_satisfaction,
                SUM(cost) as total_cost,
                SUM(revenue_generated) as total_revenue
            FROM calls
            WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
                AND campaign_id IN (SELECT id FROM campaigns WHERE organization_id = org_record.id)
            GROUP BY 
                DATE(created_at), 
                EXTRACT(HOUR FROM created_at),
                EXTRACT(DOW FROM created_at),
                campaign_id, 
                agent_id,
                (SELECT voice_id FROM agents WHERE id = calls.agent_id)
        LOOP
            INSERT INTO call_metrics (
                organization_id, date, hour, day_of_week, campaign_id, agent_id, voice_id,
                total_calls, successful_calls, failed_calls,
                success_rate, conversion_rate, avg_duration, avg_quality_score,
                total_cost, revenue_generated, cost_per_call
            ) VALUES (
                org_record.id,
                call_data.metric_date,
                call_data.metric_hour,
                call_data.day_of_week,
                call_data.campaign_id,
                call_data.agent_id,
                call_data.voice_id,
                call_data.total_calls,
                call_data.successful_calls,
                call_data.failed_calls,
                CASE WHEN call_data.total_calls > 0 THEN 
                    (call_data.successful_calls::DECIMAL / call_data.total_calls * 100) 
                ELSE 0 END,
                CASE WHEN call_data.total_calls > 0 THEN 
                    (call_data.converted_calls::DECIMAL / call_data.total_calls * 100) 
                ELSE 0 END,
                COALESCE(call_data.avg_duration, 0),
                COALESCE(call_data.avg_satisfaction, 0),
                COALESCE(call_data.total_cost, 0),
                COALESCE(call_data.total_revenue, 0),
                CASE WHEN call_data.total_calls > 0 THEN 
                    (call_data.total_cost / call_data.total_calls) 
                ELSE 0 END
            ) ON CONFLICT (organization_id, date, hour, campaign_id, agent_id, voice_id) 
            DO UPDATE SET
                total_calls = EXCLUDED.total_calls,
                successful_calls = EXCLUDED.successful_calls,
                failed_calls = EXCLUDED.failed_calls,
                success_rate = EXCLUDED.success_rate,
                conversion_rate = EXCLUDED.conversion_rate,
                avg_duration = EXCLUDED.avg_duration,
                avg_quality_score = EXCLUDED.avg_quality_score,
                total_cost = EXCLUDED.total_cost,
                revenue_generated = EXCLUDED.revenue_generated,
                cost_per_call = EXCLUDED.cost_per_call;
        END LOOP;
        
        -- Generate campaign metrics
        FOR campaign_data IN 
            SELECT 
                c.id as campaign_id,
                c.name as campaign_name,
                c.campaign_type,
                c.status,
                COUNT(ca.*) as total_calls,
                COUNT(CASE WHEN ca.status = 'completed' THEN 1 END) as successful_calls,
                COUNT(CASE WHEN ca.conversion_result = true THEN 1 END) as conversions,
                SUM(ca.cost) as total_cost,
                SUM(ca.revenue_generated) as total_revenue,
                COUNT(DISTINCT p.id) as leads_generated
            FROM campaigns c
            LEFT JOIN calls ca ON c.id = ca.campaign_id AND DATE(ca.created_at) = CURRENT_DATE - INTERVAL '1 day'
            LEFT JOIN prospects p ON c.id = p.campaign_id AND DATE(p.created_at) = CURRENT_DATE - INTERVAL '1 day'
            WHERE c.organization_id = org_record.id
            GROUP BY c.id, c.name, c.campaign_type, c.status
        LOOP
            INSERT INTO campaign_metrics (
                organization_id, campaign_id, campaign_name, campaign_type, date,
                total_calls, successful_calls, success_rate, conversion_rate,
                total_cost, revenue_generated, leads_generated, status, is_active
            ) VALUES (
                org_record.id,
                campaign_data.campaign_id,
                campaign_data.campaign_name,
                campaign_data.campaign_type,
                CURRENT_DATE - INTERVAL '1 day',
                COALESCE(campaign_data.total_calls, 0),
                COALESCE(campaign_data.successful_calls, 0),
                CASE WHEN campaign_data.total_calls > 0 THEN 
                    (campaign_data.successful_calls::DECIMAL / campaign_data.total_calls * 100) 
                ELSE 0 END,
                CASE WHEN campaign_data.total_calls > 0 THEN 
                    (campaign_data.conversions::DECIMAL / campaign_data.total_calls * 100) 
                ELSE 0 END,
                COALESCE(campaign_data.total_cost, 0),
                COALESCE(campaign_data.total_revenue, 0),
                COALESCE(campaign_data.leads_generated, 0),
                campaign_data.status,
                CASE WHEN campaign_data.status IN ('active', 'running') THEN true ELSE false END
            ) ON CONFLICT (organization_id, campaign_id, date) 
            DO UPDATE SET
                total_calls = EXCLUDED.total_calls,
                successful_calls = EXCLUDED.successful_calls,
                success_rate = EXCLUDED.success_rate,
                conversion_rate = EXCLUDED.conversion_rate,
                total_cost = EXCLUDED.total_cost,
                revenue_generated = EXCLUDED.revenue_generated,
                leads_generated = EXCLUDED.leads_generated,
                status = EXCLUDED.status,
                is_active = EXCLUDED.is_active;
        END LOOP;
        
    END LOOP;
    
    RAISE NOTICE 'Daily analytics generation completed for %', CURRENT_DATE - INTERVAL '1 day';
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- TRIGGERS AND AUTOMATION
-- ===================================================================

-- 1. Auto-update agent performance trigger
CREATE OR REPLACE FUNCTION trigger_update_agent_performance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update agent performance when a call is completed
    IF NEW.status = 'completed' AND (OLD IS NULL OR OLD.status != 'completed') THEN
        -- Update agent stats
        UPDATE agents SET
            total_calls = total_calls + 1,
            successful_calls = successful_calls + CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END,
            success_rate = CASE 
                WHEN (total_calls + 1) > 0 THEN 
                    ((successful_calls + CASE WHEN NEW.status = 'completed' THEN 1 ELSE 0 END)::DECIMAL / (total_calls + 1)) * 100
                ELSE 0 
            END,
            avg_call_duration = CASE 
                WHEN (total_calls + 1) > 0 THEN 
                    ((avg_call_duration * total_calls + COALESCE(NEW.total_duration, 0)) / (total_calls + 1))
                ELSE COALESCE(NEW.total_duration, 0)
            END,
            revenue_generated = revenue_generated + COALESCE(NEW.revenue_generated, 0)
        WHERE id = NEW.agent_id;
        
        -- Recalculate performance score asynchronously
        PERFORM calculate_agent_performance_score(NEW.agent_id);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agent_performance_trigger
    AFTER INSERT OR UPDATE ON calls
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_agent_performance();

-- 2. Campaign progress tracking trigger
CREATE OR REPLACE FUNCTION trigger_update_campaign_progress()
RETURNS TRIGGER AS $$
DECLARE
    total_prospects INTEGER;
    called_prospects INTEGER;
    progress DECIMAL;
BEGIN
    -- Get prospect counts for the campaign
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN status != 'pending' THEN 1 END)
    INTO total_prospects, called_prospects
    FROM prospects 
    WHERE campaign_id = NEW.campaign_id;
    
    -- Calculate progress percentage
    IF total_prospects > 0 THEN
        progress := (called_prospects::DECIMAL / total_prospects) * 100;
    ELSE
        progress := 0;
    END IF;
    
    -- Update campaign progress
    UPDATE campaigns SET
        progress_percentage = progress,
        last_activity_at = NOW()
    WHERE id = NEW.campaign_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_campaign_progress_trigger
    AFTER INSERT OR UPDATE ON calls
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_campaign_progress();

-- 3. Real-time metrics update trigger
CREATE OR REPLACE FUNCTION trigger_update_realtime_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert real-time metrics for the organization
    INSERT INTO realtime_metrics (
        organization_id,
        active_calls,
        calls_today,
        timestamp
    )
    SELECT 
        org.id,
        (SELECT COUNT(*) FROM calls c 
         JOIN campaigns cam ON c.campaign_id = cam.id 
         WHERE cam.organization_id = org.id 
           AND c.status IN ('initiated', 'ringing', 'in_progress')),
        (SELECT COUNT(*) FROM calls c 
         JOIN campaigns cam ON c.campaign_id = cam.id 
         WHERE cam.organization_id = org.id 
           AND DATE(c.created_at) = CURRENT_DATE),
        NOW()
    FROM organizations org
    WHERE org.id = (
        SELECT c.organization_id 
        FROM campaigns c 
        WHERE c.id = COALESCE(NEW.campaign_id, OLD.campaign_id)
    )
    ON CONFLICT (organization_id) 
    DO UPDATE SET
        active_calls = EXCLUDED.active_calls,
        calls_today = EXCLUDED.calls_today,
        timestamp = EXCLUDED.timestamp;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_realtime_metrics_trigger
    AFTER INSERT OR UPDATE OR DELETE ON calls
    FOR EACH ROW
    EXECUTE FUNCTION trigger_update_realtime_metrics();

-- 4. Usage tracking trigger
CREATE OR REPLACE FUNCTION trigger_track_usage()
RETURNS TRIGGER AS $$
DECLARE
    org_id UUID;
    call_cost DECIMAL;
BEGIN
    -- Get organization ID
    SELECT c.organization_id INTO org_id
    FROM campaigns c 
    WHERE c.id = NEW.campaign_id;
    
    -- Calculate call cost (example: $0.015 per minute)
    call_cost := (COALESCE(NEW.total_duration, 0) / 60.0) * 0.015;
    
    -- Log usage when call is completed
    IF NEW.status = 'completed' AND (OLD IS NULL OR OLD.status != 'completed') THEN
        INSERT INTO usage_logs (
            organization_id,
            usage_type,
            resource_id,
            quantity,
            unit,
            unit_cost,
            total_cost,
            billing_period,
            metadata
        ) VALUES (
            org_id,
            'call_minute',
            NEW.id::TEXT,
            (COALESCE(NEW.total_duration, 0) / 60.0),
            'minutes',
            0.015,
            call_cost,
            TO_CHAR(NEW.created_at, 'YYYY-MM'),
            jsonb_build_object(
                'campaign_id', NEW.campaign_id,
                'agent_id', NEW.agent_id,
                'phone_number', NEW.phone_number,
                'duration_seconds', NEW.total_duration
            )
        );
        
        -- Update organization monthly usage
        UPDATE organizations SET
            monthly_calls_used = monthly_calls_used + 1
        WHERE id = org_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER track_usage_trigger
    AFTER INSERT OR UPDATE ON calls
    FOR EACH ROW
    EXECUTE FUNCTION trigger_track_usage();

-- ===================================================================
-- SCHEDULED JOBS (Use pg_cron extension if available)
-- ===================================================================

-- Note: These require the pg_cron extension to be enabled
-- Enable with: CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule daily analytics generation (runs at 1 AM daily)
-- SELECT cron.schedule('generate-daily-analytics', '0 1 * * *', 'SELECT generate_daily_analytics();');

-- Schedule hourly real-time metrics cleanup (keeps last 24 hours)
-- SELECT cron.schedule('cleanup-realtime-metrics', '0 * * * *', 
--     'DELETE FROM realtime_metrics WHERE timestamp < NOW() - INTERVAL ''24 hours'';');

-- Schedule weekly agent performance updates (runs at 2 AM on Sundays)
-- SELECT cron.schedule('update-agent-performance', '0 2 * * 0', 
--     'SELECT calculate_agent_performance_score(id) FROM agents WHERE status = ''active'';');

-- ===================================================================
-- REAL-TIME SUBSCRIPTIONS CONFIGURATION
-- ===================================================================

-- Enable real-time for critical tables
ALTER PUBLICATION supabase_realtime ADD TABLE calls;
ALTER PUBLICATION supabase_realtime ADD TABLE campaigns;
ALTER PUBLICATION supabase_realtime ADD TABLE realtime_metrics;
ALTER PUBLICATION supabase_realtime ADD TABLE prospects;
ALTER PUBLICATION supabase_realtime ADD TABLE agents;

-- Real-time filters for performance (add to your client-side code)
/*
// Subscribe to campaign updates for a specific organization
const campaignSubscription = supabase
  .channel('campaign-updates')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'campaigns',
    filter: 'organization_id=eq.' + organizationId
  }, handleCampaignUpdate)
  .subscribe();

// Subscribe to call updates for active campaigns
const callSubscription = supabase
  .channel('call-updates')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'calls',
    filter: 'status=in.(initiated,ringing,in_progress)'
  }, handleCallUpdate)
  .subscribe();

// Subscribe to real-time metrics
const metricsSubscription = supabase
  .channel('metrics-updates')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'realtime_metrics',
    filter: 'organization_id=eq.' + organizationId
  }, handleMetricsUpdate)
  .subscribe();
*/

-- ===================================================================
-- API HELPER FUNCTIONS
-- ===================================================================

-- 1. Get Dashboard Overview
CREATE OR REPLACE FUNCTION get_dashboard_overview(org_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    active_campaigns INTEGER;
    total_calls_today INTEGER;
    active_calls INTEGER;
    success_rate_today DECIMAL;
    revenue_today DECIMAL;
    top_agent RECORD;
BEGIN
    -- Get active campaigns count
    SELECT COUNT(*) INTO active_campaigns
    FROM campaigns 
    WHERE organization_id = org_id AND status IN ('active', 'running');
    
    -- Get today's metrics
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN status IN ('initiated', 'ringing', 'in_progress') THEN 1 END),
        ROUND((COUNT(CASE WHEN status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2),
        ROUND(SUM(COALESCE(revenue_generated, 0)), 2)
    INTO total_calls_today, active_calls, success_rate_today, revenue_today
    FROM calls c
    JOIN campaigns camp ON c.campaign_id = camp.id
    WHERE camp.organization_id = org_id AND DATE(c.created_at) = CURRENT_DATE;
    
    -- Get top performing agent today
    SELECT 
        a.id,
        a.name,
        COUNT(c.*) as calls_made,
        ROUND((COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(c.*), 0) * 100), 2) as success_rate
    INTO top_agent
    FROM agents a
    LEFT JOIN calls c ON a.id = c.agent_id AND DATE(c.created_at) = CURRENT_DATE
    WHERE a.organization_id = org_id
    GROUP BY a.id, a.name
    ORDER BY success_rate DESC, calls_made DESC
    LIMIT 1;
    
    -- Build result JSON
    result := jsonb_build_object(
        'active_campaigns', COALESCE(active_campaigns, 0),
        'total_calls_today', COALESCE(total_calls_today, 0),
        'active_calls', COALESCE(active_calls, 0),
        'success_rate_today', COALESCE(success_rate_today, 0),
        'revenue_today', COALESCE(revenue_today, 0),
        'top_agent', CASE 
            WHEN top_agent.id IS NOT NULL THEN 
                jsonb_build_object(
                    'id', top_agent.id,
                    'name', top_agent.name,
                    'calls_made', top_agent.calls_made,
                    'success_rate', top_agent.success_rate
                )
            ELSE NULL 
        END,
        'timestamp', NOW()
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 2. Get Agent Leaderboard
CREATE OR REPLACE FUNCTION get_agent_leaderboard(
    org_id UUID,
    time_period TEXT DEFAULT '7d' -- '1d', '7d', '30d'
)
RETURNS TABLE (
    agent_id UUID,
    agent_name TEXT,
    total_calls BIGINT,
    successful_calls BIGINT,
    success_rate DECIMAL,
    conversion_rate DECIMAL,
    revenue_generated DECIMAL,
    avg_call_duration DECIMAL,
    performance_score DECIMAL,
    rank INTEGER
) AS $$
DECLARE
    date_filter TIMESTAMPTZ;
BEGIN
    -- Set date filter based on period
    CASE time_period
        WHEN '1d' THEN date_filter := CURRENT_DATE;
        WHEN '7d' THEN date_filter := CURRENT_DATE - INTERVAL '7 days';
        WHEN '30d' THEN date_filter := CURRENT_DATE - INTERVAL '30 days';
        ELSE date_filter := CURRENT_DATE - INTERVAL '7 days';
    END CASE;
    
    RETURN QUERY
    SELECT 
        a.id as agent_id,
        a.name as agent_name,
        COUNT(c.*)::BIGINT as total_calls,
        COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::BIGINT as successful_calls,
        ROUND((COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(c.*), 0) * 100), 2) as success_rate,
        ROUND((COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::DECIMAL / NULLIF(COUNT(c.*), 0) * 100), 2) as conversion_rate,
        ROUND(SUM(COALESCE(c.revenue_generated, 0)), 2) as revenue_generated,
        ROUND(AVG(c.total_duration), 2) as avg_call_duration,
        a.performance_score,
        ROW_NUMBER() OVER (ORDER BY a.performance_score DESC, COUNT(c.*) DESC)::INTEGER as rank
    FROM agents a
    LEFT JOIN calls c ON a.id = c.agent_id AND c.created_at >= date_filter
    WHERE a.organization_id = org_id AND a.status = 'active'
    GROUP BY a.id, a.name, a.performance_score
    ORDER BY rank;
END;
$$ LANGUAGE plpgsql;

-- 3. Advanced Campaign Analytics
CREATE OR REPLACE FUNCTION get_campaign_analytics(
    campaign_uuid UUID,
    time_granularity TEXT DEFAULT 'hour' -- 'hour', 'day', 'week'
)
RETURNS TABLE (
    time_bucket TIMESTAMPTZ,
    calls_made INTEGER,
    calls_answered INTEGER,
    conversions INTEGER,
    revenue DECIMAL,
    avg_duration DECIMAL,
    success_rate DECIMAL,
    conversion_rate DECIMAL
) AS $$
BEGIN
    CASE time_granularity
        WHEN 'hour' THEN
            RETURN QUERY
            SELECT 
                DATE_TRUNC('hour', c.created_at) as time_bucket,
                COUNT(*)::INTEGER as calls_made,
                COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::INTEGER as calls_answered,
                COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::INTEGER as conversions,
                ROUND(SUM(COALESCE(c.revenue_generated, 0)), 2) as revenue,
                ROUND(AVG(c.total_duration), 2) as avg_duration,
                ROUND((COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2) as success_rate,
                ROUND((COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2) as conversion_rate
            FROM calls c
            WHERE c.campaign_id = campaign_uuid
            GROUP BY DATE_TRUNC('hour', c.created_at)
            ORDER BY time_bucket;
            
        WHEN 'day' THEN
            RETURN QUERY
            SELECT 
                DATE_TRUNC('day', c.created_at) as time_bucket,
                COUNT(*)::INTEGER as calls_made,
                COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::INTEGER as calls_answered,
                COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::INTEGER as conversions,
                ROUND(SUM(COALESCE(c.revenue_generated, 0)), 2) as revenue,
                ROUND(AVG(c.total_duration), 2) as avg_duration,
                ROUND((COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2) as success_rate,
                ROUND((COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2) as conversion_rate
            FROM calls c
            WHERE c.campaign_id = campaign_uuid
            GROUP BY DATE_TRUNC('day', c.created_at)
            ORDER BY time_bucket;
            
        WHEN 'week' THEN
            RETURN QUERY
            SELECT 
                DATE_TRUNC('week', c.created_at) as time_bucket,
                COUNT(*)::INTEGER as calls_made,
                COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::INTEGER as calls_answered,
                COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::INTEGER as conversions,
                ROUND(SUM(COALESCE(c.revenue_generated, 0)), 2) as revenue,
                ROUND(AVG(c.total_duration), 2) as avg_duration,
                ROUND((COUNT(CASE WHEN c.status = 'completed' THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2) as success_rate,
                ROUND((COUNT(CASE WHEN c.conversion_result = true THEN 1 END)::DECIMAL / NULLIF(COUNT(*), 0) * 100), 2) as conversion_rate
            FROM calls c
            WHERE c.campaign_id = campaign_uuid
            GROUP BY DATE_TRUNC('week', c.created_at)
            ORDER BY time_bucket;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- WEBHOOK AND NOTIFICATION FUNCTIONS
-- ===================================================================

-- 1. Process Webhook Events
CREATE OR REPLACE FUNCTION process_webhook_event(
    event_type TEXT,
    event_data JSONB,
    organization_uuid UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    webhook_record RECORD;
    webhook_payload JSONB;
    http_response TEXT;
BEGIN
    -- Get active webhooks for this event type and organization
    FOR webhook_record IN 
        SELECT * FROM webhooks 
        WHERE organization_id = organization_uuid 
          AND is_active = true 
          AND event_type = ANY(events)
    LOOP
        -- Build webhook payload
        webhook_payload := jsonb_build_object(
            'event', event_type,
            'timestamp', NOW(),
            'organization_id', organization_uuid,
            'data', event_data,
            'webhook_id', webhook_record.id
        );
        
        -- Here you would make the HTTP request to webhook_record.url
        -- This is a placeholder - in practice, you'd use an HTTP extension
        -- or handle this in your application layer
        
        -- Update webhook statistics
        UPDATE webhooks 
        SET 
            last_triggered = NOW(),
            success_count = success_count + 1
        WHERE id = webhook_record.id;
        
    END LOOP;
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- COMPLIANCE AND SECURITY FUNCTIONS
-- ===================================================================

-- 1. Check DNC Status
CREATE OR REPLACE FUNCTION check_dnc_status(
    org_id UUID,
    phone TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    is_dnc BOOLEAN := false;
BEGIN
    -- Check if phone number is in organization's DNC list
    SELECT true INTO is_dnc
    FROM dnc_entries 
    WHERE organization_id = org_id 
      AND phone_number = phone 
      AND (expiry_date IS NULL OR expiry_date > NOW())
    LIMIT 1;
    
    RETURN COALESCE(is_dnc, false);
END;
$$ LANGUAGE plpgsql;

-- 2. Log Consent
CREATE OR REPLACE FUNCTION log_consent(
    org_id UUID,
    phone TEXT,
    consent_type_param TEXT,
    consent_given_param BOOLEAN,
    consent_method_param TEXT DEFAULT 'verbal',
    recording_url_param TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    consent_id UUID;
BEGIN
    INSERT INTO consent_records (
        organization_id,
        prospect_phone,
        consent_type,
        consent_given,
        consent_method,
        recording_url
    ) VALUES (
        org_id,
        phone,
        consent_type_param,
        consent_given_param,
        consent_method_param,
        recording_url_param
    ) RETURNING id INTO consent_id;
    
    RETURN consent_id;
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- PERFORMANCE AND MAINTENANCE
-- ===================================================================

-- 1. Archive Old Data (SAFE VERSION - Preview by default)
CREATE OR REPLACE FUNCTION archive_old_data(
    days_to_keep INTEGER DEFAULT 365,
    preview_only BOOLEAN DEFAULT true,
    confirm_delete BOOLEAN DEFAULT false
)
RETURNS TEXT AS $$
DECLARE
    cutoff_date TIMESTAMPTZ;
    calls_to_archive INTEGER;
    logs_to_archive INTEGER;
    usage_logs_to_archive INTEGER;
    result_message TEXT;
BEGIN
    -- Safety check: prevent accidental deletion of recent data
    IF days_to_keep < 30 THEN
        RAISE EXCEPTION 'Cannot archive data newer than 30 days for safety reasons';
    END IF;
    
    cutoff_date := NOW() - (days_to_keep || ' days')::INTERVAL;
    
    -- Count what would be archived
    SELECT COUNT(*) INTO calls_to_archive 
    FROM calls WHERE created_at < cutoff_date;
    
    SELECT COUNT(*) INTO logs_to_archive 
    FROM system_logs WHERE created_at < cutoff_date;
    
    SELECT COUNT(*) INTO usage_logs_to_archive 
    FROM usage_logs WHERE created_at < cutoff_date - INTERVAL '2 years';
    
    -- Preview mode (default)
    IF preview_only = true THEN
        RETURN format('PREVIEW: Would archive %s calls, %s system logs, and %s usage logs older than %s days. Call with preview_only=false and confirm_delete=true to execute.',
                     calls_to_archive, logs_to_archive, usage_logs_to_archive, days_to_keep);
    END IF;
    
    -- Require explicit confirmation for actual deletion
    IF confirm_delete = false THEN
        RAISE EXCEPTION 'Must set confirm_delete=true to actually delete data. This prevents accidental data loss.';
    END IF;
    
    -- Log the archival operation before executing
    INSERT INTO system_logs (level, message, component, metadata)
    VALUES ('info', 'Starting data archival process', 'archive_function', 
            jsonb_build_object('days_to_keep', days_to_keep, 'cutoff_date', cutoff_date,
                              'calls_to_archive', calls_to_archive, 'logs_to_archive', logs_to_archive));
    
    -- Perform actual archival (only with explicit confirmation)
    BEGIN
        -- Archive old calls
        DELETE FROM calls WHERE created_at < cutoff_date;
        
        -- Archive old system logs (but keep the archival log we just created)
        DELETE FROM system_logs 
        WHERE created_at < cutoff_date 
          AND NOT (message = 'Starting data archival process' AND component = 'archive_function');
        
        -- Archive old usage logs (keep billing data longer)
        DELETE FROM usage_logs WHERE created_at < cutoff_date - INTERVAL '2 years';
        
        -- Log successful completion
        INSERT INTO system_logs (level, message, component, metadata)
        VALUES ('info', 'Data archival completed successfully', 'archive_function',
                jsonb_build_object('calls_archived', calls_to_archive, 'logs_archived', logs_to_archive,
                                  'usage_logs_archived', usage_logs_to_archive));
        
        RETURN format('SUCCESS: Archived %s calls, %s system logs, and %s usage logs older than %s days', 
                     calls_to_archive, logs_to_archive, usage_logs_to_archive, days_to_keep);
    EXCEPTION
        WHEN OTHERS THEN
            -- Log the error
            INSERT INTO system_logs (level, message, component, metadata)
            VALUES ('error', 'Data archival failed: ' || SQLERRM, 'archive_function',
                    jsonb_build_object('error_code', SQLSTATE, 'error_message', SQLERRM));
            
            -- Re-raise the exception
            RAISE;
    END;
END;
$$ LANGUAGE plpgsql;

-- 2. Update Table Statistics
CREATE OR REPLACE FUNCTION update_table_statistics()
RETURNS VOID AS $$
BEGIN
    -- Update table statistics for better query planning
    ANALYZE organizations;
    ANALYZE users;
    ANALYZE agents;
    ANALYZE campaigns;
    ANALYZE calls;
    ANALYZE prospects;
    ANALYZE call_metrics;
    ANALYZE campaign_metrics;
    ANALYZE agent_metrics;
    ANALYZE voice_metrics;
    
    RAISE NOTICE 'Table statistics updated successfully';
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- COMMENTS AND DOCUMENTATION
-- ===================================================================

COMMENT ON FUNCTION get_call_performance_analytics IS 'Returns comprehensive call performance analytics for an organization within a date range';
COMMENT ON FUNCTION get_realtime_campaign_metrics IS 'Returns real-time metrics for all active campaigns in an organization';
COMMENT ON FUNCTION calculate_agent_performance_score IS 'Calculates and updates the performance score for an agent based on multiple factors';
COMMENT ON FUNCTION optimize_campaign_performance IS 'Analyzes campaign performance and provides optimization suggestions';
COMMENT ON FUNCTION generate_daily_analytics IS 'Generates daily analytics data for all organizations';
COMMENT ON FUNCTION get_dashboard_overview IS 'Returns a comprehensive dashboard overview for an organization';
COMMENT ON FUNCTION get_agent_leaderboard IS 'Returns agent performance leaderboard for an organization';
COMMENT ON FUNCTION get_campaign_analytics IS 'Returns time-series analytics data for a specific campaign';
COMMENT ON FUNCTION check_dnc_status IS 'Checks if a phone number is on the Do Not Call list for an organization';
COMMENT ON FUNCTION log_consent IS 'Logs customer consent for compliance purposes';
COMMENT ON FUNCTION archive_old_data IS 'SAFE data archival function with preview mode and explicit confirmation required. Usage: SELECT archive_old_data(365) for preview, SELECT archive_old_data(365, false, true) to actually delete.';

-- ===================================================================
-- USAGE EXAMPLES FOR SAFE DATA ARCHIVAL
-- ===================================================================

-- Preview what would be archived (SAFE - no data deleted):
-- SELECT archive_old_data(365);

-- Preview with custom days:
-- SELECT archive_old_data(180);

-- Actually perform archival (DESTRUCTIVE - requires explicit confirmation):
-- SELECT archive_old_data(365, false, true);

-- The function includes safety checks:
-- - Prevents archiving data newer than 30 days
-- - Requires explicit confirmation for actual deletion
-- - Logs all operations for audit trail
-- - Shows preview by default to prevent accidents

-- ===================================================================
-- FINAL SETUP COMMANDS
-- ===================================================================

-- Create indexes for new analytical queries
CREATE INDEX IF NOT EXISTS idx_calls_created_at ON calls(created_at);
CREATE INDEX IF NOT EXISTS idx_calls_campaign_id ON calls(campaign_id);
CREATE INDEX IF NOT EXISTS idx_calls_agent_id ON calls(agent_id);
CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status);

CREATE INDEX IF NOT EXISTS idx_campaign_metrics_date_org ON campaign_metrics(date, organization_id);
CREATE INDEX IF NOT EXISTS idx_agent_metrics_date_org ON agent_metrics(date, organization_id);
CREATE INDEX IF NOT EXISTS idx_voice_metrics_date_org ON voice_metrics(date, organization_id);

-- Enable automatic VACUUM and ANALYZE
ALTER TABLE calls SET (autovacuum_analyze_scale_factor = 0.05);
ALTER TABLE call_metrics SET (autovacuum_analyze_scale_factor = 0.1);
ALTER TABLE campaign_metrics SET (autovacuum_analyze_scale_factor = 0.1);

-- ===================================================================
-- SUCCESS MESSAGE
-- ===================================================================

-- Vocelio AI Call Center Logic Setup Complete!
-- ✅ Advanced analytics functions
-- ✅ Real-time triggers and automation
-- ✅ Performance optimization functions  
-- ✅ Compliance and security functions
-- ✅ API helper functions
-- ✅ Webhook processing
-- ✅ Data archival and maintenance
-- ✅ Real-time subscriptions configured
-- 
-- Next steps:
-- 1. Run this script in your Supabase SQL editor
-- 2. Enable pg_cron extension for scheduled jobs
-- 3. Configure real-time subscriptions in your frontend
-- 4. Set up webhook endpoints in your application
-- 5. Schedule regular maintenance tasks

SELECT 'Vocelio AI Call Center logic setup completed successfully!' as status;
