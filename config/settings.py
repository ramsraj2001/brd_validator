"""Application settings and configuration."""

import os
from pathlib import Path

# Application settings
APP_TITLE = "BRD Validation Framework"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Comprehensive Business Requirements Document Validator"

# File settings
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
SUPPORTED_FORMATS = ['.docx', '.pdf', '.txt', '.json', '.md']

# Validation settings
VALIDATION_TIMEOUT = 300  # 5 minutes
MAX_ERRORS_DISPLAY = 100

# Paths
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMP_DIR = BASE_DIR / "temp"

# Ensure temp directory exists
TEMP_DIR.mkdir(exist_ok=True)

# Severity levels
SEVERITY_LEVELS = {
    'Critical': {'color': '#ff4b4b', 'icon': '🔴', 'priority': 1},
    'High': {'color': '#ff8c00', 'icon': '🟠', 'priority': 2},
    'Medium': {'color': '#ffd700', 'icon': '🟡', 'priority': 3},
    'Low': {'color': '#90ee90', 'icon': '🟢', 'priority': 4}
}

# BRD Structure
BRD_SECTIONS = {
    0: "Project Foundation",
    1: "Organizational Structure", 
    2: "Data & Entity Management",
    3: "Functions & Operations",
    4: "Business Process Workflows",
    5: "Intelligence & Analytics"
}

BRD_NODES = {
    "0.1": "Executive Summary & Business Case",
    "0.2": "Requirements Summary Dashboard",
    "0.3": "Discovery Metadata & Quality",
    "1.1": "Hierarchy & Authority Structure",
    "1.2": "Role Definitions",
    "1.3": "Department Structure",
    "1.4": "Performance Management",
    "2.1": "Entity Management",
    "2.2": "Entity Relationships",
    "2.3": "Business Rules",
    "2.4": "Data Flow Patterns",
    "3.1": "Function Discovery",
    "3.2": "Input-Process-Output Specifications",
    "3.3": "Function Validation",
    "3.4": "Function Integration",
    "4.1": "Workflow Assembly",
    "4.2": "Data Flow Validation",
    "4.3": "Workflow Logic",
    "4.4": "Gap Analysis"
}