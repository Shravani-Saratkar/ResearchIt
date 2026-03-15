"""AI Research Assistant Page - Self-contained with built-in styling"""

import streamlit as st
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_papers():
    """Validate papers exist and are accessible"""
    try:
        papers = st.session_state.get("papers", [])
        return bool(papers and isinstance(papers, list))
    except Exception as e:
        logger.error(f"Paper validation error: {e}")
        return False


def get_paper_context():
    """Extract context from papers for AI responses"""
    try:
        papers = st.session_state.get("papers", [])
        context = {
            "paper_count": len(papers),
            "topics": list(set(p.get("topic", "Unknown") for p in papers)),
            "authors": list(set(a for p in papers for a in p.get("authors", []))),
            "years": sorted(set(p.get("year") for p in papers if p.get("year")))
        }
        return context
    except Exception as e:
        logger.error(f"Error extracting context: {e}")
        return {}


def _build_paper_context_text(papers_data: List[Dict], max_papers: int = 20) -> str:
    """Build a concise text block of all papers for the AI prompt."""
    lines = []
    for i, p in enumerate(papers_data[:max_papers], 1):
        title    = p.get("title", "Untitled").strip()
        authors  = ", ".join(p.get("authors", [])[:3])
        year     = p.get("year", "n.d.")
        abstract = (p.get("abstract") or p.get("summary") or "")[:300].replace("\n", " ")
        lines.append(f"[Paper {i}] {title} ({authors}, {year})\n{abstract}")
    return "\n\n".join(lines)


def generate_ai_response(user_message: str, chat_history: List[Dict], papers_data: List) -> str:
    """Call Gemini with full paper context and conversation history."""
    import os
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ("⚠️ GEMINI_API_KEY not set. Please add it to your .env file.")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        paper_ctx = _build_paper_context_text(papers_data)

        # Last 6 turns of conversation history for context
        history_lines = []
        for msg in chat_history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_lines.append(f"{role}: {msg['content']}")
        history_str = "\n".join(history_lines)

        prompt = f"""You are an expert AI research assistant with access to the following research papers.
Answer the user's question accurately based on these papers.

--- PAPER COLLECTION ({len(papers_data)} papers) ---
{paper_ctx}

--- CONVERSATION HISTORY ---
{history_str}

--- USER QUESTION ---
{user_message}

Instructions:
- Answer based on the papers above whenever possible.
- Cite paper titles or authors when relevant.
- If the question cannot be answered from the papers, say so and give a general answer.
- Use clear, academic but accessible language.
- Structure longer answers with short paragraphs or bullet points.
"""
        response = model.generate_content(prompt)
        return (response.text or "").strip() or "I was unable to generate a response. Please try again."

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"⚠️ Error contacting Gemini: {e}"


def get_suggested_questions():
    """Generate contextual suggested questions based on papers"""
    base_suggestions = [
        "What are the main research methodologies used?",
        "What datasets are commonly mentioned?",
        "What are the key findings across these papers?",
        "What are the main limitations discussed?",
        "Who are the most frequently cited authors?",
        "What are the emerging trends in this field?",
        "How do the papers relate to each other?",
        "What future research directions are suggested?",
    ]
    return base_suggestions


def export_conversation(chat_history: List[Dict], format: str = "txt") -> str:
    """Export chat conversation in various formats"""
    try:
        if format == "markdown":
            content = "# Research Assistant Conversation\n\n"
            content += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            
            for msg in chat_history:
                role = "**You**" if msg["role"] == "user" else "**🤖 AI Assistant**"
                content += f"{role}\n\n{msg['content']}\n\n---\n\n"
        
        else:  # Plain text
            content = f"RESEARCH ASSISTANT CONVERSATION\n{'='*50}\n"
            content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for msg in chat_history:
                role = "YOU" if msg["role"] == "user" else "AI ASSISTANT"
                content += f"{role}\n{'-'*30}\n{msg['content']}\n\n"
        
        return content
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        return ""


