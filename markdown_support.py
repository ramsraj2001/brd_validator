import streamlit as st
import markdown
import tempfile
import os
from typing import Optional, Dict, Any

def add_markdown_support():
    """
    Add Markdown file upload support to Streamlit application
    """
    
    # Custom CSS for better markdown rendering
    st.markdown("""
    <style>
    .markdown-content {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 10px 0;
    }
    .markdown-content h1, .markdown-content h2, .markdown-content h3 {
        color: #2c3e50;
    }
    .markdown-content code {
        background-color: #e9ecef;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }
    .markdown-content pre {
        background-color: #f1f3f4;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

def upload_markdown_file() -> Optional[Dict[str, Any]]:
    """
    Create file uploader specifically for Markdown files
    
    Returns:
        Dict containing file content and metadata, or None if no file uploaded
    """
    
    # File uploader with markdown extensions
    uploaded_file = st.file_uploader(
        "Upload your BRD Markdown file",
        type=['md', 'markdown', 'txt'],  # Allow .txt as fallback
        help="Upload your Business Requirements Document in Markdown format (.md, .markdown, or .txt)"
    )
    
    if uploaded_file is not None:
        try:
            # Read file content
            content = uploaded_file.read()
            
            # Handle encoding
            if isinstance(content, bytes):
                # Try different encodings
                for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                    try:
                        decoded_content = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    st.error("Could not decode file. Please ensure it's a valid text file.")
                    return None
            else:
                decoded_content = content
            
            # File metadata
            file_info = {
                'name': uploaded_file.name,
                'size': len(decoded_content),
                'type': uploaded_file.type,
                'content': decoded_content,
                'lines': len(decoded_content.split('\n'))
            }
            
            return file_info
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None
    
    return None

def render_markdown_content(content: str, show_raw: bool = False) -> None:
    """
    Render markdown content in Streamlit
    
    Args:
        content: Markdown content string
        show_raw: Whether to show raw markdown alongside rendered version
    """
    
    if not content:
        st.warning("No content to display")
        return
    
    # Create tabs for different views
    if show_raw:
        tab1, tab2 = st.tabs(["📖 Rendered", "📝 Raw Markdown"])
    else:
        tab1 = st.container()
        tab2 = None
    
    with tab1:
        st.markdown('<div class="markdown-content">', unsafe_allow_html=True)
        
        # Convert markdown to HTML and display
        try:
            # Use markdown library for better rendering
            html_content = markdown.markdown(
                content, 
                extensions=['tables', 'fenced_code', 'toc', 'codehilite']
            )
            st.markdown(html_content, unsafe_allow_html=True)
        except:
            # Fallback to basic markdown
            st.markdown(content)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if tab2:
        with tab2:
            st.code(content, language='markdown')

def save_markdown_file(content: str, filename: str = "brd_document.md") -> str:
    """
    Save markdown content to a temporary file
    
    Args:
        content: Markdown content to save
        filename: Desired filename
        
    Returns:
        Path to saved file
    """
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def parse_markdown_sections(content: str) -> Dict[str, str]:
    """
    Parse markdown content into sections based on headers
    
    Args:
        content: Markdown content string
        
    Returns:
        Dictionary with section names as keys and content as values
    """
    
    sections = {}
    current_section = "Introduction"
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        # Check for headers (# ## ### etc.)
        if line.strip().startswith('#'):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            current_section = line.strip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections

def markdown_file_analyzer(content: str) -> Dict[str, Any]:
    """
    Analyze markdown file and extract key information
    
    Args:
        content: Markdown content string
        
    Returns:
        Analysis results dictionary
    """
    
    analysis = {
        'total_lines': len(content.split('\n')),
        'total_characters': len(content),
        'total_words': len(content.split()),
        'headers': [],
        'sections': {},
        'tables': 0,
        'code_blocks': 0,
        'links': 0
    }
    
    lines = content.split('\n')
    
    # Analyze content
    in_code_block = False
    for line in lines:
        line_stripped = line.strip()
        
        # Count headers
        if line_stripped.startswith('#'):
            level = len(line_stripped) - len(line_stripped.lstrip('#'))
            header_text = line_stripped.lstrip('#').strip()
            analysis['headers'].append({
                'level': level,
                'text': header_text,
                'line': lines.index(line) + 1
            })
        
        # Count code blocks
        if line_stripped.startswith('```'):
            if in_code_block:
                analysis['code_blocks'] += 1
            in_code_block = not in_code_block
        
        # Count tables (simple detection)
        if '|' in line_stripped and line_stripped.count('|') >= 2:
            analysis['tables'] += 1
        
        # Count links
        analysis['links'] += line.count('](')
    
    # Parse sections
    analysis['sections'] = parse_markdown_sections(content)
    
    return analysis

# Example Streamlit app integration
def main_app():
    """
    Example integration of markdown support in Streamlit app
    """
    
    st.title("BRD Markdown File Processor")
    st.markdown("Upload and process your Business Requirements Document in Markdown format")
    
    # Add markdown support
    add_markdown_support()
    
    # Sidebar for options
    with st.sidebar:
        st.header("Options")
        show_raw = st.checkbox("Show raw markdown", value=False)
        show_analysis = st.checkbox("Show file analysis", value=True)
        auto_process = st.checkbox("Auto-process for validation", value=True)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📄 File Upload")
        
        # Upload markdown file
        file_info = upload_markdown_file()
        
        if file_info:
            # Display file info
            st.success(f"✅ Uploaded: {file_info['name']}")
            
            with st.expander("📊 File Information"):
                st.write(f"**Size:** {file_info['size']:,} characters")
                st.write(f"**Lines:** {file_info['lines']:,}")
                st.write(f"**Type:** {file_info['type']}")
            
            # Render content
            st.header("📖 Document Content")
            render_markdown_content(file_info['content'], show_raw)
            
            # Process for validation if enabled
            if auto_process:
                st.header("🔍 Processing for Validation")
                
                with st.spinner("Analyzing document structure..."):
                    # Here you would integrate with your BRD validation system
                    sections = parse_markdown_sections(file_info['content'])
                    
                    st.success(f"Found {len(sections)} sections")
                    
                    # Show sections
                    with st.expander("📋 Document Sections"):
                        for section_name, section_content in sections.items():
                            st.write(f"**{section_name}** ({len(section_content)} chars)")
    
    with col2:
        if file_info and show_analysis:
            st.header("📈 Analysis")
            
            analysis = markdown_file_analyzer(file_info['content'])
            
            # Display metrics
            st.metric("Total Words", f"{analysis['total_words']:,}")
            st.metric("Total Lines", f"{analysis['total_lines']:,}")
            st.metric("Headers", len(analysis['headers']))
            st.metric("Sections", len(analysis['sections']))
            
            # Show header structure
            if analysis['headers']:
                st.subheader("Document Structure")
                for header in analysis['headers'][:10]:  # Show first 10 headers
                    indent = "  " * (header['level'] - 1)
                    st.text(f"{indent}{'#' * header['level']} {header['text']}")
            
            # Download processed file
            if st.button("💾 Download Processed"):
                # Save to temporary file
                temp_path = save_markdown_file(file_info['content'], f"processed_{file_info['name']}")
                if temp_path:
                    with open(temp_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download File",
                            data=f.read(),
                            file_name=f"processed_{file_info['name']}",
                            mime="text/markdown"
                        )

# Integration functions for your existing BRD system
def integrate_with_brd_validation(markdown_content: str) -> Dict[str, Any]:
    """
    Integration function to connect markdown upload with your BRD validation system
    
    Args:
        markdown_content: The uploaded markdown content
        
    Returns:
        Validation results
    """
    
    # Parse sections
    sections = parse_markdown_sections(markdown_content)
    
    # Extract BRD components (you would customize this based on your BRD structure)
    brd_components = {
        'roles': sections.get('Roles', ''),
        'entities': sections.get('Entities', ''),
        'local_objectives': sections.get('Local Objectives', ''),
        'global_objectives': sections.get('Global Objectives', ''),
        'business_rules': sections.get('Business Rules', ''),
        'workflows': sections.get('Workflows', '')
    }
    
    # Here you would call your existing BRD validation functions
    # validation_results = your_brd_validator.validate_all(brd_components)
    
    return {
        'success': True,
        'components_found': len([v for v in brd_components.values() if v]),
        'total_sections': len(sections),
        'brd_components': brd_components,
        'message': 'Markdown file successfully processed for BRD validation'
    }

if __name__ == "__main__":
    main_app()