"""
Main backend entry point for Resume Analyzer
This file is kept for backward compatibility and imports
"""

# Import everything needed for the Streamlit frontend
from workflow import workflow
from config import store
from schemas import Analyzer, StructuredScore, MemoryOutput

# Export the main workflow for use in streamlit_ui_analyzer.py
__all__ = ['workflow', 'store', 'Analyzer', 'StructuredScore', 'MemoryOutput']



# # Due to lack of open source llms i only used the gemini free 20 hits api key with proper ans structured output 

# from langgraph.graph import END, START, StateGraph
# from langchain_google_genai import ChatGoogleGenerativeAI
# from typing import TypedDict
# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import UnstructuredPDFLoader
# from langgraph.store.memory import InMemoryStore
# from langgraph.store.memory import BaseStore
# from langchain_core.runnables import RunnableConfig
# from langchain_core.messages import SystemMessage
# import uuid


# load_dotenv()
# store = InMemoryStore()

# ################################## All llm models ########################################################

# # llm model for formatting
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0.7
# )

# # llm model - for evaluation
# llm_eval = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     temperature=0.7
# )

# # llm model - for clarity
# llm_clarity = ChatGoogleGenerativeAI(
#     model='gemini-2.5-flash',
#     temperature=0.7
# )

# # llm for long term memory reading
# llm_read = ChatGoogleGenerativeAI(
#     model='gemini-2.5-flash'
# )

# # llm for longterm memory writing
# llm_write = ChatGoogleGenerativeAI(
#     model='gemini-2.5-flash'
# )

# ################### All States and pydantic one will be used for structured output ##################

# class Analyzer(TypedDict):
#     text: str
#     user_id: str
#     formatting: str
#     clarity: str
#     skills: str
#     score: float
#     suggested_fixes: str
#     pdf_path: str
#     feedback: str
#     justification: str


# # Pydantic class for proper structured output
# class StructuredScore(BaseModel):
#     score: float = Field(..., ge=0, le=10)
#     justification: str = Field(..., description="Explanation for the score")
#     key_fixes_required: str = Field(..., description="The suggestions used to fix the resume")

# class MemoryText(BaseModel):
#     text: str = Field(description='this is the atomic details of user')
#     is_there: bool = Field(description='this part will tell about the user detail is present or not')

# class remainder_node(BaseModel):
#     should_write: bool = Field(description='this will decide whether there is a relevant text or not')
#     memories: list[MemoryText] = Field(default_factory=list)

# ################################### Section for extracting the text from pdf ###########################

# # Loading text from resume
# def extract_text_from_file(path: str) -> str:
#     with open(path, "rb") as f:
#         header = f.read(20)

#     # ---------- PDF ----------
#     if header.startswith(b"%PDF"):
#         try:
#             loader = PyPDFLoader(path)
#             pages = loader.load()
#             return "\n".join(p.page_content for p in pages)
#         except Exception:
#             # fallback only for REAL PDFs
#             import pypdf
#             reader = pypdf.PdfReader(path)
#             return "\n".join(page.extract_text() or "" for page in reader.pages)

#     # ---------- DOCX ----------
#     elif header.startswith(b"PK"):
#         from langchain_community.document_loaders import Docx2txtLoader
#         pages = Docx2txtLoader(path).load()
#         return "\n".join(p.page_content for p in pages)

#     # ---------- HTML ----------
#     elif b"<html" in header.lower():
#         from langchain_community.document_loaders import BSHTMLLoader
#         pages = BSHTMLLoader(path).load()
#         return "\n".join(p.page_content for p in pages)

#     else:
#         raise ValueError("Unsupported or corrupted resume file")

# memory_output = llm_read.with_structured_output(remainder_node)

# def create_system_prompt(feedback: str, user_details: str) -> str:
#     """Creates the system prompt with proper variable substitution"""
#     return f"""
# You are a strict, unbiased professional resume evaluator with access to long-term analytical memory.

# Your task is to assign a realistic resume score ONLY based on:
# 1. The current resume feedback summary
# 2. The user's historical resume evaluation memory (if available)

# You do NOT have access to the original resume.
# You must NOT assume anything beyond the provided feedback and memory.

# --------------------------------------------------------------------
# INPUT 1: CURRENT RESUME FEEDBACK SUMMARY
# --------------------------------------------------------------------
# {feedback}

# --------------------------------------------------------------------
# INPUT 2: HISTORICAL USER MEMORY (may be empty)
# --------------------------------------------------------------------
# {user_details}

# --------------------------------------------------------------------
# EVALUATION STRATEGY (follow strictly):

# CASE 1: IF historical memory IS AVAILABLE
# - Compare the current feedback against past evaluations.
# - Identify:
#   • improvements
#   • repeated weaknesses
#   • regressions (if any)
# - Penalize issues that have appeared repeatedly across submissions.
# - Reward clear, sustained improvements.
# - Be conservative: improvement does NOT automatically imply a high score.

# CASE 2: IF historical memory IS EMPTY
# - Treat this as a first-time resume evaluation.
# - Score ONLY based on the current feedback summary.
# - Do NOT mention history or trends.

