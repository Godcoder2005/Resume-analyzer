import streamlit as st
import tempfile
import os
from backend_analyzer import workflow, store

st.set_page_config(
    page_title="Resume Analyzer",
    layout="centered"
)

st.title("📄 Akshith's AI Resume Analyzer")
st.caption("Upload your resume and get professional feedback")

# User ID input should come BEFORE file upload
user_id = st.text_input('User ID', value='default_user', help="Enter a unique ID to track your progress")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF / DOCX / HTML)",
    type=["pdf", "docx", "html"]
)

if uploaded_file and user_id:
    # Save uploaded file safely
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getbuffer())
        file_path = tmp.name

    st.success("✅ Resume uploaded successfully")

    if st.button("🔍 Analyze Resume", type="primary"):
        with st.spinner("Analyzing your resume... This may take a moment."):
            try:
                # Invoke workflow with both pdf_path AND user_id
                result = workflow.invoke(
                    {
                        "pdf_path": file_path,
                        "user_id": user_id
                    },
                    config={"configurable": {"thread_id": user_id}}
                )

                # Display results
                st.divider()
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader("📊 Resume Score")
                    st.metric("Score", f"{result['score']:.1f} / 10")
                
                with col2:
                    st.subheader("🧠 Justification")
                    st.write(result["justification"])

                st.divider()

                st.subheader("🛠 Suggested Fixes")
                st.write(result["suggested_fixes"])

                st.divider()

                st.subheader("📝 Detailed Feedback")
                with st.expander("View Full Feedback", expanded=True):
                    st.write(result["feedback"])

                # Optional: Show memory info
                if st.checkbox("Show Historical Memory"):
                    namespace = ('user_id', user_id)
                    items = store.search(namespace)
                    if items:
                        st.subheader("🧠 Your Historical Resume Data")
                        for idx, item in enumerate(items, 1):
                            st.write(f"{idx}. {item.value.get('data', 'N/A')}")
                    else:
                        st.info("No historical data found. This is your first analysis!")

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.exception(e)  # Show full traceback for debugging
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(file_path)
                except:
                    pass

elif uploaded_file and not user_id:
    st.warning("⚠️ Please enter a User ID to proceed with analysis")
    
# Optional: Add instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Enter your User ID** - This helps track your progress over time
    2. **Upload your resume** in PDF, DOCX, or HTML format
    3. **Click Analyze** to get detailed feedback
    4. Review your score, justification, and suggested improvements
    5. Upload updated versions to track your improvement!
    """)

# Footer
st.divider()
st.caption("Powered by LangGraph & Google Gemini | Built by Akshith")