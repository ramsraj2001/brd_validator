"""Validation rules configuration and definitions."""

from typing import Dict, List, Any, Callable
from config.settings import SEVERITY_LEVELS

class ValidationRule:
    """Individual validation rule definition."""
    
    def __init__(self, rule_id: str, description: str, severity: str, 
                 validation_func: Callable, category: str):
        self.rule_id = rule_id
        self.description = description
        self.severity = severity
        self.validation_func = validation_func
        self.category = category
        self.priority = SEVERITY_LEVELS[severity]['priority']

# Validation rule definitions
VALIDATION_RULES = {
    # Structural Completeness Validations
    'V001': ValidationRule(
        'V001', 
        'All 5 main sections (0-4) must be present',
        'Critical',
        lambda data: len([s for s in data['parsed_data']['sections'].values() if s['present']]) >= 5,
        'Structural Completeness'
    ),
    
    'V002': ValidationRule(
        'V002',
        'Each section must contain all required nodes',
        'Critical', 
        lambda data: all(
            node['present'] for node in data['parsed_data']['nodes'].values()
        ),
        'Structural Completeness'
    ),
    
    'V006': ValidationRule(
        'V006',
        'All 18 nodes must be present and populated',
        'Critical',
        lambda data: len([n for n in data['parsed_data']['nodes'].values() if n['present']]) >= 18,
        'Structural Completeness'
    ),
    
    'V013': ValidationRule(
        'V013',
        'No placeholder text (e.g., "TBD", "TODO") allowed in production',
        'High',
        lambda data: len(data['parsed_data']['content_analysis']['nodes_with_placeholders']) == 0,
        'Content Quality'
    ),
    
    'V014': ValidationRule(
        'V014',
        'Minimum character length requirements per field type',
        'Medium',
        lambda data: data['parsed_data']['content_analysis']['total_word_count'] >= 1000,
        'Content Quality'
    ),
    
    # Project Foundation Validations
    'V015': ValidationRule(
        'V015',
        'user_intent_category must be one of predefined values',
        'High',
        lambda data: _validate_user_intent_category(data),
        'Project Foundation'
    ),
    
    'V020': ValidationRule(
        'V020',
        'function_coverage_stats percentages must add up to 100%',
        'Medium',
        lambda data: _validate_percentage_sum(data, '0.2'),
        'Requirements Summary'
    ),
    
    # Add more validation rules here following the same pattern...
}

def _validate_user_intent_category(data: Dict[str, Any]) -> bool:
    """Validate user intent category values."""
    valid_categories = [
        'new build', 'modernization', 'AI-enablement', 
        'integration', 'UX reimagining', 'domain-specific'
    ]
    
    node_01 = data['parsed_data']['nodes'].get('0.1')
    if not node_01 or not node_01['present']:
        return False
    
    content = node_01['content'].lower() if node_01['content'] else ''
    return any(category in content for category in valid_categories)

def _validate_percentage_sum(data: Dict[str, Any], node_id: str) -> bool:
    """Validate that percentages in a node sum to 100%."""
    from utils.helpers import extract_percentages, validate_percentage_sum
    
    node = data['parsed_data']['nodes'].get(node_id)
    if not node or not node['present']:
        return False
    
    content = node['content'] if node['content'] else ''
    percentages = extract_percentages(content)
    
    if not percentages:
        return True  # No percentages found, assume valid
    
    return validate_percentage_sum(percentages)

def get_validation_rules_by_category() -> Dict[str, List[ValidationRule]]:
    """Group validation rules by category."""
    categories = {}
    for rule in VALIDATION_RULES.values():
        if rule.category not in categories:
            categories[rule.category] = []
        categories[rule.category].append(rule)
    return categories

def get_validation_rules_by_severity() -> Dict[str, List[ValidationRule]]:
    """Group validation rules by severity."""
    severities = {}
    for rule in VALIDATION_RULES.values():
        if rule.severity not in severities:
            severities[rule.severity] = []
        severities[rule.severity].append(rule)
    return severities