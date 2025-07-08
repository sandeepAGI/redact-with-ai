"""
Main Streamlit application for Legal Document Anonymization Tool
Simple, focused interface with 4-page navigation
"""

import streamlit as st
import os
import json
import time
from document_processor import DocumentProcessor
from ollama_client import OllamaClient
from testing_engine import ReconstructionTester
from scoring_system import ScoringSystem
from config import ANONYMIZATION_STRATEGIES, DOCUMENT_LIMITS


# Page configuration
st.set_page_config(
    page_title="Legal Document Anonymizer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_documents' not in st.session_state:
    st.session_state.processed_documents = {}
if 'anonymization_results' not in st.session_state:
    st.session_state.anonymization_results = {}
if 'test_results' not in st.session_state:
    st.session_state.test_results = {}
if 'current_document' not in st.session_state:
    st.session_state.current_document = None

# Initialize components
@st.cache_resource
def get_components():
    return {
        'processor': DocumentProcessor(),
        'ollama': OllamaClient(),
        'tester': ReconstructionTester(),
        'scorer': ScoringSystem()
    }

components = get_components()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page",
    ["Upload", "Anonymize", "Test", "Results"]
)

# Connection status
st.sidebar.subheader("System Status")
with st.sidebar:
    connection_status = components['ollama'].test_connection()
    if connection_status['success']:
        st.success(f"✅ Ollama Connected")
        if connection_status['llama_available']:
            st.success("✅ Llama 3 Available")
        else:
            st.warning("⚠️ Llama 3 Not Found")
    else:
        st.error("❌ Ollama Disconnected")
        st.error(connection_status['error'])

# Main content
st.title("Legal Document Anonymization Tool")

if page == "Upload":
    st.header("📁 Document Upload")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload legal documents",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help=f"Maximum {DOCUMENT_LIMITS['max_batch_files']} files, {DOCUMENT_LIMITS['max_file_size_mb']}MB each"
    )
    
    if uploaded_files:
        if len(uploaded_files) > DOCUMENT_LIMITS['max_batch_files']:
            st.error(f"Too many files! Maximum: {DOCUMENT_LIMITS['max_batch_files']}")
        else:
            st.subheader("Processing Documents...")
            
            # Process files
            progress_bar = st.progress(0)
            results = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    result = components['processor'].process_file(uploaded_file)
                    results.append(result)
                    
                    if result['success']:
                        # Store in session state
                        st.session_state.processed_documents[uploaded_file.name] = result
                        
                        # Add to corpus for testing
                        components['tester'].add_to_corpus(result)
                        
                        # Display summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Word Count", result['word_count'])
                        with col2:
                            st.metric("Chunks", result['metadata']['chunk_count'])
                        with col3:
                            st.metric("Entities", result['metadata']['total_entities'])
                        
                        st.success(f"✅ {uploaded_file.name} processed successfully")
                    else:
                        st.error(f"❌ {uploaded_file.name}: {result['error']}")
            
            progress_bar.empty()
            
            # Document selection
            if st.session_state.processed_documents:
                st.subheader("Select Document for Anonymization")
                doc_names = list(st.session_state.processed_documents.keys())
                selected_doc = st.selectbox("Choose document", doc_names)
                
                if selected_doc:
                    st.session_state.current_document = selected_doc
                    doc_data = st.session_state.processed_documents[selected_doc]
                    
                    # Document preview
                    with st.expander("Document Preview"):
                        st.text_area("Content", doc_data['text'][:1000] + "..." if len(doc_data['text']) > 1000 else doc_data['text'], height=200)
                    
                    # Entity breakdown
                    st.subheader("Entity Analysis")
                    entity_cols = st.columns(5)
                    for i, (category, entities) in enumerate(doc_data['entities'].items()):
                        with entity_cols[i]:
                            st.metric(category.title(), len(entities))
                            if entities:
                                with st.expander(f"View {category}"):
                                    for entity in entities[:5]:  # Show first 5
                                        st.write(f"• {entity['text']} ({entity['label']})")

