"""Generate validation reports and visualizations."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any
from core.validation_engine import ValidationResult, ValidationSummary
from config.settings import SEVERITY_LEVELS
from utils.helpers import get_current_timestamp

class ReportGenerator:
    """Generate comprehensive validation reports."""
    
    def __init__(self, results: List[ValidationResult], summary: ValidationSummary):
        self.results = results
        self.summary = summary
    
    def generate_summary_metrics(self) -> Dict[str, Any]:
        """Generate key summary metrics."""
        return {
            'overall_score': self.summary.overall_score,
            'pass_rate': (self.summary.passed / self.summary.total_rules * 100) if self.summary.total_rules > 0 else 0,
            'critical_issues': self.summary.critical_failures,
            'total_issues': self.summary.failed,
            'validation_time': self.summary.execution_time,
            'document_status': 'VALID' if self.summary.critical_failures == 0 else 'INVALID'
        }
    
    def create_summary_chart(self) -> go.Figure:
        """Create summary visualization chart."""
        # Create pie chart for validation results
        labels = ['Passed', 'Critical', 'High', 'Medium', 'Low']
        values = [
            self.summary.passed,
            self.summary.critical_failures,
            self.summary.high_failures,
            self.summary.medium_failures,
            self.summary.low_failures
        ]
        colors = ['#28a745', '#dc3545', '#fd7e14', '#ffc107', '#17a2b8']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title="Validation Results Overview",
            annotations=[dict(text=f'{self.summary.overall_score:.1f}%<br>Score', 
                            x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig
    
    def create_severity_breakdown_chart(self) -> go.Figure:
        """Create severity breakdown chart."""
        severity_data = {
            'Critical': {'passed': 0, 'failed': self.summary.critical_failures},
            'High': {'passed': 0, 'failed': self.summary.high_failures},
            'Medium': {'passed': 0, 'failed': self.summary.medium_failures},
            'Low': {'passed': 0, 'failed': self.summary.low_failures}
        }
        
        # Calculate passed for each severity
        for result in self.results:
            if result.passed:
                severity_data[result.severity]['passed'] += 1
        
        severities = list(severity_data.keys())
        passed_counts = [severity_data[s]['passed'] for s in severities]
        failed_counts = [severity_data[s]['failed'] for s in severities]
        
        fig = go.Figure(data=[
            go.Bar(name='Passed', x=severities, y=passed_counts, marker_color='#28a745'),
            go.Bar(name='Failed', x=severities, y=failed_counts, marker_color='#dc3545')
        ])
        
        fig.update_layout(
            title='Validation Results by Severity',
            xaxis_title='Severity Level',
            yaxis_title='Number of Rules',
            barmode='stack'
        )
        
        return fig
    
    def create_category_breakdown_chart(self) -> go.Figure:
        """Create category breakdown chart."""
        category_data = {}
        
        for result in self.results:
            if result.category not in category_data:
                category_data[result.category] = {'passed': 0, 'failed': 0}
            
            if result.passed:
                category_data[result.category]['passed'] += 1
            else:
                category_data[result.category]['failed'] += 1
        
        categories = list(category_data.keys())
        passed_counts = [category_data[c]['passed'] for c in categories]
        failed_counts = [category_data[c]['failed'] for c in categories]
        
        fig = go.Figure(data=[
            go.Bar(name='Passed', x=categories, y=passed_counts, marker_color='#28a745'),
            go.Bar(name='Failed', x=categories, y=failed_counts, marker_color='#dc3545')
        ])
        
        fig.update_layout(
            title='Validation Results by Category',
            xaxis_title='Validation Category',
            yaxis_title='Number of Rules',
            barmode='stack',
            xaxis_tickangle=-45
        )
        
        return fig
    
    def generate_results_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame."""
        data = []
        for result in self.results:
            data.append({
                'Rule ID': result.rule_id,
                'Description': result.rule_description,
                'Category': result.category,
                'Severity': result.severity,
                'Status': 'PASS' if result.passed else 'FAIL',
                'Details': result.details,
                'Execution Time (ms)': round(result.execution_time * 1000, 2)
            })
        
        return pd.DataFrame(data)
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary text."""
        status = "VALID" if self.summary.critical_failures == 0 else "INVALID"
        
        summary_text = f"""
# BRD Validation Executive Summary

**Document Status:** {status}
**Overall Score:** {self.summary.overall_score:.1f}%
**Validation Date:** {self.summary.timestamp}

## Key Metrics
- **Total Rules Evaluated:** {self.summary.total_rules}
- **Rules Passed:** {self.summary.passed} ({self.summary.passed/self.summary.total_rules*100:.1f}%)
- **Rules Failed:** {self.summary.failed} ({self.summary.failed/self.summary.total_rules*100:.1f}%)

## Issue Breakdown
- **Critical Issues:** {self.summary.critical_failures} (Must fix before approval)
- **High Priority Issues:** {self.summary.high_failures} (Should fix before implementation)
- **Medium Priority Issues:** {self.summary.medium_failures} (Recommended improvements)
- **Low Priority Issues:** {self.summary.low_failures} (Nice to have)

## Recommendation
"""
        
        if self.summary.critical_failures > 0:
            summary_text += f"❌ **Document requires immediate attention.** {self.summary.critical_failures} critical issues must be resolved before proceeding."
        elif self.summary.high_failures > 0:
            summary_text += f"⚠️ **Document needs improvements.** Address {self.summary.high_failures} high-priority issues before implementation."
        elif self.summary.medium_failures > 0:
            summary_text += f"✅ **Document is acceptable with minor improvements.** Consider addressing {self.summary.medium_failures} medium-priority issues."
        else:
            summary_text += "✅ **Document meets all validation criteria and is ready for implementation.**"
        
        return summary_text
    
    def generate_detailed_report(self) -> str:
        """Generate detailed validation report."""
        report = self.generate_executive_summary()
        
        # Add failed validations details
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            report += "\n\n## Failed Validations\n\n"
            
            # Group by severity
            for severity in ['Critical', 'High', 'Medium', 'Low']:
                severity_failures = [r for r in failed_results if r.severity == severity]
                if severity_failures:
                    icon = SEVERITY_LEVELS[severity]['icon']
                    report += f"\n### {icon} {severity} Issues\n\n"
                    
                    for result in severity_failures:
                        report += f"**{result.rule_id}:** {result.rule_description}\n"
                        if result.details:
                            report += f"*Details:* {result.details}\n"
                        report += "\n"
        
        return report