# --------------------------------------------------------------------
# SCORING RULES:
# - Score range: 0 to 10
# - 10 → Excellent, industry-ready resume
# - 7–8 → Strong resume with minor gaps
# - 5–6 → Average resume with clear improvement areas
# - <4 → Weak or incomplete resume
# - Avoid score inflation. Most resumes fall between 5 and 7.

# --------------------------------------------------------------------
# SCORING CRITERIA (use all):
# - Structure & presentation quality
# - Communication clarity
# - Technical and professional skill strength
# - Overall readiness for professional roles
# - Consistency and progress over time (ONLY if memory exists)

# --------------------------------------------------------------------
# OUTPUT FORMAT (follow strictly):

# Score: X/10

# Justification:
# A concise paragraph explaining the score. Reference:
# - current strengths and weaknesses
# - historical patterns ONLY if memory exists

# Key Fixes Required:
# - Bullet list of the most critical fixes (max 4)
# - Fixes must be concrete, specific, and actionable
# - If an issue has appeared in past memory, prioritize it

# --------------------------------------------------------------------
# QUALITY CHECK (apply silently before answering):
# - Would two independent professional reviewers likely assign a similar score?
# - Is the score justified by both current feedback and memory (if used)?
# - Are the suggested fixes realistic and immediately actionable?

# OUTPUT: Provide ONLY the formatted result.
# Do NOT include explanations, assumptions, or meta-comments.
# """


# MEMORY_PROMPT = """
# You are responsible for maintaining long-term analytical memory for a Resume Analysis Agent.

# CURRENT USER MEMORY (historical resume evaluations and patterns):
# {user_details_content}

# TASK:
# - Review the latest resume analysis outputs and user-provided context.
# - Extract ONLY resume-relevant information that is stable or recurring over time.

# STORE MEMORY ONLY IF IT IS:
# - A repeated weakness or strength (e.g., "Project impact descriptions remain vague across versions")
# - A confirmed improvement or regression (e.g., "Formatting improved compared to previous submission")
# - A consistent skill gap or strength (e.g., "Strong Python skills, weak system design evidence")
# - A long-term professional goal explicitly stated by the user (e.g., "Targeting backend engineering roles")

# DO NOT STORE:
# - One-off comments or temporary issues
# - Emotional reactions or opinions
# - Raw resume text or personal data
# - Assumptions or inferred intent

# MEMORY RULES:
# - Each memory must be a short, atomic, factual sentence.
# - Compare against CURRENT USER MEMORY before adding anything new.
# - Set is_new=true ONLY if the information is meaningfully new.
# - If the meaning already exists, set is_new=false.
# - Do not duplicate or paraphrase existing memory.
# - If nothing qualifies as long-term memory, return should_write=false with an empty list.

# OUTPUT FORMAT (strict):
# {{
#   "should_write": true | false,
#   "memories": [
#     {{
#       "content": "<atomic resume-related memory>",
#       "is_new": true | false
#     }}
#   ]
# }}
# """

# #################################### This is the remember node ##########################################

# def remember_node(state: Analyzer, config: RunnableConfig, store: BaseStore) -> Analyzer:
#     user_id = state['user_id']
#     namespace = ('user_id', user_id)
#     last_msg = state['text']
#     items = store.search(namespace)
#     existing = "\n".join(it.value["data"] for it in items) if items else "(empty)"

#     result = memory_output.invoke([
#         SystemMessage(content=MEMORY_PROMPT.format(user_details_content=existing)),
#         {'role': 'user', 'content': last_msg}
#     ])

#     if result.should_write:
#         for mem in result.memories:
#             if mem.is_there:
#                 store.put(namespace, str(uuid.uuid4()), {'data': mem.text})

#     return state

# ######################################### loading text #############################################

# def text_loading(state: Analyzer) -> Analyzer:
#     try:
#         text = extract_text_from_file(state['pdf_path'])
#         return {'text': text}
#     except Exception as e:
#         return {'text': f"ERROR: {str(e)}"}


# ######################################### formatting #############################################

# def formatting(state: Analyzer) -> Analyzer:
#     prompt = f"""You are a strict professional resume reviewer.

# TASK: Evaluate the FORMAT of the following resume text.

# FORMAT CRITERIA:
# - Clear section headings
# - Logical ordering of sections
# - Consistent bullet points
# - Readable spacing and structure
# - No unnecessary symbols or visual clutter

# INSTRUCTIONS:
# - Do NOT evaluate content quality or skills.
# - Focus ONLY on structure and formatting.
# - Be concise and objective.

# OUTPUT:
# - One short paragraph describing format quality
# - One clear improvement suggestion (if any)

# Resume Text:
# {state['text']}
# """
#     response = llm.invoke(prompt).content
#     return {'formatting': response}


# ######################################### clarity #############################################

# def clarity(state: Analyzer) -> Analyzer:
#     prompt = f"""You are a professional technical communication reviewer.

# TASK: Evaluate the CLARITY of the following resume text.

# CLARITY CRITERIA:
# - Sentences are clear and easy to understand
# - Bullet points convey one idea at a time
# - No vague or generic statements
# - Action-oriented and specific language

