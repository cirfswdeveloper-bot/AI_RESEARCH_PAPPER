import streamlit as st
import io
import zipfile
import pypandoc
import requests

from arxiv_api import get_related_papers            # Fetches related papers from arXiv
from gpt_generator import generate_sections         # Uses Gemini to generate paper sections
from latex_generator import create_latex_file       # Generates LaTeX code from sections
from docx_generator import create_docx_bytes        # Generates Word DOCX from sections

# ------------------ Helper Function: Markdown Generator ------------------ #
def create_markdown(topic, sections, bib_entries):
    """Generates Markdown content from paper sections and references."""
    md = f"# {topic}\n\n"
    for sec, txt in sections.items():
        md += f"## {sec.capitalize()}\n{txt}\n\n"
    md += "## References\n" + "\n".join(bib_entries)
    return md

# ------------------ Page Configuration ------------------ #
st.set_page_config(page_title="AI-Powered Research Paper Writer", layout="wide")

# ------------------ Modern Colorful UI Styling ------------------ #
st.markdown("""
    <style>

        /* -------- Global UI -------- */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #f8fbff 0%, #e6f0ff 100%);
            color: #1e1e2f;
        }

        h1, h2, h3 {
            font-weight: 700;
            line-height: 1.3;
        }

        h1 {
            color: #1e90ff !important;  /* Dodger Blue */
            font-size: 2.8rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }

        h2 {
            color: #264653;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }

        h3 {
            color: #457b9d;
        }

        /* -------- Input Fields -------- */
        .stTextInput > div > div > input {
            padding: 0.75rem 1rem;
            font-size: 1.1rem;
            border: 2px solid #d0d7e3;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
            transition: 0.3s;
        }

        .stTextInput > div > div > input:focus {
            border-color: #4dabf7;
            box-shadow: 0px 5px 15px rgba(77,171,247,0.25);
        }

        /* -------- Buttons -------- */
        .stButton > button, .stDownloadButton button, .stDownloadButton > button {
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
            color: #fff;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            box-shadow: 0px 4px 14px rgba(0,0,0,0.2);
            transition: all 0.3s ease-in-out;
        }

        .stButton > button:hover, .stDownloadButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0px 6px 18px rgba(0,0,0,0.3);
            background: linear-gradient(90deg, #2575fc 0%, #6a11cb 100%);
        }

        .stDownloadButton button, .stDownloadButton > button {
            background: linear-gradient(90deg, #f9b71c 0%, #f78c1f 100%) !important;
        }

        /* -------- Sidebar Style -------- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #dbe9ff 100%);
            border-right: 2px solid #d0d7e3;
            box-shadow: 3px 0px 12px rgba(0,0,0,0.05);
            padding: 1rem 0;
        }

        .stSidebar .stInfo {
            background: #e0f0ff;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
        }

        /* -------- Main Container -------- */
        .block-container {
            padding: 2rem 3rem;
            min-height: 90vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        /* -------- Links -------- */
        a {
            color: #2575fc;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }

        a:hover {
            color: #6a11cb;
            text-decoration: underline;
        }

        /* -------- Responsive -------- */
        @media screen and (max-width: 768px) {
            .block-container {
                padding: 1.5rem 1.5rem;
            }
            h1 {
                font-size: 2.2rem;
            }
            h2 {
                font-size: 1.6rem;
            }
        }

    </style>
""", unsafe_allow_html=True)


# ------------------ Sidebar Content ------------------ #
st.sidebar.markdown("<h1>ℹ️ Research Paper AI</h1>", unsafe_allow_html=True)
st.sidebar.info("""
This AI-powered app helps you generate structured research papers 
based on your topic using **ArXiv** and **Gemini (Google LLM)**.

**✨ Key Features:**
- Automatically fetches related papers
- Writes Abstract, Introduction, Related Work, etc.
- Exports to **LaTeX**, **DOCX**, **PDF**, **Markdown**, **ZIP**
""")
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tip:** Enter a clear research topic above and click **Generate Paper** for instant results!")

