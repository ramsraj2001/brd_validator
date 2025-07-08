"""General helper functions and utilities."""

import re
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime

def extract_section_content(text: str, section_pattern: str) -> Optional[str]:
    """Extract content for a specific section using regex pattern."""
    pattern = re.compile(section_pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(1).strip() if match else None

def find_node_content(text: str, node_id: str) -> Optional[str]:
    """Find content for a specific node ID in the document."""
    # Pattern to match node sections like "0.1", "1.2", etc.
    pattern = rf"{re.escape(node_id)}[.\s]*(.*?)(?=\d+\.\d+|$)"
    match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None

def validate_node_numbering(text: str) -> List[str]:
    """Validate node numbering sequence."""
    errors = []
    node_pattern = r"(\d+\.\d+)"
    nodes = re.findall(node_pattern, text)
    
    expected_sequences = {
        0: ['0.1', '0.2', '0.3'],
        1: ['1.1', '1.2', '1.3', '1.4'],
        2: ['2.1', '2.2', '2.3', '2.4'],
        3: ['3.1', '3.2', '3.3', '3.4'],
        4: ['4.1', '4.2', '4.3', '4.4'],
        5: ['5.1', '5.2', '5.3']
    }
    
    for section, expected_nodes in expected_sequences.items():
        section_nodes = [n for n in nodes if n.startswith(f"{section}.")]
        for expected_node in expected_nodes:
            if expected_node not in section_nodes:
                errors.append(f"Missing node: {expected_node}")
    
    return errors

def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split()) if text else 0

def count_characters(text: str) -> int:
    """Count characters in text."""
    return len(text) if text else 0

def has_placeholder_text(text: str) -> bool:
    """Check if text contains placeholder content."""
    placeholders = ['tbd', 'todo', 'placeholder', 'coming soon', 'fill in', 'xxx']
    text_lower = text.lower() if text else ''
    return any(placeholder in text_lower for placeholder in placeholders)

def extract_percentages(text: str) -> List[float]:
    """Extract percentage values from text."""
    pattern = r"(\d+(?:\.\d+)?)\s*%"
    matches = re.findall(pattern, text)
    return [float(match) for match in matches]

def validate_percentage_sum(percentages: List[float], tolerance: float = 0.1) -> bool:
    """Validate that percentages sum to approximately 100%."""
    total = sum(percentages)
    return abs(total - 100.0) <= tolerance

def format_validation_message(rule_id: str, message: str, severity: str) -> str:
    """Format validation message with consistent structure."""
    return f"[{rule_id}] {message} (Severity: {severity})"

def get_current_timestamp() -> str:
    """Get current timestamp in formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class TextAnalyzer:
    """Analyze text content for various validation criteria."""
    
    @staticmethod
    def extract_entities(text: str) -> List[str]:
        """Extract potential entity names from text."""
        # Look for capitalized words that might be entities
        pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"
        entities = re.findall(pattern, text)
        return list(set(entities))  # Remove duplicates
    
    @staticmethod
    def extract_roles(text: str) -> List[str]:
        """Extract role mentions from text."""
        role_patterns = [
            r"(?:role|position|title):\s*([^,\n]+)",
            r"\b([A-Z][a-z]+\s+(?:Manager|Director|Analyst|Coordinator|Administrator))\b"
        ]
        roles = []
        for pattern in role_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            roles.extend(matches)
        return list(set(roles))
    
    @staticmethod
    def extract_processes(text: str) -> List[str]:
        """Extract process mentions from text."""
        process_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+Process)\b"
        processes = re.findall(process_pattern, text)
        return list(set(processes))
    
    @staticmethod
    def check_authority_structure(text: str) -> Dict[str, Any]:
        """Analyze authority structure mentions in text."""
        hierarchy_keywords = ['reports to', 'manages', 'supervises', 'authority', 'approval']
        found_keywords = []
        
        for keyword in hierarchy_keywords:
            if keyword.lower() in text.lower():
                found_keywords.append(keyword)
        
        return {
            'has_hierarchy_info': len(found_keywords) > 0,
            'found_keywords': found_keywords,
            'keyword_count': len(found_keywords)
        }