elif page == "Anonymize":
    st.header("🔒 Document Anonymization")
    
    if not st.session_state.current_document:
        st.warning("Please upload and select a document first.")
    else:
        doc_data = st.session_state.processed_documents[st.session_state.current_document]
        
        st.subheader(f"Anonymizing: {st.session_state.current_document}")
        
        # Anonymization settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Strategy Selection")
            strategy = st.selectbox(
                "Choose anonymization strategy",
                list(ANONYMIZATION_STRATEGIES.keys()),
                format_func=lambda x: ANONYMIZATION_STRATEGIES[x]['name']
            )
            
            st.write(ANONYMIZATION_STRATEGIES[strategy]['description'])
            
            # Custom guidelines for custom strategy
            custom_guidelines = ""
            if strategy == "custom":
                custom_guidelines = st.text_area(
                    "Custom Guidelines",
                    placeholder="Enter specific anonymization instructions..."
                )
        
        with col2:
            st.subheader("Processing Options")
            
            # Level settings
            level = st.selectbox(
                "Anonymization Level",
                ["Light", "Standard", "Aggressive"]
            )
            
            target_audience = st.selectbox(
                "Target Audience",
                ["Internal", "External", "Public"]
            )
            
            practice_area = st.selectbox(
                "Practice Area",
                ["Litigation", "Corporate", "IP", "Employment", "General"]
            )
        
        # Anonymization button
        if st.button("🚀 Start Anonymization", type="primary"):
            if not connection_status['success']:
                st.error("Ollama connection required for anonymization")
            else:
                with st.spinner("Anonymizing document..."):
                    progress_container = st.container()
                    
                    # Show progress
                    with progress_container:
                        st.write(f"Processing {len(doc_data['chunks'])} chunks...")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                    
                    # Anonymize chunks
                    result = components['ollama'].anonymize_chunks(
                        doc_data['chunks'],
                        strategy=strategy,
                        custom_guidelines=custom_guidelines if strategy == "custom" else None
                    )
                    
                    if result['success']:
                        # Store results
                        st.session_state.anonymization_results[st.session_state.current_document] = result
                        
                        # Display results
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Chunks Processed", result['chunks_processed'])
                        with col2:
                            st.metric("Processing Time", f"{result['total_processing_time']:.1f}s")
                        with col3:
                            st.metric("Total Tokens", result['total_tokens'])
                        
                        st.success("✅ Anonymization completed!")
                        
                        # Show before/after comparison
                        st.subheader("Before/After Comparison")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Original")
                            st.text_area("", doc_data['text'][:1000] + "..." if len(doc_data['text']) > 1000 else doc_data['text'], height=300, key="original")
                        
                        with col2:
                            st.subheader("Anonymized")
                            st.text_area("", result['anonymized_text'][:1000] + "..." if len(result['anonymized_text']) > 1000 else result['anonymized_text'], height=300, key="anonymized")
                        
                        # Failed chunks
                        if result['failed_chunks']:
                            st.warning(f"⚠️ {len(result['failed_chunks'])} chunks failed to process")
                            with st.expander("View Failed Chunks"):
                                for failed in result['failed_chunks']:
                                    st.write(f"Chunk {failed['chunk_id']}: {failed['error']}")
                    
                    else:
                        st.error(f"❌ Anonymization failed: {result['error']}")

