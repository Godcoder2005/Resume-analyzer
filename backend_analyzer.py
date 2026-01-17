from langgraph.graph import END, START, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_huggingface import HuggingFaceEndpoint
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPDFLoader

load_dotenv()

################################## All llm models ########################################################

# llm model for formatting
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# llm model - for evaluation
llm_eval = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# llm model - for clarity
llm_clarity = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',  # Fixed: changed from 'gemini-2.5-flash' which doesn't exist
    temperature=0.7
)

################### All States and pydantic one will be used for structured output ##################

class Analyzer(TypedDict):
    text: str
    formatting: str
    clarity: str
    skills: str
    score: float
    suggested_fixes: str
    pdf_path: str
    feedback: str
    justification: str


# Pydantic class for proper structured output
class StructuredScore(BaseModel):
    score: float = Field(..., ge=0, le=10)
    justification: str = Field(..., description="Explanation for the score")
    key_fixes_required: str = Field(..., description="The suggestions used to fix the resume")


# Loading text from resume
def extract_text_from_file(path: str) -> str:
    with open(path, "rb") as f:
        header = f.read(20)

    # ---------- PDF ----------
    if header.startswith(b"%PDF"):
        try:
            loader = PyPDFLoader(path)
            pages = loader.load()
            return "\n".join(p.page_content for p in pages)
        except Exception:
            # fallback only for REAL PDFs
            import pypdf
            reader = pypdf.PdfReader(path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)

    # ---------- DOCX ----------
    elif header.startswith(b"PK"):
        from langchain_community.document_loaders import Docx2txtLoader
        pages = Docx2txtLoader(path).load()
        return "\n".join(p.page_content for p in pages)

    # ---------- HTML ----------
    elif b"<html" in header.lower():
        from langchain_community.document_loaders import BSHTMLLoader
        pages = BSHTMLLoader(path).load()
        return "\n".join(p.page_content for p in pages)

    else:
        raise ValueError("Unsupported or corrupted resume file")



######################################### loading text #############################################

def text_loading(state: Analyzer) -> Analyzer:
    try:
        text = extract_text_from_file(state['pdf_path'])
        return {'text': text}
    except Exception as e:
        return {'text': f"ERROR: {str(e)}"}


######################################### formatting #############################################

def formatting(state: Analyzer) -> Analyzer:
    prompt = f"""You are a strict professional resume reviewer.

TASK: Evaluate the FORMAT of the following resume text.

FORMAT CRITERIA:
- Clear section headings
- Logical ordering of sections
- Consistent bullet points
- Readable spacing and structure
- No unnecessary symbols or visual clutter

INSTRUCTIONS:
- Do NOT evaluate content quality or skills.
- Focus ONLY on structure and formatting.
- Be concise and objective.

OUTPUT:
- One short paragraph describing format quality
- One clear improvement suggestion (if any)

Resume Text:
{state['text']}
"""
    response = llm.invoke(prompt).content
    return {'formatting': response}


######################################### clarity #############################################

def clarity(state: Analyzer) -> Analyzer:
    prompt = f"""You are a professional technical communication reviewer.

TASK: Evaluate the CLARITY of the following resume text.

CLARITY CRITERIA:
- Sentences are clear and easy to understand
- Bullet points convey one idea at a time
- No vague or generic statements
- Action-oriented and specific language

INSTRUCTIONS:
- Do NOT judge formatting or skill relevance.
- Focus ONLY on clarity and readability.
- Be precise and professional.

OUTPUT:
- One short paragraph on clarity
- One concrete suggestion to improve clarity

Resume Text:
{state['text']}
"""
    response = llm_clarity.invoke(prompt).content  # Fixed: added .content to extract text
    return {'clarity': response}


################################ skills ############################################################

def skills(state: Analyzer) -> Analyzer:
    prompt = f"""You are a senior technical interviewer.

TASK: Evaluate the TECHNICAL SKILLS presented in the following resume text.

SKILLS CRITERIA:
- Relevance of skills to modern software/AI roles
- Evidence of practical application
- Balance between fundamentals and tools
- Missing or weak skill areas

INSTRUCTIONS:
- Ignore formatting and writing style.
- Focus ONLY on technical skills and experience.
- Be realistic and industry-oriented.

OUTPUT:
- One short assessment of skill strength
- One recommendation to improve technical profile

Resume Text:
{state['text']}
"""
    response = llm.invoke(prompt).content
    return {'skills': response}


