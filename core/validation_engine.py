"""Core validation engine for BRD documents."""

import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from config.validation_rules import VALIDATION_RULES, ValidationRule
from config.settings import VALIDATION_TIMEOUT
from utils.helpers import get_current_timestamp, format_validation_message

@dataclass
class ValidationResult:
    """Individual validation result."""
    rule_id: str
    rule_description: str
    severity: str
    category: str
    passed: bool
    message: str
    details: str = ""
    execution_time: float = 0.0

@dataclass
class ValidationSummary:
    """Overall validation summary."""
    total_rules: int
    passed: int
    failed: int
    critical_failures: int
    high_failures: int
    medium_failures: int
    low_failures: int
    overall_score: float
    execution_time: float
    timestamp: str

class ValidationEngine:
    """Main validation engine for BRD documents."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.summary: ValidationSummary = None
        self.validation_start_time = None
    
    def validate_document(self, parsed_data: Dict[str, Any]) -> Tuple[List[ValidationResult], ValidationSummary]:
        """Run all validation rules against parsed document data."""
        self.validation_start_time = time.time()
        self.results = []
        
        print(f"Starting validation with {len(VALIDATION_RULES)} rules...")
        
        # Run each validation rule
        for rule_id, rule in VALIDATION_RULES.items():
            if time.time() - self.validation_start_time > VALIDATION_TIMEOUT:
                print(f"Validation timeout reached after {VALIDATION_TIMEOUT} seconds")
                break
            
            result = self._execute_validation_rule(rule, parsed_data)
            self.results.append(result)
        
        # Generate summary
        self.summary = self._generate_summary()
        
        print(f"Validation completed in {self.summary.execution_time:.2f} seconds")
        return self.results, self.summary
    
    def _execute_validation_rule(self, rule: ValidationRule, data: Dict[str, Any]) -> ValidationResult:
        """Execute a single validation rule."""
        start_time = time.time()
        
        try:
            # Execute the validation function
            passed = rule.validation_func(data)
            message = f"Rule {rule.rule_id} {'PASSED' if passed else 'FAILED'}"
            details = self._get_rule_details(rule, data, passed)
            
        except Exception as e:
            passed = False
            message = f"Rule {rule.rule_id} FAILED - Execution Error"
            details = f"Error executing validation: {str(e)}"
        
        execution_time = time.time() - start_time
        
        return ValidationResult(
            rule_id=rule.rule_id,
            rule_description=rule.description,
            severity=rule.severity,
            category=rule.category,
            passed=passed,
            message=message,
            details=details,
            execution_time=execution_time
        )
    
    def _get_rule_details(self, rule: ValidationRule, data: Dict[str, Any], passed: bool) -> str:
        """Get detailed information about rule execution."""
        details = []
        
        # Add context based on rule category
        if rule.category == "Structural Completeness":
            structure_analysis = data['parsed_data'].get('structure_analysis', {})
            details.append(f"Sections found: {structure_analysis.get('total_sections', 0)}")
            details.append(f"Nodes found: {structure_analysis.get('total_nodes', 0)}")
            
            if not passed:
                missing_sections = structure_analysis.get('missing_sections', [])
                missing_nodes = structure_analysis.get('missing_nodes', [])
                if missing_sections:
                    details.append(f"Missing sections: {', '.join(missing_sections)}")
                if missing_nodes:
                    details.append(f"Missing nodes: {', '.join(missing_nodes[:5])}...")  # Limit output
        
        elif rule.category == "Content Quality":
            content_analysis = data['parsed_data'].get('content_analysis', {})
            details.append(f"Quality score: {content_analysis.get('quality_score', 0)}%")
            details.append(f"Total words: {content_analysis.get('total_word_count', 0)}")
            
            if not passed:
                placeholders = content_analysis.get('nodes_with_placeholders', [])
                empty_fields = content_analysis.get('empty_fields', [])
                if placeholders:
                    details.append(f"Nodes with placeholders: {', '.join(placeholders[:3])}...")
                if empty_fields:
                    details.append(f"Empty fields: {', '.join(empty_fields[:3])}...")
        
        elif rule.category == "Project Foundation":
            node_01 = data['parsed_data']['nodes'].get('0.1', {})
            if node_01.get('present'):
                details.append("Executive Summary section found")
            else:
                details.append("Executive Summary section missing")
        
        return " | ".join(details) if details else "No additional details available"
    
    def _generate_summary(self) -> ValidationSummary:
        """Generate validation summary statistics."""
        total_rules = len(self.results)
        passed = len([r for r in self.results if r.passed])
        failed = total_rules - passed
        
        # Count failures by severity
        critical_failures = len([r for r in self.results if not r.passed and r.severity == 'Critical'])
        high_failures = len([r for r in self.results if not r.passed and r.severity == 'High'])
        medium_failures = len([r for r in self.results if not r.passed and r.severity == 'Medium'])
        low_failures = len([r for r in self.results if not r.passed and r.severity == 'Low'])
        
        # Calculate overall score (weighted by severity)
        severity_weights = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
        total_possible_score = sum(severity_weights[r.severity] for r in self.results)
        actual_score = sum(severity_weights[r.severity] for r in self.results if r.passed)
        overall_score = (actual_score / total_possible_score * 100) if total_possible_score > 0 else 0
        
        execution_time = time.time() - self.validation_start_time
        
        return ValidationSummary(
            total_rules=total_rules,
            passed=passed,
            failed=failed,
            critical_failures=critical_failures,
            high_failures=high_failures,
            medium_failures=medium_failures,
            low_failures=low_failures,
            overall_score=round(overall_score, 1),
            execution_time=round(execution_time, 2),
            timestamp=get_current_timestamp()
        )
    
    def get_results_by_severity(self) -> Dict[str, List[ValidationResult]]:
        """Group results by severity level."""
        severity_groups = {'Critical': [], 'High': [], 'Medium': [], 'Low': []}
        for result in self.results:
            if result.severity in severity_groups:
                severity_groups[result.severity].append(result)
        return severity_groups
    
    def get_results_by_category(self) -> Dict[str, List[ValidationResult]]:
        """Group results by validation category."""
        category_groups = {}
        for result in self.results:
            if result.category not in category_groups:
                category_groups[result.category] = []
            category_groups[result.category].append(result)
        return category_groups
    
    def get_failed_results(self) -> List[ValidationResult]:
        """Get only failed validation results."""
        return [r for r in self.results if not r.passed]
    
    def is_document_valid(self) -> bool:
        """Check if document passes all critical validations."""
        critical_failures = [r for r in self.results if not r.passed and r.severity == 'Critical']
        return len(critical_failures) == 0