elif page == "Test":
    st.header("🧪 Reconstruction Resistance Testing")
    
    if not st.session_state.current_document:
        st.warning("Please upload and select a document first.")
    elif st.session_state.current_document not in st.session_state.anonymization_results:
        st.warning("Please anonymize the document first.")
    else:
        doc_data = st.session_state.processed_documents[st.session_state.current_document]
        anon_result = st.session_state.anonymization_results[st.session_state.current_document]
        
        st.subheader(f"Testing: {st.session_state.current_document}")
        
        # Test configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Test Configuration")
            
            run_adversarial = st.checkbox("Run Adversarial Tests", value=True)
            
            if run_adversarial:
                attacker_levels = st.multiselect(
                    "Attacker Levels",
                    ["naive", "professional", "advanced", "expert"],
                    default=["naive", "professional"]
                )
        
        with col2:
            st.subheader("Corpus Information")
            st.metric("Documents in Corpus", len(components['tester'].document_corpus))
            st.info("Corpus is used for cross-reference testing")
        
        # Run tests button
        if st.button("🧪 Run Tests", type="primary"):
            if not connection_status['success']:
                st.error("Ollama connection required for contextual reconstruction testing")
            else:
                with st.spinner("Running reconstruction resistance tests..."):
                    # Run main test suite
                    test_result = components['tester'].run_all_tests(
                        doc_data['text'],
                        anon_result['anonymized_text'],
                        anon_result['strategy']
                    )
                    
                    if test_result['success']:
                        # Store results
                        st.session_state.test_results[st.session_state.current_document] = test_result
                        
                        # Display results
                        st.success("✅ Testing completed!")
                        
                        # Overall score
                        st.subheader("Overall Resistance Score")
                        score = test_result['resistance_score']
                        
                        # Color coding
                        if score >= 90:
                            score_color = "green"
                        elif score >= 80:
                            score_color = "lightgreen"
                        elif score >= 70:
                            score_color = "yellow"
                        elif score >= 60:
                            score_color = "orange"
                        else:
                            score_color = "red"
                        
                        st.markdown(f"<h1 style='color: {score_color}'>{score}/100</h1>", unsafe_allow_html=True)
                        
                        # Test breakdown
                        st.subheader("Test Results Breakdown")
                        
                        for test_name, result in test_result['test_results'].items():
                            if 'score' in result:
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.write(f"**{test_name.replace('_', ' ').title()}**")
                                with col2:
                                    st.metric("Score", f"{result['score']:.1f}/100")
                                with col3:
                                    risk_level = result.get('risk_level', 'unknown')
                                    color = {"low": "green", "medium": "orange", "high": "red"}.get(risk_level, "gray")
                                    st.markdown(f"<span style='color: {color}'>● {risk_level.upper()}</span>", unsafe_allow_html=True)
                        
                        # Risk assessment
                        st.subheader("Risk Assessment")
                        risk_assessment = test_result['risk_assessment']
                        
                        if risk_assessment['high_risk_factors']:
                            st.error(f"🔴 High Risk: {', '.join(risk_assessment['high_risk_factors'])}")
                        if risk_assessment['medium_risk_factors']:
                            st.warning(f"🟡 Medium Risk: {', '.join(risk_assessment['medium_risk_factors'])}")
                        if risk_assessment['low_risk_factors']:
                            st.success(f"🟢 Low Risk: {', '.join(risk_assessment['low_risk_factors'])}")
                        
                        # Recommendations
                        st.subheader("Recommendations")
                        for rec in test_result['recommendations']:
                            st.write(f"• {rec}")
                        
                        # Adversarial tests
                        if run_adversarial and attacker_levels:
                            st.subheader("Adversarial Test Results")
                            
                            adversarial_results = components['tester'].run_adversarial_tests(
                                anon_result['anonymized_text'],
                                attacker_levels
                            )
                            
                            for level, result in adversarial_results.items():
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write(f"**{level.title()} Attacker**")
                                with col2:
                                    st.metric("Success Rate", f"{result['success_rate']:.1%}")
                                with col3:
                                    st.metric("Resistance", f"{result['resistance_score']:.1f}/100")
                    
                    else:
                        st.error(f"❌ Testing failed: {test_result['error']}")