######################################### feedback generator #############################################

def feedback_generator(state: Analyzer) -> Analyzer:
    prompt = f"""You are a senior professional reviewer and feedback synthesizer.

Your task is to generate a clear, structured feedback summary of a resume based on multiple independent evaluations.
The goal is to produce feedback that allows any subsequent AI model to fully understand the resume's strengths, 
weaknesses, and overall quality WITHOUT seeing the original resume.

INPUTS:
- Format Evaluation: {state['formatting']}
- Clarity Evaluation: {state['clarity']}
- Skills Evaluation: {state['skills']}

INSTRUCTIONS:
- Synthesize all inputs into one coherent assessment.
- Do NOT repeat the inputs verbatim.
- Resolve overlaps or contradictions logically.
- Be precise, professional, and neutral.
- Avoid vague language.
- Do not exaggerate strengths or weaknesses.

OUTPUT STRUCTURE (follow strictly):

1. OVERALL SUMMARY
   A concise paragraph describing the resume's overall quality and readiness.

2. STRUCTURE & PRESENTATION
   Clear assessment of formatting, organization, and visual clarity.

3. COMMUNICATION & CLARITY
   Assessment of writing clarity, specificity, and readability.

4. TECHNICAL & PROFESSIONAL SKILLS
   Assessment of skill depth, relevance, and practical experience.

5. KEY STRENGTHS
   Bullet list of the most important strengths (max 4).

6. KEY GAPS / IMPROVEMENT AREAS
   Bullet list of the most important gaps or weaknesses (max 4).

7. RECOMMENDED NEXT ACTIONS
   2–3 concrete, actionable recommendations to improve the resume.

QUALITY CHECK (apply silently before answering):
- Would a senior recruiter understand this resume clearly from this feedback alone?
- Does each section add distinct value?
- Is the feedback balanced and realistic?

OUTPUT: Provide only the structured feedback. Do not add explanations or meta-comments.
"""
    response = llm_eval.invoke(prompt).content
    return {'feedback': response}


######################################### score generator #############################################

def score_generator(state: Analyzer) -> Analyzer:
    prompt = f"""You are a strict, unbiased professional resume evaluator.

Your task is to assess a resume ONLY based on the provided feedback summary.
You do NOT have access to the original resume and must not assume anything beyond the feedback.

INPUT:
Resume Feedback Summary:
{state['feedback']}

EVALUATION RULES:
- Score the resume on a scale of 0 to 10.
- A score of 10 represents an excellent, industry-ready resume.
- A score of 5 represents an average resume with notable gaps.
- A score below 4 represents a weak or incomplete resume.
- Be realistic and conservative. Do not inflate scores.

SCORING CRITERIA (use all):
- Structure & presentation quality
- Communication clarity
- Technical and professional skill strength
- Overall readiness for professional roles

OUTPUT FORMAT (follow strictly):

Score: X/10

Justification:
A short paragraph explaining why this score was assigned, referencing structure, clarity, and skills.

Key Fixes Required:
- Bullet list of the most important fixes (max 4).
- Each fix must be concrete and actionable.

QUALITY CHECK (apply silently before answering):
- Would two independent reviewers likely give a similar score?
- Is the justification consistent with the score?
- Are the fixes specific enough to act on immediately?

OUTPUT: Provide only the formatted result. Do not include explanations, disclaimers, or meta-comments.
"""
    structured_output = llm_eval.with_structured_output(StructuredScore)
    response = structured_output.invoke(prompt)
    
    return {
        'score': response.score,
        'justification': response.justification,
        'suggested_fixes': response.key_fixes_required
    }


# Creating the graph
graph = StateGraph(Analyzer)

# Adding nodes to the graph
graph.add_node('text_loading', text_loading)
graph.add_node('formatting', formatting)
graph.add_node('clarity', clarity)
graph.add_node('skills', skills)
graph.add_node('feedback_generator', feedback_generator)
graph.add_node('score_generator', score_generator)

# Connecting the nodes
graph.add_edge(START, 'text_loading')
graph.add_edge('text_loading', 'formatting')
graph.add_edge('text_loading', 'clarity')
graph.add_edge('text_loading', 'skills')
graph.add_edge('formatting', 'feedback_generator')
graph.add_edge('clarity', 'feedback_generator')
graph.add_edge('skills', 'feedback_generator')
graph.add_edge('feedback_generator', 'score_generator')
graph.add_edge('score_generator', END)

workflow = graph.compile()