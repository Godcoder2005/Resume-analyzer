"""
LangGraph nodes for Resume Analyzer workflow
Contains all node functions for the analysis pipeline
"""

import uuid
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage
from langgraph.store.memory import BaseStore

from schemas import Analyzer, MemoryOutput
from config import (
    llm_formatting, 
    llm_clarity, 
    llm_eval, 
    llm_memory_read
)
from prompts import (
    MEMORY_PROMPT,
    FORMAT_EVALUATION_PROMPT,
    CLARITY_EVALUATION_PROMPT,
    SKILLS_EVALUATION_PROMPT,
    FEEDBACK_SYNTHESIS_PROMPT,
    create_scoring_prompt
)
from utils import extract_text_from_file


# Initialize memory output parser
memory_output = llm_memory_read.with_structured_output(MemoryOutput)


def text_loading_node(state: Analyzer) -> Analyzer:
    """
    Load and extract text from the uploaded resume file
    """
    try:
        text = extract_text_from_file(state['pdf_path'])
        return {'text': text}
    except Exception as e:
        return {'text': f"ERROR: {str(e)}"}


def formatting_node(state: Analyzer) -> Analyzer:
    """
    Evaluate the formatting and structure of the resume
    """
    prompt = FORMAT_EVALUATION_PROMPT.format(resume_text=state['text'])
    response = llm_formatting.invoke(prompt).content
    return {'formatting': response}


def clarity_node(state: Analyzer) -> Analyzer:
    """
    Evaluate the clarity and readability of the resume
    """
    prompt = CLARITY_EVALUATION_PROMPT.format(resume_text=state['text'])
    response = llm_clarity.invoke(prompt).content
    return {'clarity': response}


def skills_node(state: Analyzer) -> Analyzer:
    """
    Evaluate the technical skills and experience in the resume
    """
    prompt = SKILLS_EVALUATION_PROMPT.format(resume_text=state['text'])
    response = llm_formatting.invoke(prompt).content  # Using llm_formatting here
    return {'skills': response}


def feedback_generator_node(state: Analyzer) -> Analyzer:
    """
    Synthesize all evaluations into comprehensive feedback
    """
    prompt = FEEDBACK_SYNTHESIS_PROMPT.format(
        formatting=state['formatting'],
        clarity=state['clarity'],
        skills=state['skills']
    )
    response = llm_eval.invoke(prompt).content
    return {'feedback': response}


def score_generator_node(state: Analyzer, config: RunnableConfig, store: BaseStore) -> Analyzer:
    """
    Generate final score and justification based on feedback and historical memory
    """
    from schemas import StructuredScore
    
    user_id = state['user_id']
    namespace = ('user_id', user_id)

    # Retrieve historical memory
    items = store.search(namespace)
    user_details = "\n".join(it.value["data"] for it in items) if items else "(empty)"
    
    # Create scoring prompt with feedback and memory
    prompt = create_scoring_prompt(state['feedback'], user_details)
    
    # Get structured output
    structured_output = llm_eval.with_structured_output(StructuredScore)
    response = structured_output.invoke(prompt)
    
    return {
        'score': response.score,
        'justification': response.justification,
        'suggested_fixes': response.key_fixes_required
    }


def remember_node(state: Analyzer, config: RunnableConfig, store: BaseStore) -> Analyzer:
    """
    Store relevant long-term memory about the user's resume patterns
    """
    user_id = state['user_id']
    namespace = ('user_id', user_id)
    
    # Get existing memory
    items = store.search(namespace)
    existing = "\n".join(it.value["data"] for it in items) if items else "(empty)"

    # Analyze what should be remembered
    result = memory_output.invoke([
        SystemMessage(content=MEMORY_PROMPT.format(user_details_content=existing)),
        {'role': 'user', 'content': state['feedback']}
    ])

    # Store new memories
    if result.should_write:
        for mem in result.memories:
            if mem.is_there:
                store.put(namespace, str(uuid.uuid4()), {'data': mem.text})

    return state