"""Unit tests for BRD Parser module."""

import unittest
import json
from unittest.mock import patch, mock_open
from core.brd_parser import BRDParser
from config.settings import BRD_SECTIONS, BRD_NODES

class TestBRDParser(unittest.TestCase):
    """Test cases for BRD Parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = BRDParser()
        
        # Sample text content for testing
        self.sample_text = """
        Section 0: Project Foundation
        0.1 Executive Summary & Business Case
        This is the executive summary with user_intent_category: modernization
        solution_scope_and_scale: Enterprise-wide system modernization
        industry_and_solution_type: Financial Services
        
        0.2 Requirements Summary Dashboard
        function_coverage_stats: Core Functions: 60%, Support Functions: 25%, Analytics: 15%
        process_and_entity_summary: 25 processes identified
        
        Section 1: Organizational Structure
        1.1 Hierarchy & Authority Structure
        The organization has a clear hierarchy with reports to relationships.
        Authority levels are defined for approval processes.
        
        1.2 Role Definitions
        Role: Project Manager
        Role: Business Analyst
        Position: System Administrator
        """
        
        # Sample structured JSON content
        self.sample_json = {
            "section_0": {
                "node_0_1": {
                    "user_intent_category": "modernization",
                    "solution_scope_and_scale": "Enterprise-wide system modernization",
                    "industry_and_solution_type": "Financial Services - Core Banking"
                },
                "node_0_2": {
                    "function_coverage_stats": "Core Functions: 60%, Support Functions: 25%, Analytics: 15%",
                    "process_and_entity_summary": "25 processes, 150 entities identified"
                }
            },
            "section_1": {
                "node_1_1": {
                    "hierarchy_structure": "CEO -> CTO -> Development Manager -> Developers",
                    "authority_levels": "Level 1: Executive, Level 2: Management, Level 3: Team Lead"
                }
            }
        }
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        self.assertIsInstance(self.parser, BRDParser)
        self.assertEqual(self.parser.parsed_data, {})
        self.assertEqual(self.parser.parsing_errors, [])
    
    def test_parse_text_content(self):
        """Test parsing of plain text content."""
        result = self.parser.parse_document(self.sample_text, is_structured=False)
        
        # Check that parsing returned expected structure
        self.assertIn('parsed_data', result)
        self.assertIn('parsing_errors', result)
        
        parsed_data = result['parsed_data']
        
        # Check sections are parsed
        self.assertIn('sections', parsed_data)
        self.assertIn('nodes', parsed_data)
        
        # Check specific node content
        node_01 = parsed_data['nodes'].get('0.1')
        self.assertIsNotNone(node_01)
        self.assertTrue(node_01['present'])
        self.assertIn('modernization', node_01['content'].lower())
    
    def test_parse_structured_content(self):
        """Test parsing of structured JSON content."""
        json_string = json.dumps(self.sample_json)
        result = self.parser.parse_document(json_string, is_structured=True)
        
        parsed_data = result['parsed_data']
        
        # Check that structured data is properly parsed
        self.assertIn('sections', parsed_data)
        self.assertIn('nodes', parsed_data)
        
        # Check specific node
        node_01 = parsed_data['nodes'].get('0.1')
        self.assertIsNotNone(node_01)
        self.assertTrue(node_01['present'])
        
        # Check fields extraction
        self.assertIn('fields', node_01)
        fields = node_01['fields']
        self.assertIn('user_intent_category', fields)
        self.assertEqual(fields['user_intent_category']['content']['user_intent_category'], 'modernization')
    
    def test_extract_node_fields_from_text(self):
        """Test extraction of fields from text content."""
        test_text = """
        Description: This is a sample description of the business process
        Purpose: To streamline operations and improve efficiency
        Requirements: Must handle 1000+ transactions per minute
        Scope: Enterprise-wide implementation across all departments
        """
        
        fields = self.parser._extract_node_fields_from_text(test_text)
        
        # Check that fields are extracted
        self.assertIn('description', fields)
        self.assertIn('purpose', fields)
        self.assertIn('requirements', fields)
        self.assertIn('scope', fields)
        
        # Check field content
        self.assertIn('sample description', fields['description']['content'])
        self.assertIn('streamline operations', fields['purpose']['content'])
    
    def test_document_structure_analysis(self):
        """Test document structure analysis."""
        result = self.parser.parse_document(self.sample_text, is_structured=False)
        parsed_data = result['parsed_data']
        
        # Check structure analysis
        self.assertIn('structure_analysis', parsed_data)
        structure = parsed_data['structure_analysis']
        
        self.assertIn('total_sections', structure)
        self.assertIn('total_nodes', structure)
        self.assertIn('missing_sections', structure)
        self.assertIn('missing_nodes', structure)
        self.assertIn('completeness_percentage', structure)
        
        # Completeness should be calculated
        self.assertIsInstance(structure['completeness_percentage'], (int, float))
        self.assertGreaterEqual(structure['completeness_percentage'], 0)
        self.assertLessEqual(structure['completeness_percentage'], 100)
    
    def test_content_quality_analysis(self):
        """Test content quality analysis."""
        # Add placeholder text to test detection
        text_with_placeholders = self.sample_text + "\n0.3 Discovery Metadata & Quality\nTBD - Coming soon\nTODO: Fill in later"
        
        result = self.parser.parse_document(text_with_placeholders, is_structured=False)
        parsed_data = result['parsed_data']
        
        # Check content analysis
        self.assertIn('content_analysis', parsed_data)
        content = parsed_data['content_analysis']
        
        self.assertIn('total_word_count', content)
        self.assertIn('nodes_with_placeholders', content)
        self.assertIn('empty_fields', content)
        self.assertIn('quality_score', content)
        
        # Should detect placeholder text
        self.assertGreater(len(content['nodes_with_placeholders']), 0)
        
        # Quality score should be calculated
        self.assertIsInstance(content['quality_score'], (int, float))
        self.assertGreaterEqual(content['quality_score'], 0)
        self.assertLessEqual(content['quality_score'], 100)
    
    def test_completeness_calculation(self):
        """Test completeness percentage calculation."""
        # Test with empty document
        empty_result = self.parser.parse_document("", is_structured=False)
        empty_completeness = empty_result['parsed_data']['structure_analysis']['completeness_percentage']
        self.assertEqual(empty_completeness, 0.0)
        
        # Test with partial document
        partial_result = self.parser.parse_document(self.sample_text, is_structured=False)
        partial_completeness = partial_result['parsed_data']['structure_analysis']['completeness_percentage']
        self.assertGreater(partial_completeness, 0.0)
        self.assertLess(partial_completeness, 100.0)
    
    def test_error_handling(self):
        """Test error handling in parser."""
        # Test with invalid JSON
        invalid_json = "{ invalid json content"
        result = self.parser.parse_document(invalid_json, is_structured=True)
        
        # Should have parsing errors
        self.assertGreater(len(result['parsing_errors']), 0)
    
    def test_extraction_summary(self):
        """Test extraction summary generation."""
        result = self.parser.parse_document(self.sample_text, is_structured=False)
        summary = self.parser.get_extraction_summary()
        
        # Check summary structure
        self.assertIn('total_sections_found', summary)
        self.assertIn('total_nodes_found', summary)
        self.assertIn('completeness_percentage', summary)
        self.assertIn('quality_score', summary)
        self.assertIn('parsing_errors', summary)
        
        # Check that values are reasonable
        self.assertIsInstance(summary['total_sections_found'], int)
        self.assertIsInstance(summary['total_nodes_found'], int)
        self.assertGreaterEqual(summary['total_sections_found'], 0)
        self.assertGreaterEqual(summary['total_nodes_found'], 0)
    
    def test_missing_content_handling(self):
        """Test handling of missing sections and nodes."""
        minimal_text = "0.1 Executive Summary\nBasic summary content"
        result = self.parser.parse_document(minimal_text, is_structured=False)
        parsed_data = result['parsed_data']
        
        # Should have missing sections and nodes
        structure = parsed_data['structure_analysis']
        self.assertGreater(len(structure['missing_sections']), 0)
        self.assertGreater(len(structure['missing_nodes']), 0)
        
        # Check that missing items are properly formatted
        for missing_section in structure['missing_sections']:
            self.assertIn(':', missing_section)  # Should have format "id: name"
        
        for missing_node in structure['missing_nodes']:
            self.assertIn(':', missing_node)  # Should have format "id: name"

class TestTextAnalyzer(unittest.TestCase):
    """Test cases for TextAnalyzer utility class."""
    
    def setUp(self):
        """Set up test fixtures."""
        from utils.helpers import TextAnalyzer
        self.analyzer = TextAnalyzer()
    
    def test_extract_entities(self):
        """Test entity extraction."""
        text = "The Customer Management System handles Customer and Order entities."
        entities = self.analyzer.extract_entities(text)
        
        self.assertIn('Customer', entities)
        self.assertIn('Order', entities)
        self.assertIn('System', entities)
    
    def test_extract_roles(self):
        """Test role extraction."""
        text = """
        Role: Project Manager - Responsible for project oversight
        The Business Analyst will gather requirements
        Position: System Administrator
        """
        roles = self.analyzer.extract_roles(text)
        
        self.assertTrue(any('Project Manager' in role for role in roles))
        self.assertTrue(any('Business Analyst' in role for role in roles))
    
    def test_check_authority_structure(self):
        """Test authority structure analysis."""
        text = "The manager supervises the team and has approval authority. Each employee reports to their direct supervisor."
        result = self.analyzer.check_authority_structure(text)
        
        self.assertTrue(result['has_hierarchy_info'])
        self.assertGreater(result['keyword_count'], 0)
        self.assertIn('supervises', result['found_keywords'])
        self.assertIn('reports to', result['found_keywords'])

if __name__ == '__main__':
    # Run specific test categories
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'parser':
        # Run only parser tests
        suite = unittest.TestLoader().loadTestsFromTestCase(TestBRDParser)
    elif len(sys.argv) > 1 and sys.argv[1] == 'analyzer':
        # Run only analyzer tests
        suite = unittest.TestLoader().loadTestsFromTestCase(TestTextAnalyzer)
    else:
        # Run all tests
        suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)