# ------------------ Main Page Content ------------------ #
with st.container():
    st.markdown("<h1 style='text-align:center;'>📝 AI-Powered Research Paper Writer</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # ----------- User Input Section ----------- #
    topic = st.text_input("🔍 Enter your research topic:")
    generate = st.button("🚀 Generate Paper")

    if generate and topic:

        # ----------- Step 1: Fetch Related Papers ----------- #
        with st.spinner("📚 Fetching related papers..."):
            papers, bib_entries = get_related_papers(topic)

        # ----------- Step 2: Generate Paper Sections ----------- #
        with st.spinner("📝 Generating paper sections..."):
            sections, bib_entries = generate_sections(topic, papers)

        # ----------- Step 3: Format Outputs ----------- #
        latex_code = create_latex_file(sections, bib_entries)
        docx_bytes = create_docx_bytes(sections, bib_entries)
        markdown = create_markdown(topic, sections, bib_entries)

        st.success("✅ Paper generated successfully!")
        st.markdown("### 📥 Download Options")

        # ----------- Download Buttons ----------- #
        col1, col2, col3 = st.columns(3)

        # LaTeX and Markdown Downloads
        with col1:
            st.download_button(
                label="📄 LaTeX (.tex)",
                data=latex_code,
                file_name=f"{topic.replace(' ', '_')}.tex",
                mime="text/x-tex"
            )
            st.download_button(
                label="📝 Markdown (.md)",
                data=markdown,
                file_name=f"{topic.replace(' ', '_')}.md",
                mime="text/markdown"
            )

        # DOCX Download
        with col2:
            st.download_button(
                label="🧾 DOCX (.docx)",
                data=docx_bytes,
                file_name=f"{topic.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # PDF Download using pypandoc (LaTeX to PDF)
        with col3:
            try:
                pdf_bytes = pypandoc.convert_text(latex_code, 'pdf', format='latex')
                st.download_button(
                    label="📕 PDF (.pdf)",
                    data=pdf_bytes,
                    file_name=f"{topic.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception:
                st.warning("⚠️ PDF conversion unavailable. Install `pypandoc` and a LaTeX engine.")

        # ----------- ZIP Download (All LaTeX Sections Separately) ----------- #
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr(f"{topic.replace(' ', '_')}.tex", latex_code)
            for sec, txt in sections.items():
                section_content = f"\\section{{{sec.capitalize()}}}\n{txt}\n"
                zf.writestr(f"{sec}.tex", section_content)
        zip_buffer.seek(0)

        st.download_button(
            label="🗜️ ZIP (All LaTeX Files)",
            data=zip_buffer,
            file_name=f"{topic.replace(' ', '_')}_latex.zip",
            mime="application/zip"
        )

# ------------------ Footer Styling ------------------ #
st.markdown("""
    <style>
        /* Add bottom padding so content doesn't hide behind footer */
        .block-container {
            padding-bottom: 150px !important;
        }

        /* Footer styling */
        .footer {
            width: 100%;
            text-align: center;
            padding: 20px 0;
            background: linear-gradient(90deg, #00c6ff, #0072ff);
            color: #fff;
            font-size: 0.95rem;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            box-shadow: 0 -3px 10px rgba(0,0,0,0.1);
            position: relative;
            margin-top: 50px;
            transition: all 0.3s ease-in-out;
        }

        .footer:hover {
            background: linear-gradient(90deg, #0072ff, #00c6ff);
            box-shadow: 0 -5px 15px rgba(0,0,0,0.2);
        }

        .footer a {
            color: #fff;
            text-decoration: none;
            font-weight: bold;
            transition: color 0.3s;
        }

        .footer a:hover {
            text-decoration: underline;
            color: #ffd700;
        }

        /* Responsive text */
        @media screen and (max-width: 600px) {
            .footer {
                font-size: 0.85rem;
                padding: 15px 0;
            }
        }
    </style>

    <div class='footer'>
        🚀 <strong><a href="https://cirf.co.in/" target="_blank">Developed by CIRF</a></strong> | &copy; 2025 All Rights Reserved
    </div>
""", unsafe_allow_html=True)
