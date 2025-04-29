import streamlit as st
from llm import *
from io import BytesIO
from datetime import datetime

def main():
    st.set_page_config(layout="wide", page_title="Advanced Document Validator Pro")
    
    # Initialize session state
    if 'document_text' not in st.session_state:
        st.session_state.document_text = ""
    if 'document_data' not in st.session_state:
        st.session_state.document_data = {}
    if 'rules' not in st.session_state:
        st.session_state.rules = []
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = []
    if 'editable_data' not in st.session_state:
        st.session_state.editable_data = {}
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .big-font {
        font-size:18px !important;
    }
    .rule-card {
        border-left: 4px solid #4e79a7;
        padding: 10px;
        margin: 5px 0;
        background-color: #f0f2f6;
    }
    .passed {
        border-left: 4px solid #2ecc71 !important;
    }
    .failed {
        border-left: 4px solid #e74c3c !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Go to", 
                               ["📄 Document Processing", "⚙️ Rule Management", "✅ Validation Dashboard"])
    
    # Document Processing Section
    if app_mode == "📄 Document Processing":
        st.header("📄 Document Processing")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Upload Document")
            uploaded_file = st.file_uploader("Upload PDF/image", 
                                           type=["pdf", "png", "jpg", "jpeg"], 
                                           key="uploader")
            
            if uploaded_file:
                try:
                    file_bytes = uploaded_file.read()
                    with st.spinner("Extracting text..."):
                        st.session_state.document_text = extract_text_from_document(uploaded_file, file_bytes)
                    
                    with st.spinner("Extracting data with LLM..."):
                        st.session_state.document_data = extract_data_from_text(st.session_state.document_text)
                        st.session_state.editable_data = st.session_state.document_data.copy()
                    
                    st.success("✅ Document processed successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with col2:
            if st.session_state.document_text:
                st.subheader("Extracted Content")
                
                with st.expander("🔍 Raw Extracted Text", expanded=True):
                    edited_text = st.text_area("Edit extracted text", 
                                             value=st.session_state.document_text, 
                                             height=300,
                                             key="edited_text",
                                             label_visibility="collapsed")
                    if edited_text != st.session_state.document_text:
                        st.session_state.document_text = edited_text
                        with st.spinner("Updating extracted data..."):
                            st.session_state.document_data = extract_data_from_text(st.session_state.document_text)
                            st.session_state.editable_data = st.session_state.document_data.copy()
                
                if st.session_state.document_data:
                    st.subheader("📊 Extracted Data Fields")
                    st.info("Edit the values below if needed before validation")
                    
                    # Create editable fields for each data category
                    cols = st.columns(3)
                    for i, (category, value) in enumerate(st.session_state.document_data.items()):
                        with cols[i % 3]:
                            if category == "money":
                                new_value = st.number_input(f"{category.capitalize()}", 
                                                          value=float(value) if value else 0.0,
                                                          key=f"edit_{category}")
                            elif category in ["date", "time"]:
                                new_value = st.text_input(f"{category.capitalize()}", 
                                                        value=value,
                                                        key=f"edit_{category}")
                            else:
                                new_value = st.text_input(f"{category.capitalize()}", 
                                                         value=value,
                                                         key=f"edit_{category}")
                            
                            if new_value != value:
                                st.session_state.editable_data[category] = new_value
                    
                    with st.expander("🔧 Advanced Data Editing (JSON)"):
                        edited_json = st.text_area("Edit full JSON data",
                                                 value=json.dumps(st.session_state.editable_data, indent=2),
                                                 height=200,
                                                 key="edited_json")
                        try:
                            if edited_json != json.dumps(st.session_state.editable_data, indent=2):
                                st.session_state.editable_data = json.loads(edited_json)
                                st.success("Data updated from JSON!")
                        except json.JSONDecodeError:
                            st.error("Invalid JSON format")
    
    # Rule Management Section
    elif app_mode == "⚙️ Rule Management":
        st.header("⚙️ Rule Management")
        
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.subheader("➕ Add New Rule")
            rule_text = st.text_area("Enter rule in natural language:", 
                                    placeholder="e.g. 'Invoice date must be after 2025-01-01'",
                                    height=100,
                                    key="rule_text")
            
            if st.button("✨ Parse and Add Rule", use_container_width=True):
                if rule_text:
                    with st.spinner("Parsing rule with LLM..."):
                        try:
                            new_rule = parse_rule(rule_text)
                            if new_rule:
                                st.session_state.rules.append(new_rule)
                                st.success("✅ Rule added successfully!")
                                st.balloons()
                        except Exception as e:
                            st.error(f"❌ Error parsing rule: {str(e)}")
                else:
                    st.warning("⚠ Please enter a rule first")
        
        with col2:
            st.subheader("📋 Current Rules")
            if not st.session_state.rules:
                st.info("ℹ No rules defined yet. Add your first rule above.")
            else:
                for i, rule in enumerate(st.session_state.rules):
                    condition_map = {
                        "equals": "=",
                        "not_equals": "≠",
                        "greater_than": ">",
                        "less_than": "<",
                        "before_date": "before",
                        "after_date": "after",
                        "contains": "contains",
                        "not_contains": "does not contain"
                    }
                    
                    condition_symbol = condition_map.get(rule.get('condition', ''), rule.get('condition', ''))
                    
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="rule-card">
                                <p class="big-font">
                                    <b>Rule #{i+1}:</b> {rule.get('category', '').capitalize()} {condition_symbol} {rule.get('value', '')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("🗑️", key=f"del_{i}"):
                                st.session_state.rules.pop(i)
                                st.success("Rule deleted!")
                                st.rerun()
                    
                    with st.expander(f"✏️ Edit Rule #{i+1}", expanded=False):
                        edited_rule = {}
                        edited_rule['category'] = st.selectbox(
                            "Category",
                            options=["money", "date", "time", "text"],
                            index=["money", "date", "time", "text"].index(rule.get('category', 'money')),
                            key=f"category_{i}"
                        )
                        
                        condition_options = {
                            "money": ["equals", "not_equals", "greater_than", "less_than"],
                            "date": ["equals", "not_equals", "before_date", "after_date"],
                            "time": ["equals", "not_equals", "greater_than", "less_than"],
                            "text": ["equals", "not_equals", "contains", "not_contains"]
                        }
                        
                        edited_rule['condition'] = st.selectbox(
                            "Condition",
                            options=condition_options[edited_rule['category']],
                            index=condition_options[edited_rule['category']].index(rule.get('condition')),
                            key=f"condition_{i}"
                        )
                        
                        edited_rule['value'] = st.text_input(
                            "Value",
                            value=str(rule.get('value', '')),
                            key=f"value_{i}"
                        )
                        
                        if st.button("💾 Save Changes", key=f"save_{i}"):
                            st.session_state.rules[i] = edited_rule
                            st.success("Rule updated!")
    
    # Validation Dashboard Section
    elif app_mode == "✅ Validation Dashboard":
        st.header("✅ Validation Dashboard")
        
        if not st.session_state.document_data:
            st.warning("⚠ Please process a document first in the Document Processing section")
        elif not st.session_state.rules:
            st.warning("⚠ Please add at least one rule in the Rule Management section")
        else:
            if st.button("🔍 Run All Validations", use_container_width=True):
                st.session_state.validation_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, rule in enumerate(st.session_state.rules):
                    progress = (i + 1) / len(st.session_state.rules)
                    progress_bar.progress(progress)
                    status_text.text(f"Validating Rule #{i+1} of {len(st.session_state.rules)}...")
                    
                    with st.spinner(f"Validating Rule #{i+1}..."):
                        try:
                            result = validate_rule(
                                rule,
                                st.session_state.editable_data if st.session_state.editable_data else st.session_state.document_data
                            )
                            st.session_state.validation_results.append(result)
                        except Exception as e:
                            st.error(f"Validation error for Rule #{i+1}: {str(e)}")
                
                progress_bar.empty()
                status_text.empty()
                st.success("🎉 All validations completed!")
                st.balloons()
            
            if st.session_state.validation_results:
                st.subheader("📊 Validation Summary")
                
                total_rules = len(st.session_state.validation_results)
                passed = sum(1 for r in st.session_state.validation_results if r.get('status') == 'PASS')
                failed = sum(1 for r in st.session_state.validation_results if r.get('status') == 'FAIL')
                errors = total_rules - passed - failed
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Rules", total_rules)
                col2.metric("Passed", passed, f"{passed/total_rules*100:.1f}%")
                col3.metric("Failed", failed, f"{failed/total_rules*100:.1f}%", delta_color="inverse")
                
                st.subheader("📝 Detailed Results")
                for i, result in enumerate(st.session_state.validation_results):
                    rule = st.session_state.rules[i]
                    actual = result.get('actual_value', 'N/A')
                    expected = result.get('expected_value', 'N/A')
                    condition = rule.get('condition', '').replace('_', ' ')
                    
                    status_class = ""
                    if result['status'] == "PASS":
                        status_class = "passed"
                        status_icon = "✅"
                        status_text = f"PASS: {actual} is {condition} {expected}"
                    elif result['status'] == "FAIL":
                        status_class = "failed"
                        status_icon = "❌"
                        status_text = f"FAIL: {actual} is not {condition} {expected}"
                    else:
                        status_icon = "⚠️"
                        status_text = f"ERROR: {result.get('message', 'Unknown error')}"
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="rule-card {status_class}">
                            <p class="big-font">
                                <b>{status_icon} Rule #{i+1}:</b> {rule.get('category', '').capitalize()} {condition} {expected}<br>
                                <b>Result:</b> {status_text}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander("🔍 View details", expanded=False):
                            st.write(f"**Field:** {rule.get('category', '').capitalize()}")
                            st.write(f"**Condition:** {condition.title()}")
                            st.write(f"**Expected Value:** {expected}")
                            st.write(f"**Actual Value:** {actual}")
                            
                            if result.get('message'):
                                st.write(f"**Note:** {result.get('message')}")
                            
                            st.json(result)

if __name__ == "__main__":
    main()