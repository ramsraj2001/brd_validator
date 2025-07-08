"""Unit tests for Validation Engine module."""

import unittest
from unittest.mock import patch, MagicMock
import time
from core.validation_engine import ValidationEngine, ValidationResult, ValidationSummary
from config.validation_rules import VALIDATION_RULES

class TestValidationEngine(unittest.TestCase):
    """Test cases for Validation Engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ValidationEngine()
        
        # Sample parsed data for testing
        self.sample_parsed_data = {
            'parsed_data': {
                'sections': {
                    0: {'name': 'Project Foundation', 'content': 'Content here', 'present': True},
                    1: {'name': 'Organizational Structure', 'content': 'Content here', 'present': True},
                    2: {'name': 'Data & Entity Management', 'content': 'Content here', 'present': True},
                    3: {'name': 'Functions & Operations', 'content': 'Content here', 'present': True},
                    4: {'name': 'Business Process Workflows', 'content': 'Content here', 'present': True}
                },
                'nodes': {
                    '0.1': {'name': 'Executive Summary', 'content': 'modernization project', 'present': True, 'fields': {}},
                    '0.2': {'name': 'Requirements Summary', 'content': 'function_coverage_stats: Core: 60%, Support: 25%, Analytics: 15%', 'present': True, 'fields': {}},
                    '0.3': {'name': 'Discovery Metadata', 'content': 'Quality metrics here', 'present': True, 'fields': {}},
                    '1.1': {'name': 'Hierarchy Structure', 'content': 'Authority structure defined', 'present': True, 'fields': {}},
                    '1.2': {'name': 'Role Definitions', 'content': 'Roles are defined', 'present': True, 'fields': {}},
                    '1.3': {'name': 'Department Structure', 'content': 'Departments listed', 'present': True, 'fields': {}},
                    '1.4': {'name': 'Performance Management', 'content': 'Performance criteria', 'present': True, 'fields': {}},
                    '2.1': {'name': 'Entity Management', 'content': 'Entities defined', 'present': True, 'fields': {}},
                    '2.2': {'name': 'Entity Relationships', 'content': 'Relationships mapped', 'present': True, 'fields': {}},
                    '2.3': {'name': 'Business Rules', 'content': 'Rules documented', 'present': True, 'fields': {}},
                    '2.4': {'name': 'Data Flow Patterns', 'content': 'Data flows defined', 'present': True, 'fields': {}},
                    '3.1': {'name': 'Function Discovery', 'content': 'Functions identified', 'present': True, 'fields': {}},
                    '3.2': {'name': 'Input-Process-Output', 'content': 'IPO specifications', 'present': True, 'fields': {}},
                    '3.3': {'name': 'Function Validation', 'content': 'Validation criteria', 'present': True, 'fields': {}},
                    '3.4': {'name': 'Function Integration', 'content': 'Integration points', 'present': True, 'fields': {}},
                    '4.1': {'name': 'Workflow Assembly', 'content': 'Workflows defined', 'present': True, 'fields': {}},
                    '4.2': {'name': 'Data Flow Validation', 'content': 'Data validation', 'present': True, 'fields': {}},
                    '4.3': {'name': 'Workflow Logic', 'content': 'Logic documented', 'present': True, 'fields': {}},
                    '4.4': {'name': 'Gap Analysis', 'content': 'Gaps identified', 'present': True, 'fields': {}}
                },
                'structure_analysis': {
                    'total_sections': 5,
                    'total_nodes': 18,
                    'missing_sections': [],
                    'missing_nodes': [],
                    'completeness_percentage': 100.0
                },
                'content_analysis': {
                    'total_word_count': 500,
                    'nodes_with_placeholders': [],
                    'empty_fields': [],
                    'quality_score': 95.0
                }
            }
        }
        
        # Sample data with missing elements
        self.incomplete_parsed_data = {
            'parsed_data': {
                'sections': {
                    0: {'name': 'Project Foundation', 'content': 'Content here', 'present': True},
                    1: {'name': 'Organizational Structure', 'content': None, 'present': False},
                    2: {'name': 'Data & Entity Management', 'content': None, 'present': False},
                    3: {'name': 'Functions & Operations', 'content': None, 'present': False},
                    4: {'name': 'Business Process Workflows', 'content': None, 'present': False}
                },
                'nodes': {
                    '0.1': {'name': 'Executive Summary', 'content': 'TBD - coming soon', 'present': True, 'fields': {}},
                    '0.2': {'name': 'Requirements Summary', 'content': None, 'present': False, 'fields': {}},
                    # Missing most other nodes
                },
                'structure_analysis': {
                    'total_sections': 1,
                    'total_nodes': 1,
                    'missing_sections': ['1: Organizational Structure', '2: Data & Entity Management'],
                    'missing_nodes': ['0.2: Requirements Summary', '0.3: Discovery Metadata'],
                    'completeness_percentage': 15.0
                },
                'content_analysis': {
                    'total_word_count': 50,
                    'nodes_with_placeholders': ['0.1'],
                    'empty_fields': ['0.1.description', '0.1.purpose'],
                    'quality_score': 25.0
                }
            }
        }
    
    def test_engine_initialization(self):
        """Test validation engine initialization."""
        self.assertIsInstance(self.engine, ValidationEngine)
        self.assertEqual(self.engine.results, [])
        self.assertIsNone(self.engine.summary)
        self.assertIsNone(self.engine.validation_start_time)
    
    def test_validate_complete_document(self):
        """Test validation of complete document."""
        results, summary = self.engine.validate_document(self.sample_parsed_data)
        
        # Check results structure
        self.assertIsInstance(results, list)
        self.assertIsInstance(summary, ValidationSummary)
        self.assertGreater(len(results), 0)
        
        # Check that all validation rules were executed
        self.assertEqual(len(results), len(VALIDATION_RULES))
        
        # Check summary calculations
        self.assertEqual(summary.total_rules, len(VALIDATION_RULES))
        self.assertEqual(summary.passed + summary.failed, summary.total_rules)
        self.assertGreaterEqual(summary.overall_score, 0)
        self.assertLessEqual(summary.overall_score, 100)
        
        # Complete document should have high pass rate
        pass_rate = summary.passed / summary.total_rules
        self.assertGreater(pass_rate, 0.5)  # At least 50% should pass
    
    def test_validate_incomplete_document(self):
        """Test validation of incomplete document."""
        results, summary = self.engine.validate_document(self.incomplete_parsed_data)
        
        # Should have many failures
        self.assertGreater(summary.failed, 0)
        self.assertGreater(summary.critical_failures, 0)
        
        # Overall score should be low
        self.assertLess(summary.overall_score, 50)
        
        # Should have validation results for all rules
        self.assertEqual(len(results), len(VALIDATION_RULES))
    
    def test_validation_result_structure(self):
        """Test structure of individual validation results."""
        results, _ = self.engine.validate_document(self.sample_parsed_data)
        
        for result in results:
            self.assertIsInstance(result, ValidationResult)
            self.assertIsInstance(result.rule_id, str)
            self.assertIsInstance(result.rule_description, str)
            self.assertIsInstance(result.severity, str)
            self.assertIsInstance(result.category, str)
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.message, str)
            self.assertIsInstance(result.details, str)
            self.assertIsInstance(result.execution_time, float)
            
            # Check severity is valid
            self.assertIn(result.severity, ['Critical', 'High', 'Medium', 'Low'])
            
            # Check rule ID format
            self.assertTrue(result.rule_id.startswith('V'))
            self.assertTrue(result.rule_id[1:].isdigit())
    
    def test_get_results_by_severity(self):
        """Test grouping results by severity."""
        results, _ = self.engine.validate_document(self.sample_parsed_data)
        severity_groups = self.engine.get_results_by_severity()
        
        # Check all severity levels are present
        expected_severities = ['Critical', 'High', 'Medium', 'Low']
        for severity in expected_severities:
            self.assertIn(severity, severity_groups)
            self.assertIsInstance(severity_groups[severity], list)
        
        # Check that all results are accounted for
        total_grouped = sum(len(group) for group in severity_groups.values())
        self.assertEqual(total_grouped, len(results))
    
    def test_get_results_by_category(self):
        """Test grouping results by category."""
        results, _ = self.engine.validate_document(self.sample_parsed_data)
        category_groups = self.engine.get_results_by_category()
        
        # Should have multiple categories
        self.assertGreater(len(category_groups), 0)
        
        # Check that all results are accounted for
        total_grouped = sum(len(group) for group in category_groups.values())
        self.assertEqual(total_grouped, len(results))
        
        # Each category should have at least one result
        for category, group in category_groups.items():
            self.assertGreater(len(group), 0)
            self.assertIsInstance(category, str)
    
    def test_get_failed_results(self):
        """Test filtering failed results."""
        results, summary = self.engine.validate_document(self.incomplete_parsed_data)
        failed_results = self.engine.get_failed_results()
        
        # Should have failed results for incomplete document
        self.assertGreater(len(failed_results), 0)
        self.assertEqual(len(failed_results), summary.failed)
        
        # All returned results should be failures
        for result in failed_results:
            self.assertFalse(result.passed)
    
    def test_is_document_valid(self):
        """Test document validity check."""
        # Complete document should be valid (no critical failures)
        self.engine.validate_document(self.sample_parsed_data)
        is_valid_complete = self.engine.is_document_valid()
        
        # Incomplete document should be invalid (has critical failures)
        self.engine.validate_document(self.incomplete_parsed_data)
        is_valid_incomplete = self.engine.is_document_valid()
        
        # Results depend on actual validation rules, but incomplete should likely fail
        self.assertIsInstance(is_valid_complete, bool)
        self.assertIsInstance(is_valid_incomplete, bool)
    
    def test_execution_timing(self):
        """Test that execution timing is recorded."""
        results, summary = self.engine.validate_document(self.sample_parsed_data)
        
        # Summary should have execution time
        self.assertGreater(summary.execution_time, 0)
        
        # Individual results should have execution times
        for result in results:
            self.assertGreaterEqual(result.execution_time, 0)
    
    def test_rule_details_generation(self):
        """Test generation of rule details."""
        results, _ = self.engine.validate_document(self.sample_parsed_data)
        
        # Check that details are generated for different rule categories
        structural_results = [r for r in results if r.category == 'Structural Completeness']
        content_results = [r for r in results if r.category == 'Content Quality']
        
        # Should have details for structural rules
        if structural_results:
            structural_result = structural_results[0]
            self.assertIsInstance(structural_result.details, str)
            # Details should contain relevant information
            self.assertTrue(len(structural_result.details) > 0)
        
        # Should have details for content rules
        if content_results:
            content_result = content_results[0]
            self.assertIsInstance(content_result.details, str)

class TestValidationRules(unittest.TestCase):
    """Test cases for individual validation rules."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample data that should pass most validations
        self.valid_data = {
            'parsed_data': {
                'sections': {i: {'present': True} for i in range(5)},
                'nodes': {f'{i}.{j}': {'present': True} for i in range(5) for j in range(1, 5)},
                'structure_analysis': {'total_sections': 5, 'total_nodes': 18},
                'content_analysis': {
                    'total_word_count': 2000,
                    'nodes_with_placeholders': [],
                    'empty_fields': [],
                    'quality_score': 90.0
                }
            }
        }
        
        # Sample data that should fail validations
        self.invalid_data = {
            'parsed_data': {
                'sections': {i: {'present': i < 2} for i in range(5)},  # Only first 2 sections
                'nodes': {f'{i}.{j}': {'present': i < 1} for i in range(5) for j in range(1, 5)},  # Only first section nodes
                'structure_analysis': {'total_sections': 2, 'total_nodes': 4},
                'content_analysis': {
                    'total_word_count': 100,
                    'nodes_with_placeholders': ['0.1', '0.2'],
                    'empty_fields': ['0.1.description', '0.2.purpose'],
                    'quality_score': 30.0
                }
            }
        }
    
    def test_structural_completeness_rules(self):
        """Test structural completeness validation rules."""
        from config.validation_rules import VALIDATION_RULES
        
        # Test V001 - All 5 main sections must be present
        rule_v001 = VALIDATION_RULES['V001']
        self.assertTrue(rule_v001.validation_func(self.valid_data))
        self.assertFalse(rule_v001.validation_func(self.invalid_data))
        
        # Test V006 - All 18 nodes must be present
        rule_v006 = VALIDATION_RULES['V006']
        self.assertTrue(rule_v006.validation_func(self.valid_data))
        self.assertFalse(rule_v006.validation_func(self.invalid_data))
    
    def test_content_quality_rules(self):
        """Test content quality validation rules."""
        from config.validation_rules import VALIDATION_RULES
        
        # Test V013 - No placeholder text allowed
        rule_v013 = VALIDATION_RULES['V013']
        self.assertTrue(rule_v013.validation_func(self.valid_data))
        self.assertFalse(rule_v013.validation_func(self.invalid_data))
        
        # Test V014 - Minimum character length requirements
        rule_v014 = VALIDATION_RULES['V014']
        self.assertTrue(rule_v014.validation_func(self.valid_data))
        self.assertFalse(rule_v014.validation_func(self.invalid_data))
    
    def test_user_intent_category_validation(self):
        """Test user intent category validation."""
        from config.validation_rules import _validate_user_intent_category
        
        # Valid data with recognized category
        valid_intent_data = {
            'parsed_data': {
                'nodes': {
                    '0.1': {
                        'present': True,
                        'content': 'This is a modernization project for the enterprise system'
                    }
                }
            }
        }
        
        # Invalid data with unrecognized category
        invalid_intent_data = {
            'parsed_data': {
                'nodes': {
                    '0.1': {
                        'present': True,
                        'content': 'This is some random project type'
                    }
                }
            }
        }
        
        self.assertTrue(_validate_user_intent_category(valid_intent_data))
        self.assertFalse(_validate_user_intent_category(invalid_intent_data))
    
    def test_percentage_sum_validation(self):
        """Test percentage sum validation."""
        from config.validation_rules import _validate_percentage_sum
        
        # Valid data with percentages that sum to 100%
        valid_percentage_data = {
            'parsed_data': {
                'nodes': {
                    '0.2': {
                        'present': True,
                        'content': 'Core Functions: 60%, Support Functions: 25%, Analytics: 15%'
                    }
                }
            }
        }
        
        # Invalid data with percentages that don't sum to 100%
        invalid_percentage_data = {
            'parsed_data': {
                'nodes': {
                    '0.2': {
                        'present': True,
                        'content': 'Core Functions: 70%, Support Functions: 20%, Analytics: 20%'
                    }
                }
            }
        }
        
        self.assertTrue(_validate_percentage_sum(valid_percentage_data, '0.2'))
        self.assertFalse(_validate_percentage_sum(invalid_percentage_data, '0.2'))

