"""BRD document parser and content extractor."""

import re
from typing import Dict, List, Any, Optional
from utils.helpers import (
    extract_section_content, find_node_content, validate_node_numbering,
    count_words, has_placeholder_text, TextAnalyzer
)
from config.settings import BRD_SECTIONS, BRD_NODES

class BRDParser:
    """Parse and extract structured information from BRD documents."""
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        self.parsed_data = {}
        self.parsing_errors = []
    
    def parse_document(self, content: str, is_structured: bool = False) -> Dict[str, Any]:
        """Main parsing method for BRD documents."""
        self.parsed_data = {
            'sections': {},
            'nodes': {},
            'metadata': {},
            'structure_analysis': {},
            'content_analysis': {}
        }
        self.parsing_errors = []
        
        try:
            if is_structured:
                # If content is JSON/structured data
                self._parse_structured_content(content)
            else:
                # If content is plain text
                self._parse_text_content(content)
            
            # Perform additional analysis
            self._analyze_document_structure()
            self._analyze_content_quality()
            
        except Exception as e:
            self.parsing_errors.append(f"Parsing error: {str(e)}")
        
        return {
            'parsed_data': self.parsed_data,
            'parsing_errors': self.parsing_errors
        }
    
    def _parse_structured_content(self, content: Any):
        """Parse structured JSON content."""
        try:
            import json
            if isinstance(content, str):
                data = json.loads(content)
            else:
                data = content
            
            # Extract sections and nodes from structured data
            for section_id, section_name in BRD_SECTIONS.items():
                section_key = f"section_{section_id}"
                if section_key in data:
                    self.parsed_data['sections'][section_id] = {
                        'name': section_name,
                        'content': data[section_key],
                        'present': True
                    }
                else:
                    self.parsed_data['sections'][section_id] = {
                        'name': section_name,
                        'content': None,
                        'present': False
                    }
            
            # Extract nodes
            for node_id, node_name in BRD_NODES.items():
                node_key = f"node_{node_id.replace('.', '_')}"
                if node_key in data:
                    self.parsed_data['nodes'][node_id] = {
                        'name': node_name,
                        'content': data[node_key],
                        'present': True,
                        'fields': self._extract_node_fields(data[node_key])
                    }
                else:
                    self.parsed_data['nodes'][node_id] = {
                        'name': node_name,
                        'content': None,
                        'present': False,
                        'fields': {}
                    }
            
        except Exception as e:
            self.parsing_errors.append(f"Structured content parsing error: {str(e)}")
    
    def _parse_text_content(self, text: str):
        """Parse plain text content."""
        # Extract sections
        for section_id, section_name in BRD_SECTIONS.items():
            section_patterns = [
                rf"(?:section\s+{section_id}|{re.escape(section_name)})[:\s]+(.*?)(?=section\s+\d+|\Z)",
                rf"{section_id}[.\s]+{re.escape(section_name)}[:\s]+(.*?)(?=\d+[.\s]+\w+|\Z)"
            ]
            
            section_content = None
            for pattern in section_patterns:
                section_content = extract_section_content(text, pattern)
                if section_content:
                    break
            
            self.parsed_data['sections'][section_id] = {
                'name': section_name,
                'content': section_content,
                'present': section_content is not None
            }
        
        # Extract nodes
        for node_id, node_name in BRD_NODES.items():
            node_content = find_node_content(text, node_id)
            
            self.parsed_data['nodes'][node_id] = {
                'name': node_name,
                'content': node_content,
                'present': node_content is not None,
                'fields': self._extract_node_fields_from_text(node_content) if node_content else {}
            }
    
    def _extract_node_fields(self, node_data: Any) -> Dict[str, Any]:
        """Extract fields from structured node data."""
        fields = {}
        if isinstance(node_data, dict):
            for key, value in node_data.items():
                fields[key] = {
                    'content': value,
                    'description': value.get('description', '') if isinstance(value, dict) else str(value),
                    'purpose': value.get('purpose', '') if isinstance(value, dict) else '',
                    'present': True,
                    'has_placeholder': has_placeholder_text(str(value))
                }
        return fields
    
    def _extract_node_fields_from_text(self, text: str) -> Dict[str, Any]:
        """Extract fields from text-based node content."""
        fields = {}
        
        # Common field patterns in BRD documents
        field_patterns = {
            'description': r"description[:\s]+(.*?)(?=purpose|$)",
            'purpose': r"purpose[:\s]+(.*?)(?=description|$)",
            'requirements': r"requirements?[:\s]+(.*?)(?=\w+:|$)",
            'scope': r"scope[:\s]+(.*?)(?=\w+:|$)",
            'objectives': r"objectives?[:\s]+(.*?)(?=\w+:|$)",
            'stakeholders': r"stakeholders?[:\s]+(.*?)(?=\w+:|$)",
            'metrics': r"metrics?[:\s]+(.*?)(?=\w+:|$)",
            'kpis': r"kpis?[:\s]+(.*?)(?=\w+:|$)"
        }
        
        for field_name, pattern in field_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                fields[field_name] = {
                    'content': content,
                    'description': content,
                    'purpose': '',
                    'present': True,
                    'has_placeholder': has_placeholder_text(content)
                }
        
        return fields
    
    def _analyze_document_structure(self):
        """Analyze overall document structure."""
        structure_analysis = {
            'total_sections': len([s for s in self.parsed_data['sections'].values() if s['present']]),
            'total_nodes': len([n for n in self.parsed_data['nodes'].values() if n['present']]),
            'missing_sections': [
                f"{sid}: {sdata['name']}" 
                for sid, sdata in self.parsed_data['sections'].items() 
                if not sdata['present']
            ],
            'missing_nodes': [
                f"{nid}: {ndata['name']}" 
                for nid, ndata in self.parsed_data['nodes'].items() 
                if not ndata['present']
            ],
            'completeness_percentage': self._calculate_completeness()
        }
        
        self.parsed_data['structure_analysis'] = structure_analysis
    
    def _analyze_content_quality(self):
        """Analyze content quality metrics."""
        content_analysis = {
            'total_word_count': 0,
            'nodes_with_placeholders': [],
            'empty_fields': [],
            'quality_score': 0
        }
        
        for node_id, node_data in self.parsed_data['nodes'].items():
            if node_data['present'] and node_data['content']:
                # Count words
                word_count = count_words(node_data['content'])
                content_analysis['total_word_count'] += word_count
                
                # Check for placeholders
                if has_placeholder_text(node_data['content']):
                    content_analysis['nodes_with_placeholders'].append(node_id)
                
                # Check for empty fields
                for field_name, field_data in node_data['fields'].items():
                    if not field_data['content'] or field_data['content'].strip() == '':
                        content_analysis['empty_fields'].append(f"{node_id}.{field_name}")
        
        # Calculate quality score
        total_possible_nodes = len(BRD_NODES)
        present_nodes = len([n for n in self.parsed_data['nodes'].values() if n['present']])
        placeholder_penalty = len(content_analysis['nodes_with_placeholders']) * 5
        empty_field_penalty = len(content_analysis['empty_fields']) * 2
        
        quality_score = max(0, 100 * (present_nodes / total_possible_nodes) - placeholder_penalty - empty_field_penalty)
        content_analysis['quality_score'] = round(quality_score, 1)
        
        self.parsed_data['content_analysis'] = content_analysis
    
    def _calculate_completeness(self) -> float:
        """Calculate document completeness percentage."""
        total_sections = len(BRD_SECTIONS)
        total_nodes = len(BRD_NODES)
        
        present_sections = len([s for s in self.parsed_data['sections'].values() if s['present']])
        present_nodes = len([n for n in self.parsed_data['nodes'].values() if n['present']])
        
        section_weight = 0.3
        node_weight = 0.7
        
        completeness = (
            (present_sections / total_sections) * section_weight +
            (present_nodes / total_nodes) * node_weight
        ) * 100
        
        return round(completeness, 1)
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of extraction results."""
        return {
            'total_sections_found': len([s for s in self.parsed_data['sections'].values() if s['present']]),
            'total_nodes_found': len([n for n in self.parsed_data['nodes'].values() if n['present']]),
            'completeness_percentage': self.parsed_data['structure_analysis']['completeness_percentage'],
            'quality_score': self.parsed_data['content_analysis']['quality_score'],
            'parsing_errors': self.parsing_errors
        }