def page_header(title, subtitle, icon="📄"):
    """Render a page header"""
    st.markdown(f"""
    <div style="padding: 20px 0 30px 0;">
        <h1 style="font-size: 40px; font-weight: 800; color: #F5F5F0; margin: 0 0 8px 0; letter-spacing: -0.02em;">
            {icon} {title}
        </h1>
        <p style="font-size: 16px; color: #C0C0C0; margin: 0; line-height: 1.6;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, icon="📋"):
    """Render a section header"""
    st.markdown(f"""
    <div style="padding: 20px 0 15px 0;">
        <h2 style="font-size: 24px; font-weight: 700; color: #F5F5F0; margin: 0; letter-spacing: -0.01em;">
            {icon} {title}
        </h2>
    </div>
    """, unsafe_allow_html=True)


def card_start(padding="24px"):
    """Start a card container"""
    st.markdown(f"""
    <div style="background: #2A2A2A; border: 1px solid #3A3A3A; border-radius: 12px; padding: {padding}; margin-bottom: 20px;">
    """, unsafe_allow_html=True)


def card_end():
    """End a card container"""
    st.markdown("</div>", unsafe_allow_html=True)


def metric_card(value, label, icon=""):
    """Create a metric card HTML"""
    return f"""
    <div style="background: linear-gradient(135deg, rgba(85, 107, 47, 0.08), rgba(85, 107, 47, 0.03)); border: 1px solid #e8ebe3; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(45, 59, 47, 0.04);">
        <div style="font-size: 32px; font-weight: 800; color: #F5F5F0; margin-bottom: 8px;">
            {icon} {value}
        </div>
        <div style="font-size: 13px; color: #C0C0C0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
            {label}
        </div>
    </div>
    """


def spacing(pixels=10):
    """Add vertical spacing"""
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html=True)


def render_message_card(content: str, role: str = "assistant"):
    """Render a message card with enhanced styling"""
    if role == "user":
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(85, 107, 47, 0.12), rgba(85, 107, 47, 0.06)); border-left: 4px solid #D4AF37; border-radius: 12px; padding: 18px 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(45, 59, 47, 0.08);">
            <div style="font-size: 12px; font-weight: 700; color: #D4AF37; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                You
            </div>
            <div style="color: #F5F5F0; font-size: 15px; line-height: 1.6; word-wrap: break-word;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:  # AI message
        st.markdown(f"""
        <div style="background: #2A2A2A; border: 1px solid #3A3A3A;
        border-radius: 12px; padding: 18px 24px; margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);">

            <div style="font-size: 12px; font-weight: 700;
            color: #D4AF37; text-transform: uppercase;
            letter-spacing: 0.08em; margin-bottom: 8px;">
                🤖 AI Assistant
            </div>

            <div style="color: #F5F5F0;
            font-size: 15px;
            line-height: 1.8;
            word-wrap: break-word;">
                {content}
            </div>

        </div>
        """, unsafe_allow_html=True)


def render_assistant_page():
    """Main page renderer for AI research assistant"""
    
    page_header(
        "AI Research Assistant",
        "Ask questions about your paper collection and get instant answers",
        "💬"
    )

    # Check if papers exist
    if not validate_papers():
        card_start()
        st.warning("⚠️ Please fetch papers from the Discover page to use the AI assistant.")
        card_end()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Go to Discover", use_container_width=True, type="primary"):
                st.session_state.current_page = "discover"
                st.rerun()
        with col2:
            if st.button("📚 Browse Papers", use_container_width=True):
                st.session_state.current_page = "library"
                st.rerun()
        return

    # Initialize chat history if needed
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False

    # Get paper context
    paper_context = get_paper_context()
    
    # Display conversation or empty state
    if st.session_state.chat_history:
        st.session_state.conversation_started = True
        
        # Conversation stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(metric_card(str(len(st.session_state.chat_history) // 2), "Messages Exchanged", "💬"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(metric_card(str(paper_context.get("paper_count", 0)), "Source Papers", "📚"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(metric_card(str(len(paper_context.get("authors", []))), "Unique Authors", "👥"), unsafe_allow_html=True)
        
        spacing(20)
        section_header("Conversation", "💬")
        
        # Display chat messages
        for msg in st.session_state.chat_history:
            render_message_card(msg["content"], msg["role"])
    
    else:
        # Empty state with enhanced suggestions
        card_start()
        
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 56px; margin-bottom: 16px; opacity: 0.5;">💬</div>
            <h3 style="font-size: 24px; font-weight: 700; color: #F5F5F0; margin: 0 0 8px 0;">
                Start Your Research Conversation
            </h3>
            <p style="font-size: 15px; color: #C0C0C0; margin: 0; line-height: 1.6;">
                Ask questions about methodologies, findings, trends, or connections within your paper collection.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        spacing(20)
        
        # Paper context info
        st.markdown("""
        <div style="font-size: 14px; font-weight: 600; color: #C0C0C0; margin-bottom: 12px;">
            📊 Collection Overview:
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Papers", paper_context.get("paper_count", 0))
        
        with col2:
            st.metric("Authors", len(paper_context.get("authors", [])))
        
        with col3:
            years = paper_context.get("years", [])
            year_span = f"{min(years)}-{max(years)}" if years else "N/A"
            st.metric("Year Range", year_span)
        
        spacing(20)
        
        st.markdown("""
        <div style="font-size: 14px; font-weight: 600; color: #C0C0C0; margin-bottom: 12px;">
            💡 Suggested Questions:
        </div>
        """, unsafe_allow_html=True)
        
        suggestions = get_suggested_questions()
        
        for i, suggestion in enumerate(suggestions[:4], 1):
            if st.button(f"💬 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": suggestion})
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": generate_ai_response(suggestion, st.session_state.chat_history, st.session_state.get("papers", []))
                })
                st.rerun()
        
        card_end()

    # Input area with enhanced features
    spacing(20)
    
    
    
    st.markdown("""
    <div style="font-size: 14px; font-weight: 600; color: #C0C0C0; margin-bottom: 12px;">
        Message
    </div>
    """, unsafe_allow_html=True)
    
    # Clear the input BEFORE the widget is rendered (Streamlit requires this order)
    if st.session_state.pop("_clear_chat_input", False):
        st.session_state["chat_input"] = ""

    col1, col2 = st.columns([5, 1])

    with col1:
        user_input = st.text_input(
            "Ask your question",
            placeholder="Ask about methodologies, findings, trends, or paper connections...",
            label_visibility="collapsed",
            key="chat_input"
        )

    with col2:
        spacing(5)
        send = st.button("🚀", use_container_width=True, help="Send message", key="send_btn")

    

    # Handle message sending
    if send and user_input:
        try:
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            papers_data = st.session_state.get("papers", [])
            ai_response = generate_ai_response(user_input, st.session_state.chat_history, papers_data)

            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

            # Set flag so the NEXT rerun clears the box before the widget is created
            st.session_state["_clear_chat_input"] = True
            st.rerun()

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            st.error("❌ Error processing your message. Please try again.")

    # Action buttons for conversation
    if st.session_state.chat_history:
        spacing(15)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📋 Export as Text", use_container_width=True):
                try:
                    export_content = export_conversation(st.session_state.chat_history, "txt")
                    st.download_button(
                        "⬇️ Download Text",
                        export_content,
                        file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                except Exception as e:
                    logger.error(f"Error exporting: {e}")
                    st.warning("Could not export conversation")
        
        with col2:
            if st.button("📄 Export as Markdown", use_container_width=True):
                try:
                    export_content = export_conversation(st.session_state.chat_history, "markdown")
                    st.download_button(
                        "⬇️ Download Markdown",
                        export_content,
                        file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                except Exception as e:
                    logger.error(f"Error exporting: {e}")
                    st.warning("Could not export conversation")
        
        with col3:
            if st.button("🔄 New Conversation", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.conversation_started = False
                st.rerun()
        
        with col4:
            if st.button("🗑️ Clear All", use_container_width=True):
                if st.session_state.get("confirm_clear"):
                    st.session_state.chat_history = []
                    st.session_state.conversation_started = False
                    st.session_state.confirm_clear = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("⚠️ Click again to confirm deletion")


if __name__ == "__main__":
    render_assistant_page()