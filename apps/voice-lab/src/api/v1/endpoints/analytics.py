"""
Voice Lab - Analytics Endpoints
Handles voice usage analytics, performance insights, and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from services.analytics_service import AnalyticsService
from schemas.analytics import (
    VoiceAnalytics,
    UsageReport,
    PerformanceInsights,
    CostAnalysis,
    TrendReport
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

@router.get("/overview", response_model=Dict)
async def get_analytics_overview(
    days: int = Query(30, description="Number of days for analytics"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics overview"""
    try:
        overview = await analytics_service.get_analytics_overview(
            user_id=current_user.id,
            days=days
        )
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics overview failed: {str(e)}")

@router.get("/voice/{voice_id}/analytics", response_model=VoiceAnalytics)
async def get_voice_analytics(
    voice_id: str,
    days: int = Query(30, description="Number of days for analytics"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analytics for specific voice"""
    analytics = await analytics_service.get_voice_analytics(
        voice_id=voice_id,
        user_id=current_user.id,
        days=days
    )
    if not analytics:
        raise HTTPException(status_code=404, detail="Voice analytics not found")
    return analytics

@router.get("/usage-report", response_model=UsageReport)
async def get_usage_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    voice_ids: Optional[List[str]] = Query(None),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Generate detailed usage report"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    report = await analytics_service.generate_usage_report(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        voice_ids=voice_ids
    )
    return report

@router.get("/performance-insights", response_model=PerformanceInsights)
async def get_performance_insights(
    days: int = Query(30, description="Number of days for analysis"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered performance insights and recommendations"""
    insights = await analytics_service.get_performance_insights(
        user_id=current_user.id,
        days=days
    )
    return insights

@router.get("/cost-analysis", response_model=CostAnalysis)
async def get_cost_analysis(
    days: int = Query(30, description="Number of days for analysis"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get detailed cost analysis and optimization suggestions"""
    analysis = await analytics_service.get_cost_analysis(
        user_id=current_user.id,
        days=days
    )
    return analysis

@router.get("/trends", response_model=TrendReport)
async def get_trend_analysis(
    metric: str = Query("usage", description="Metric to analyze (usage, quality, cost)"),
    days: int = Query(90, description="Number of days for trend analysis"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get trend analysis for specified metrics"""
    valid_metrics = ["usage", "quality", "cost", "performance", "satisfaction"]
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Must be one of: {valid_metrics}")
    
    trends = await analytics_service.get_trend_analysis(
        user_id=current_user.id,
        metric=metric,
        days=days
    )
    return trends

@router.get("/top-voices")
async def get_top_performing_voices(
    limit: int = Query(10, description="Number of top voices to return"),
    metric: str = Query("usage", description="Ranking metric"),
    days: int = Query(30, description="Number of days for analysis"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get top performing voices based on specified metric"""
    top_voices = await analytics_service.get_top_voices(
        user_id=current_user.id,
        limit=limit,
        metric=metric,
        days=days
    )
    return {
        "metric": metric,
        "period_days": days,
        "voices": top_voices
    }

@router.get("/optimization-recommendations")
async def get_optimization_recommendations(
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered optimization recommendations"""
    recommendations = await analytics_service.get_optimization_recommendations(
        user_id=current_user.id
    )
    return recommendations

@router.get("/real-time-metrics")
async def get_real_time_metrics(
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get real-time voice lab metrics"""
    metrics = await analytics_service.get_real_time_metrics(
        user_id=current_user.id
    )
    return metrics

@router.post("/custom-report")
async def generate_custom_report(
    report_config: Dict,
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Generate custom analytics report"""
    try:
        report = await analytics_service.generate_custom_report(
            user_id=current_user.id,
            config=report_config
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom report generation failed: {str(e)}")

@router.get("/export/{format}")
async def export_analytics(
    format: str,
    days: int = Query(30, description="Number of days for export"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Export analytics data in specified format"""
    valid_formats = ["csv", "json", "pdf", "excel"]
    if format not in valid_formats:
        raise HTTPException(status_code=400, detail=f"Invalid format. Must be one of: {valid_formats}")
    
    try:
        export_file = await analytics_service.export_analytics(
            user_id=current_user.id,
            format=format,
            days=days
        )
        
        return {
            "format": format,
            "file_path": export_file,
            "download_url": f"/voice-lab/analytics/download/{export_file}",
            "expires_at": datetime.now() + timedelta(hours=24)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/benchmarks/industry")
async def get_industry_benchmarks(
    industry: Optional[str] = Query(None, description="Specific industry for benchmarks"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get industry benchmarks for voice performance"""
    benchmarks = await analytics_service.get_industry_benchmarks(
        user_id=current_user.id,
        industry=industry
    )
    return benchmarks

@router.get("/sentiment-analysis")
async def get_sentiment_analysis(
    voice_ids: Optional[List[str]] = Query(None),
    days: int = Query(30, description="Number of days for analysis"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get sentiment analysis of voice usage and feedback"""
    sentiment = await analytics_service.get_sentiment_analysis(
        user_id=current_user.id,
        voice_ids=voice_ids,
        days=days
    )
    return sentiment

@router.get("/alerts/performance")
async def get_performance_alerts(
    severity: Optional[str] = Query(None, description="Alert severity (low, medium, high, critical)"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get performance alerts and anomaly detection"""
    alerts = await analytics_service.get_performance_alerts(
        user_id=current_user.id,
        severity=severity
    )
    return alerts

@router.post("/dashboards/custom")
async def create_custom_dashboard(
    dashboard_config: Dict,
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Create custom analytics dashboard"""
    try:
        dashboard = await analytics_service.create_custom_dashboard(
            user_id=current_user.id,
            config=dashboard_config
        )
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")

@router.get("/predictions/usage")
async def get_usage_predictions(
    days_ahead: int = Query(30, description="Number of days to predict"),
    analytics_service: AnalyticsService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered usage predictions"""
    predictions = await analytics_service.get_usage_predictions(
        user_id=current_user.id,
        days_ahead=days_ahead
    )
    return predictions