elif page == "Results":
    st.header("📊 Results & Export")
    
    if not st.session_state.current_document:
        st.warning("Please upload and select a document first.")
    else:
        doc_name = st.session_state.current_document
        
        # Check what's available
        has_anonymization = doc_name in st.session_state.anonymization_results
        has_testing = doc_name in st.session_state.test_results
        
        if not has_anonymization:
            st.warning("No anonymization results available. Please anonymize the document first.")
        elif not has_testing:
            st.warning("No test results available. Please run tests first.")
        else:
            # Get results
            doc_data = st.session_state.processed_documents[doc_name]
            anon_result = st.session_state.anonymization_results[doc_name]
            test_result = st.session_state.test_results[doc_name]
            
            # Calculate strategic value score
            strategic_score = components['scorer'].calculate_strategic_value_score(
                doc_data['text'],
                anon_result['anonymized_text'],
                anon_result['strategy']
            )
            
            # Calculate overall score
            overall_result = components['scorer'].calculate_overall_score(
                test_result['test_results'],
                {'strategic_value': strategic_score}
            )
            
            # Display comprehensive results
            st.subheader("📈 Comprehensive Score Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Overall Quality Score",
                    f"{overall_result['overall_score']:.1f}/100",
                    help="Combined reconstruction resistance and strategic value"
                )
                
                quality_level = overall_result['quality_level']
                st.markdown(f"**Quality Level:** {quality_level['level'].upper()}")
                st.markdown(f"*{quality_level['description']}*")
            
            with col2:
                st.metric(
                    "Reconstruction Resistance",
                    f"{overall_result['reconstruction_resistance_score']:.1f}/100",
                    help="How well the document resists reconstruction attempts"
                )
            
            with col3:
                st.metric(
                    "Strategic Value Preservation",
                    f"{overall_result['strategic_value_score']:.1f}/100",
                    help="How well legal and business value is preserved"
                )
            
            # Detailed breakdown
            st.subheader("📋 Detailed Score Breakdown")
            
            # Reconstruction resistance breakdown
            st.write("**Reconstruction Resistance Components:**")
            for test_name, result in test_result['test_results'].items():
                if 'score' in result:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {test_name.replace('_', ' ').title()}")
                    with col2:
                        st.write(f"{result['score']:.1f}/100")
            
            # Export options
            st.subheader("📥 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 Export Anonymized Document"):
                    # Create anonymized document
                    export_data = {
                        "filename": doc_name,
                        "original_text": doc_data['text'],
                        "anonymized_text": anon_result['anonymized_text'],
                        "strategy": anon_result['strategy'],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    os.makedirs("exports", exist_ok=True)
                    export_path = f"exports/{doc_name}_anonymized.json"
                    
                    with open(export_path, 'w') as f:
                        json.dump(export_data, f, indent=2)
                    
                    st.success(f"✅ Document exported to {export_path}")
            
            with col2:
                if st.button("📊 Export Test Report"):
                    # Create test report
                    report_data = {
                        "document": doc_name,
                        "overall_score": overall_result['overall_score'],
                        "quality_level": overall_result['quality_level'],
                        "test_results": test_result['test_results'],
                        "recommendations": test_result['recommendations'],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    os.makedirs("exports", exist_ok=True)
                    report_path = f"exports/{doc_name}_report.json"
                    
                    with open(report_path, 'w') as f:
                        json.dump(report_data, f, indent=2)
                    
                    st.success(f"✅ Report exported to {report_path}")
            
            with col3:
                if st.button("📈 Export All Data"):
                    # Create comprehensive export
                    comprehensive_data = {
                        "document_info": {
                            "filename": doc_name,
                            "word_count": doc_data['word_count'],
                            "entities": doc_data['entities'],
                            "legal_patterns": doc_data['legal_patterns']
                        },
                        "anonymization_results": anon_result,
                        "test_results": test_result,
                        "scores": overall_result,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    os.makedirs("exports", exist_ok=True)
                    comprehensive_path = f"exports/{doc_name}_comprehensive.json"
                    
                    with open(comprehensive_path, 'w') as f:
                        json.dump(comprehensive_data, f, indent=2)
                    
                    st.success(f"✅ Comprehensive data exported to {comprehensive_path}")
            
            # Download buttons would go here in a full implementation
            st.info("💡 Exported files are saved in the 'exports' folder")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Legal Document Anonymization Tool**")
st.sidebar.markdown("Built with Streamlit + Ollama + Llama 3")
st.sidebar.markdown("🔒 All processing is local")