# INSTRUCTIONS:
# - Do NOT judge formatting or skill relevance.
# - Focus ONLY on clarity and readability.
# - Be precise and professional.

# OUTPUT:
# - One short paragraph on clarity
# - One concrete suggestion to improve clarity

# Resume Text:
# {state['text']}
# """
#     response = llm_clarity.invoke(prompt).content
#     return {'clarity': response}


# ################################ skills ############################################################

# def skills(state: Analyzer) -> Analyzer:
#     prompt = f"""You are a senior technical interviewer.

# TASK: Evaluate the TECHNICAL SKILLS presented in the following resume text.

# SKILLS CRITERIA:
# - Relevance of skills to modern software/AI roles
# - Evidence of practical application
# - Balance between fundamentals and tools
# - Missing or weak skill areas

# INSTRUCTIONS:
# - Ignore formatting and writing style.
# - Focus ONLY on technical skills and experience.
# - Be realistic and industry-oriented.

# OUTPUT:
# - One short assessment of skill strength
# - One recommendation to improve technical profile

# Resume Text:
# {state['text']}
# """
#     response = llm.invoke(prompt).content
#     return {'skills': response}


# ######################################### feedback generator #############################################

# def feedback_generator(state: Analyzer) -> Analyzer:
#     prompt = f"""You are a senior professional reviewer and feedback synthesizer.

# Your task is to generate a clear, structured feedback summary of a resume based on multiple independent evaluations.
# The goal is to produce feedback that allows any subsequent AI model to fully understand the resume's strengths, 
# weaknesses, and overall quality WITHOUT seeing the original resume.

# INPUTS:
# - Format Evaluation: {state['formatting']}
# - Clarity Evaluation: {state['clarity']}
# - Skills Evaluation: {state['skills']}

# INSTRUCTIONS:
# - Synthesize all inputs into one coherent assessment.
# - Do NOT repeat the inputs verbatim.
# - Resolve overlaps or contradictions logically.
# - Be precise, professional, and neutral.
# - Avoid vague language.
# - Do not exaggerate strengths or weaknesses.

# OUTPUT STRUCTURE (follow strictly):

# 1. OVERALL SUMMARY
#    A concise paragraph describing the resume's overall quality and readiness.

# 2. STRUCTURE & PRESENTATION
#    Clear assessment of formatting, organization, and visual clarity.

# 3. COMMUNICATION & CLARITY
#    Assessment of writing clarity, specificity, and readability.

# 4. TECHNICAL & PROFESSIONAL SKILLS
#    Assessment of skill depth, relevance, and practical experience.

# 5. KEY STRENGTHS
#    Bullet list of the most important strengths (max 4).

# 6. KEY GAPS / IMPROVEMENT AREAS
#    Bullet list of the most important gaps or weaknesses (max 4).

# 7. RECOMMENDED NEXT ACTIONS
#    2–3 concrete, actionable recommendations to improve the resume.

# QUALITY CHECK (apply silently before answering):
# - Would a senior recruiter understand this resume clearly from this feedback alone?
# - Does each section add distinct value?
# - Is the feedback balanced and realistic?

# OUTPUT: Provide only the structured feedback. Do not add explanations or meta-comments.
# """
#     response = llm_eval.invoke(prompt).content
#     return {'feedback': response}


# ######################################### score generator #############################################

# def score_generator(state: Analyzer, config: RunnableConfig, store: BaseStore) -> Analyzer:
#     user_id = state['user_id']
#     namespace = ('user_id', user_id)

#     items = store.search(namespace)

#     if items:
#         user_details = "\n".join(it.value["data"] for it in items)
#     else:
#         user_details = "(empty)"
    
#     system_prompt = create_system_prompt(state['feedback'], user_details)
    
#     # Create structured output with the system prompt as a user message
#     structured_output = llm_eval.with_structured_output(StructuredScore)
#     response = structured_output.invoke(system_prompt)
    
#     return {
#         'score': response.score,
#         'justification': response.justification,
#         'suggested_fixes': response.key_fixes_required
#     }


# # Creating the graph
# graph = StateGraph(Analyzer)

# # Adding nodes to the graph
# graph.add_node('remember_node', remember_node)
# graph.add_node('text_loading', text_loading)
# graph.add_node('formatting', formatting)
# graph.add_node('clarity', clarity)
# graph.add_node('skills', skills)
# graph.add_node('feedback_generator', feedback_generator)
# graph.add_node('score_generator', score_generator)

# # Connecting the nodes
# graph.add_edge(START, 'text_loading')
# graph.add_edge('text_loading', 'formatting')
# graph.add_edge('text_loading', 'clarity')
# graph.add_edge('text_loading', 'skills')
# graph.add_edge('formatting', 'feedback_generator')
# graph.add_edge('clarity', 'feedback_generator')
# graph.add_edge('skills', 'feedback_generator')
# graph.add_edge('feedback_generator', 'score_generator')
# graph.add_edge('score_generator', 'remember_node')
# graph.add_edge('remember_node', END)

# workflow = graph.compile(store=store)