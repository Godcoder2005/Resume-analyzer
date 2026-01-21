"""
Main workflow definition for Resume Analyzer
Assembles all nodes into a LangGraph workflow
"""

from langgraph.graph import END, START, StateGraph

from schemas import Analyzer
from config import store
from nodes import (
    text_loading_node,
    formatting_node,
    clarity_node,
    skills_node,
    feedback_generator_node,
    score_generator_node,
    remember_node
)


def create_workflow():
    """
    Create and compile the resume analysis workflow
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create the graph
    graph = StateGraph(Analyzer)

    # Add all nodes
    graph.add_node('text_loading', text_loading_node)
    graph.add_node('formatting', formatting_node)
    graph.add_node('clarity', clarity_node)
    graph.add_node('skills', skills_node)
    graph.add_node('feedback_generator', feedback_generator_node)
    graph.add_node('score_generator', score_generator_node)
    graph.add_node('remember', remember_node)

    # Define the workflow edges
    # Start -> Load text
    graph.add_edge(START, 'text_loading')
    
    # Text loading -> Parallel evaluation (formatting, clarity, skills)
    graph.add_edge('text_loading', 'formatting')
    graph.add_edge('text_loading', 'clarity')
    graph.add_edge('text_loading', 'skills')
    
    # All evaluations -> Feedback synthesis
    graph.add_edge('formatting', 'feedback_generator')
    graph.add_edge('clarity', 'feedback_generator')
    graph.add_edge('skills', 'feedback_generator')
    
    # Feedback -> Scoring
    graph.add_edge('feedback_generator', 'score_generator')
    
    # Scoring -> Memory storage
    graph.add_edge('score_generator', 'remember')
    
    # Memory -> End
    graph.add_edge('remember', END)

    # Compile with store
    return graph.compile(store=store)


# Create the workflow instance
workflow = create_workflow()