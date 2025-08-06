"""
Reports Service
Business logic for report generation and data export
"""

import asyncio
import os
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4
from pathlib import Path
import pandas as pd
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from shared.database.client import get_database
from schemas.reports import (
    ReportRequest,
    ReportResponse,
    ReportStatus,
    ExportFormat,
    ScheduledReport
)

logger = logging.getLogger(__name__)

class ReportsService:
    """Service for managing reports and data exports"""
    
    def __init__(self):
        self._reports_cache = {}
        self.export_path = Path("/tmp/exports")
        self.export_path.mkdir(exist_ok=True)
    
    async def create_report_job(
        self, 
        organization_id: str, 
        user_id: str, 
        request: ReportRequest
    ) -> str:
        """Create a new report generation job"""
        try:
            report_id = str(uuid4())
            
            # Store report job in database
            db = await get_database()
            await db.from_("reports").insert({
                "id": report_id,
                "organization_id": organization_id,
                "user_id": user_id,
                "report_type": request.report_type,
                "parameters": request.parameters,
                "format": request.format.value,
                "status": ReportStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            return report_id
            
        except Exception as e:
            logger.error(f"Error creating report job: {str(e)}")
            raise
    
    async def generate_report_async(self, report_id: str, request: ReportRequest):
        """Generate report asynchronously"""
        try:
            logger.info(f"Starting report generation: {report_id}")
            
            # Update status to processing
            await self._update_report_status(report_id, ReportStatus.PROCESSING)
            
            # Generate report based on type
            if request.report_type == "dashboard_summary":
                file_path = await self._generate_dashboard_summary_report(report_id, request)
            elif request.report_type == "metrics_analysis":
                file_path = await self._generate_metrics_analysis_report(report_id, request)
            elif request.report_type == "performance_report":
                file_path = await self._generate_performance_report(report_id, request)
            else:
                file_path = await self._generate_custom_report(report_id, request)
            
            # Update status to completed
            await self._update_report_status(
                report_id, 
                ReportStatus.COMPLETED,
                file_path=file_path
            )
            
            logger.info(f"Report generation completed: {report_id}")
            
        except Exception as e:
            logger.error(f"Error generating report {report_id}: {str(e)}")
            await self._update_report_status(report_id, ReportStatus.FAILED, error=str(e))
    
    async def _update_report_status(
        self, 
        report_id: str, 
        status: ReportStatus, 
        file_path: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update report status in database"""
        try:
            db = await get_database()
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if file_path:
                update_data["file_path"] = file_path
            if error:
                update_data["error_message"] = error
            
            await db.from_("reports").update(update_data).eq("id", report_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating report status: {str(e)}")
    
    async def _generate_dashboard_summary_report(self, report_id: str, request: ReportRequest) -> str:
        """Generate dashboard summary report"""
        # Get dashboard data
        data = await self.get_comprehensive_dashboard_data(
            request.parameters.get("organization_id"),
            request.parameters.get("time_range", "30d")
        )
        
        if request.format == ExportFormat.PDF:
            return await self._create_pdf_report(report_id, "Dashboard Summary", data)
        elif request.format == ExportFormat.EXCEL:
            return await self._create_excel_report(report_id, "Dashboard Summary", data)
        else:
            return await self._create_csv_report(report_id, "Dashboard Summary", data)
    
    async def _generate_metrics_analysis_report(self, report_id: str, request: ReportRequest) -> str:
        """Generate metrics analysis report"""
        # Simulate metrics analysis data
        data = {
            "report_type": "Metrics Analysis",
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": [
                {"metric": "Total Calls", "value": 125678, "change": "+12.3%"},
                {"metric": "Success Rate", "value": "23.4%", "change": "+2.1%"},
                {"metric": "Revenue", "value": "$2,847,592", "change": "+18.9%"},
                {"metric": "AI Score", "value": "94.7", "change": "+5.4%"}
            ],
            "trends": [
                {"period": "Last 7 days", "calls": 8750, "success_rate": 23.8},
                {"period": "Last 30 days", "calls": 125678, "success_rate": 23.4},
                {"period": "Last 90 days", "calls": 387654, "success_rate": 22.1}
            ]
        }
        
        if request.format == ExportFormat.PDF:
            return await self._create_pdf_report(report_id, "Metrics Analysis", data)
        elif request.format == ExportFormat.EXCEL:
            return await self._create_excel_report(report_id, "Metrics Analysis", data)
        else:
            return await self._create_csv_report(report_id, "Metrics Analysis", data)
    
    async def _generate_performance_report(self, report_id: str, request: ReportRequest) -> str:
        """Generate performance report"""
        # Simulate performance data
        data = {
            "report_type": "Performance Report",
            "generated_at": datetime.utcnow().isoformat(),
            "agents": [
                {"name": "Professional Sarah", "calls": 23847, "success_rate": 34.5, "revenue": 892340},
                {"name": "Solar Expert Mike", "calls": 18923, "success_rate": 42.1, "revenue": 1234567},
                {"name": "Insurance Pro Lisa", "calls": 15632, "success_rate": 29.8, "revenue": 456789}
            ],
            "campaigns": [
                {"name": "Solar Energy Q1", "calls": 45678, "success_rate": 38.2, "revenue": 1876543},
                {"name": "Insurance Drive", "calls": 32456, "success_rate": 25.7, "revenue": 987654},
                {"name": "Real Estate Premium", "calls": 28945, "success_rate": 42.8, "revenue": 2345678}
            ]
        }
        
        if request.format == ExportFormat.PDF:
            return await self._create_pdf_report(report_id, "Performance Report", data)
        elif request.format == ExportFormat.EXCEL:
            return await self._create_excel_report(report_id, "Performance Report", data)
        else:
            return await self._create_csv_report(report_id, "Performance Report", data)
    
    async def _generate_custom_report(self, report_id: str, request: ReportRequest) -> str:
        """Generate custom report"""
        data = {
            "report_type": "Custom Report",
            "parameters": request.parameters,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return await self._create_json_report(report_id, "Custom Report", data)
    
    async def _create_pdf_report(self, report_id: str, title: str, data: Dict[str, Any]) -> str:
        """Create PDF report"""
        file_path = self.export_path / f"report_{report_id}.pdf"
        
        doc = SimpleDocTemplate(str(file_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Generated timestamp
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Add data sections
        if 'metrics' in data:
            story.append(Paragraph("<b>Key Metrics</b>", styles['Heading2']))
            for metric in data['metrics']:
                story.append(Paragraph(f"• {metric['metric']}: {metric['value']} ({metric['change']})", styles['Normal']))
            story.append(Spacer(1, 12))
        
        if 'agents' in data:
            story.append(Paragraph("<b>Agent Performance</b>", styles['Heading2']))
            agent_data = [['Agent', 'Calls', 'Success Rate', 'Revenue']]
            for agent in data['agents']:
                agent_data.append([agent['name'], str(agent['calls']), f"{agent['success_rate']}%", f"${agent['revenue']:,}"])
            
            table = Table(agent_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), '#4CAF50'),
                ('TEXTCOLOR', (0, 0), (-1, 0), '#FFFFFF'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), '#F8F9FA'),
                ('GRID', (0, 0), (-1, -1), 1, '#CCCCCC')
            ]))
            story.append(table)
        
        doc.build(story)
        return str(file_path)
    
    async def _create_excel_report(self, report_id: str, title: str, data: Dict[str, Any]) -> str:
        """Create Excel report"""
        file_path = self.export_path / f"report_{report_id}.xlsx"
        
        with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Report': [title],
                'Generated': [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Metrics sheet
            if 'metrics' in data:
                metrics_df = pd.DataFrame(data['metrics'])
                metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
            
            # Agents sheet
            if 'agents' in data:
                agents_df = pd.DataFrame(data['agents'])
                agents_df.to_excel(writer, sheet_name='Agents', index=False)
            
            # Campaigns sheet
            if 'campaigns' in data:
                campaigns_df = pd.DataFrame(data['campaigns'])
                campaigns_df.to_excel(writer, sheet_name='Campaigns', index=False)
        
        return str(file_path)
    
    async def _create_csv_report(self, report_id: str, title: str, data: Dict[str, Any]) -> str:
        """Create CSV report"""
        file_path = self.export_path / f"report_{report_id}.csv"
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            if 'metrics' in data:
                fieldnames = ['metric', 'value', 'change']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data['metrics'])
            elif 'agents' in data:
                fieldnames = ['name', 'calls', 'success_rate', 'revenue']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data['agents'])
        
        return str(file_path)
    
    async def _create_json_report(self, report_id: str, title: str, data: Dict[str, Any]) -> str:
        """Create JSON report"""
        file_path = self.export_path / f"report_{report_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, default=str)
        
        return str(file_path)
    
    async def get_report_status(self, report_id: str, organization_id: str) -> ReportResponse:
        """Get report status"""
        try:
            db = await get_database()
            result = await db.from_("reports").select("*").eq("id", report_id).eq("organization_id", organization_id).single().execute()
            
            if not result.data:
                raise Exception("Report not found")
            
            report = result.data
            return ReportResponse(
                report_id=report_id,
                status=ReportStatus(report['status']),
                message=f"Report {report['status']}",
                created_at=datetime.fromisoformat(report['created_at']),
                completed_at=datetime.fromisoformat(report['updated_at']) if report.get('updated_at') else None,
                download_url=f"/api/v1/reports/download/{report_id}" if report['status'] == 'completed' else None,
                file_size=None,
                error_message=report.get('error_message')
            )
            
        except Exception as e:
            logger.error(f"Error getting report status: {str(e)}")
            raise
    
    async def get_comprehensive_dashboard_data(self, organization_id: str, time_range: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for export"""
        return {
            "organization_id": organization_id,
            "time_range": time_range,
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": [
                {"metric": "Total Calls", "value": 125678, "period": time_range},
                {"metric": "Success Rate", "value": "23.4%", "period": time_range},
                {"metric": "Revenue", "value": "$2,847,592", "period": time_range}
            ],
            "summary": {
                "total_calls": 125678,
                "successful_calls": 29409,
                "success_rate": 23.4,
                "total_revenue": 2847592.50,
                "avg_call_duration": 185,
                "ai_optimization_score": 94.7
            }
        }
    
    def get_media_type(self, format: str) -> str:
        """Get media type for format"""
        media_types = {
            "pdf": "application/pdf",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "csv": "text/csv",
            "json": "application/json"
        }
        return media_types.get(format.lower(), "application/octet-stream")


# Dependency injection
_reports_service = None

async def get_reports_service() -> ReportsService:
    """Get reports service instance"""
    global _reports_service
    if _reports_service is None:
        _reports_service = ReportsService()
    return _reports_service