"""Main Streamlit application for BRD validation."""
from markdown_support import upload_markdown_file, render_markdown_content, integrate_with_brd_validation

import streamlit as st
import pandas as pd
import time
from pathlib import Path

# Import custom modules
from utils.file_handlers import FileHandler
from core.brd_parser import BRDParser
from core.validation_engine import ValidationEngine
from core.report_generator import ReportGenerator
from config.settings import (
    APP_TITLE, APP_VERSION, APP_DESCRIPTION, 
    SEVERITY_LEVELS, MAX_ERRORS_DISPLAY
)

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
def load_custom_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    .severity-critical { border-left-color: #ff4b4b; }
    .severity-high { border-left-color: #ff8c00; }
    .severity-medium { border-left-color: #ffd700; }
    .severity-low { border-left-color: #90ee90; }
    .status-valid { color: #28a745; font-weight: bold; }
    .status-invalid { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'validation_summary' not in st.session_state:
        st.session_state.validation_summary = None
    if 'parsed_data' not in st.session_state:
        st.session_state.parsed_data = None
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False

def main():
    """Main application function."""
    load_custom_css()
    initialize_session_state()
    
    # Header
    st.markdown(f'<h1 class="main-header">{APP_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666;'>{APP_DESCRIPTION} v{APP_VERSION}</p>", 
                unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("📁 File Upload")
    st.sidebar.markdown("Upload your BRD document for validation")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Choose a BRD document",
        type=['docx', 'pdf', 'txt', 'json', 'md'],
        help="Supported formats: DOCX, PDF, TXT, JSON, MD. Limit 200MB per file."
    )
    
    # Main content area
    if uploaded_file is None:
        show_welcome_page()
    else:
        process_uploaded_file(uploaded_file)

def show_welcome_page():
    """Display welcome page with instructions."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🎯 Welcome to BRD Validator")
        st.markdown("""
        This application validates Business Requirements Documents (BRD) against a comprehensive 
        framework of 130+ validation rules.
        
        ### 📋 What we validate:
        - **Structural Completeness** - All required sections and nodes
        - **Content Quality** - Placeholder text, field completeness
        - **Business Logic** - Process flows, data consistency
        - **Integration Points** - Cross-section dependencies
        
        ### 🚀 How to get started:
        1. Upload your BRD document using the sidebar
        2. Wait for automatic parsing and validation
        3. Review detailed results and recommendations
        4. Download comprehensive validation report
        
        ### 📊 Validation Categories:
        """)
        
        # Show validation categories
        categories = [
            ("🏗️ Structural Completeness", "Document structure and organization"),
            ("📈 Project Foundation", "Executive summary and business case"),
            ("👥 Organizational Structure", "Roles, hierarchy, and authority"),
            ("📊 Data & Entity Management", "Data models and relationships"),
            ("⚙️ Functions & Operations", "Business functions and processes"),
            ("🔄 Business Process Workflows", "End-to-end process validation"),
            ("🧠 Intelligence & Analytics", "KPIs and reporting requirements")
        ]
        
        for category, description in categories:
            st.markdown(f"**{category}:** {description}")

def process_uploaded_file(uploaded_file):
    """Process the uploaded file and run validation."""
    # Initialize handlers
    file_handler = FileHandler()
    
    # Validate file
    validation_result = file_handler.validate_file(uploaded_file)
    
    if not validation_result['valid']:
        st.sidebar.error(f"❌ {validation_result['error']}")
        return
    
    # Display file info
    file_info = validation_result['file_info']
    st.sidebar.success("✅ File uploaded successfully")
    st.sidebar.markdown(f"""
    **File:** {file_info['name']}  
    **Size:** {file_info['size'] / 1024:.1f} KB  
    **Type:** {file_info['extension']}
    """)
    
    # Process file button
    if st.sidebar.button("🔍 Analyze Document", type="primary"):
        process_document(uploaded_file, file_handler)
    
    # Show results if available
    if st.session_state.validation_results:
        show_validation_results()

def process_document(uploaded_file, file_handler):
    """Process document and run validation."""
    try:
        # Save temporary file
        temp_path = file_handler.save_temp_file(uploaded_file)
        if not temp_path:
            st.error("Failed to save uploaded file")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Extract content
        status_text.text("📄 Extracting document content...")
        progress_bar.progress(20)
        
        file_extension = Path(uploaded_file.name).suffix.lower()
        content = file_handler.extract_content(temp_path, file_extension)
        
        if content['error']:
            st.error(f"Content extraction failed: {content['error']}")
            return
        
        # Step 2: Parse document
        status_text.text("🔍 Parsing document structure...")
        progress_bar.progress(40)
        
        parser = BRDParser()
        is_structured = file_extension == '.json'
        parse_result = parser.parse_document(content['text'], is_structured)
        
        if parse_result['parsing_errors']:
            st.warning(f"Parsing warnings: {', '.join(parse_result['parsing_errors'][:3])}")
        
        # Step 3: Run validation
        status_text.text("✅ Running validation rules...")
        progress_bar.progress(60)
        
        validator = ValidationEngine()
        results, summary = validator.validate_document(parse_result)
        
        # Step 4: Generate report
        status_text.text("📊 Generating validation report...")
        progress_bar.progress(80)
        
        # Store results in session state
        st.session_state.validation_results = results
        st.session_state.validation_summary = summary
        st.session_state.parsed_data = parse_result['parsed_data']
        st.session_state.file_processed = True
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Validation completed!")
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        # Cleanup
        file_handler.cleanup_temp_files()
        
        # Auto-rerun to show results
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Processing failed: {str(e)}")
        # Collect error log
        error_log = [str(e)]
        # Show download button for error log
        st.download_button(
            label="Download Error Log",
            data="\n".join(error_log),
            file_name="error_log.txt",
            mime="text/plain"
        )
        file_handler.cleanup_temp_files()

def show_validation_results():
    """Display comprehensive validation results."""
    results = st.session_state.validation_results
    summary = st.session_state.validation_summary
    
    if not results or not summary:
        return
    
    # Generate report
    report_generator = ReportGenerator(results, summary)
    
    # Summary metrics
    st.markdown("## 📊 Validation Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_class = "status-valid" if summary.critical_failures == 0 else "status-invalid"
        status_text = "VALID" if summary.critical_failures == 0 else "INVALID"
        st.markdown(f'<div class="metric-card"><h3>Document Status</h3><p class="{status_class}">{status_text}</p></div>', 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="metric-card"><h3>Overall Score</h3><p style="font-size: 2rem; font-weight: bold;">{summary.overall_score:.1f}%</p></div>', 
                   unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="metric-card"><h3>Rules Passed</h3><p style="color: #28a745; font-size: 1.5rem;">{summary.passed}/{summary.total_rules}</p></div>', 
                   unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="metric-card"><h3>Critical Issues</h3><p style="color: #dc3545; font-size: 1.5rem;">{summary.critical_failures}</p></div>', 
                   unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "🔍 Detailed Results", "📋 Failed Rules", "📊 Analytics", "📄 Report"])
    
    with tab1:
        show_overview_tab(report_generator, summary)
    
    with tab2:
        show_detailed_results_tab(results)
    
    with tab3:
        show_failed_rules_tab(results)
    
    with tab4:
        show_analytics_tab(report_generator)
    
    with tab5:
        show_report_tab(report_generator)

def show_overview_tab(report_generator, summary):
    """Show overview tab content."""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Summary chart
        fig = report_generator.create_summary_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Issue breakdown
        st.markdown("### 🚨 Issues by Severity")
        
        severity_data = [
            ("Critical", summary.critical_failures, "#ff4b4b"),
            ("High", summary.high_failures, "#ff8c00"),
            ("Medium", summary.medium_failures, "#ffd700"),
            ("Low", summary.low_failures, "#90ee90")
        ]
        
        for severity, count, color in severity_data:
            if count > 0:
                st.markdown(f"""
                <div class="metric-card severity-{severity.lower()}">
                    <strong>{SEVERITY_LEVELS[severity]['icon']} {severity}</strong>: {count} issues
                </div>
                """, unsafe_allow_html=True)

def show_detailed_results_tab(results):
    """Show detailed results tab."""
    st.markdown("### 📋 All Validation Results")
    
    # Create DataFrame
    df_data = []
    for result in results:
        df_data.append({
            'Rule ID': result.rule_id,
            'Status': '✅ PASS' if result.passed else '❌ FAIL',
            'Severity': f"{SEVERITY_LEVELS[result.severity]['icon']} {result.severity}",
            'Category': result.category,
            'Description': result.rule_description,
            'Details': result.details[:100] + "..." if len(result.details) > 100 else result.details
        })
    
    df = pd.DataFrame(df_data)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "PASS", "FAIL"])
    with col2:
        severity_filter = st.selectbox("Filter by Severity", ["All", "Critical", "High", "Medium", "Low"])
    with col3:
        category_filter = st.selectbox("Filter by Category", ["All"] + df['Category'].unique().tolist())
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['Status'].str.contains(status_filter)]
    if severity_filter != "All":
        filtered_df = filtered_df[filtered_df['Severity'].str.contains(severity_filter)]
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['Category'] == category_filter]
    
    # Display table
    st.dataframe(filtered_df, use_container_width=True, height=400)

def show_failed_rules_tab(results):
    """Show failed rules tab."""
    failed_results = [r for r in results if not r.passed]
    
    if not failed_results:
        st.success("🎉 No failed validations! Your document passes all rules.")
        return
    
    st.markdown(f"### ❌ Failed Validations ({len(failed_results)} rules)")
    
    # Group by severity
    for severity in ['Critical', 'High', 'Medium', 'Low']:
        severity_failures = [r for r in failed_results if r.severity == severity]
        if severity_failures:
            with st.expander(f"{SEVERITY_LEVELS[severity]['icon']} {severity} Issues ({len(severity_failures)})", 
                           expanded=(severity == 'Critical')):
                for result in severity_failures:
                    st.markdown(f"""
                    **{result.rule_id}:** {result.rule_description}
                    
                    *Category:* {result.category}  
                    *Details:* {result.details}
                    """)
                    st.divider()

def show_analytics_tab(report_generator):
    """Show analytics tab."""
    st.markdown("### 📊 Validation Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Severity breakdown
        fig_severity = report_generator.create_severity_breakdown_chart()
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col2:
        # Category breakdown
        fig_category = report_generator.create_category_breakdown_chart()
        st.plotly_chart(fig_category, use_container_width=True)

def show_report_tab(report_generator):
    """Show report tab."""
    st.markdown("### 📄 Validation Report")
    
    # Generate report
    detailed_report = report_generator.generate_detailed_report()
    
    # Display report
    st.markdown(detailed_report)
    
    # Download options
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # Download detailed report
        st.download_button(
            label="📥 Download Detailed Report",
            data=detailed_report,
            file_name=f"brd_validation_report_{int(time.time())}.md",
            mime="text/markdown"
        )
    
    with col2:
        # Download results CSV
        df = report_generator.generate_results_dataframe()
        csv = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Results CSV",
            data=csv,
            file_name=f"brd_validation_results_{int(time.time())}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()