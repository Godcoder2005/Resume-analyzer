import streamlit as st
import tempfile
from backend_analyzer import workflow

st.set_page_config(
    page_title="Resume Analyzer",
    layout="centered"
)

st.title("📄 AI Resume Analyzer")
st.caption("Upload your resume and get professional feedback")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF / DOCX / HTML)",
    type=["pdf", "docx", "html"]
)

if uploaded_file:
    # Save uploaded file safely
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.getbuffer())
        file_path = tmp.name

    st.success("Resume uploaded successfully")

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing resume..."):
            try:
                result = workflow.invoke({"pdf_path": file_path})

                st.subheader("📊 Resume Score")
                st.metric("Score", f"{result['score']} / 10")

                st.subheader("🧠 Justification")
                st.write(result["justification"])

                st.subheader("🛠 Suggested Fixes")
                st.write(result["suggested_fixes"])

                st.subheader("📝 Detailed Feedback")
                st.write(result["feedback"])

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