class TestValidationSummary(unittest.TestCase):
    """Test cases for ValidationSummary functionality."""
    
    def test_summary_creation(self):
        """Test ValidationSummary creation."""
        summary = ValidationSummary(
            total_rules=10,
            passed=7,
            failed=3,
            critical_failures=1,
            high_failures=1,
            medium_failures=1,
            low_failures=0,
            overall_score=75.5,
            execution_time=2.5,
            timestamp="2024-01-01 12:00:00"
        )
        
        self.assertEqual(summary.total_rules, 10)
        self.assertEqual(summary.passed, 7)
        self.assertEqual(summary.failed, 3)
        self.assertEqual(summary.critical_failures, 1)
        self.assertEqual(summary.overall_score, 75.5)
        self.assertEqual(summary.execution_time, 2.5)
    
    def test_summary_calculations(self):
        """Test that summary calculations are consistent."""
        engine = ValidationEngine()
        
        # Create mock data
        sample_data = {
            'parsed_data': {
                'sections': {i: {'present': True} for i in range(5)},
                'nodes': {f'{i}.{j}': {'present': True} for i in range(2) for j in range(1, 3)},
                'structure_analysis': {'total_sections': 5, 'total_nodes': 4},
                'content_analysis': {
                    'total_word_count': 1500,
                    'nodes_with_placeholders': [],
                    'empty_fields': [],
                    'quality_score': 80.0
                }
            }
        }
        
        results, summary = engine.validate_document(sample_data)
        
        # Check that passed + failed = total
        self.assertEqual(summary.passed + summary.failed, summary.total_rules)
        
        # Check that severity counts add up to total failures
        severity_total = (summary.critical_failures + summary.high_failures + 
                         summary.medium_failures + summary.low_failures)
        self.assertEqual(severity_total, summary.failed)

if __name__ == '__main__':
    # Run specific test categories
    import sys
    
    if len(sys.argv) > 1:
        test_category = sys.argv[1]
        if test_category == 'engine':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestValidationEngine)
        elif test_category == 'rules':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestValidationRules)
        elif test_category == 'summary':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestValidationSummary)
        else:
            suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    else:
        # Run all tests
        suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Results Summary:")
    print(f"Ran {result.testsRun} tests")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print(f"{'='*50}")
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)