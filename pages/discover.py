"""Discover Papers Page - Updated with ArXiv Rate Limiting and Fallback"""

import streamlit as st
from arxiv_helper import fetch_papers
import logging

logger = logging.getLogger(__name__)


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
    st.markdown(f"""
    <div style="background: #2A2A2A; border: 1px solid #3A3A3A; border-radius: 12px; padding: {padding}; margin-bottom: 20px;">
    """, unsafe_allow_html=True)


def card_end():
    """End a card container"""
    st.markdown("</div>", unsafe_allow_html=True)


def spacing(pixels=10):
    """Add vertical spacing"""
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html=True)


def metric_card(value, label, icon=""):
    """Create a metric card HTML"""
    return f"""
    <div style="background: linear-gradient(135deg, rgba(85, 107, 47, 0.08), rgba(85, 107, 47, 0.03)); border: 1px solid #3A3A3A; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 4px rgba(45, 59, 47, 0.04);">
        <div style="font-size: 32px; font-weight: 800; color: #F5F5F0; margin-bottom: 8px;">
            {icon} {value}
        </div>
        <div style="font-size: 13px; color: #C0C0C0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
            {label}
        </div>
    </div>
    """


def render_discover_page():
    """Main page renderer for paper discovery"""
    
    page_header(
        "Discover Papers",
        "Search and fetch research papers from ArXiv",
        "🔍"
    )

    # Initialize session state
    if "papers" not in st.session_state:
        st.session_state.papers = []
    if "papers_fetched" not in st.session_state:
        st.session_state.papers_fetched = False

    # Search section
    section_header("Search Papers", "🔎")
    
    card_start()
    
    st.markdown("""
    <p style="color: #C0C0C0; font-size: 15px; margin-bottom: 16px; line-height: 1.6;">
        Enter keywords to search ArXiv for research papers. Supports multiple keywords.
    </p>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Search Query",
            placeholder="e.g., machine learning, deep learning, artificial intelligence, transformers...",
            label_visibility="collapsed",
            key="search_query"
        )
    
    with col2:
        spacing(8)
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")
    
    spacing(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_results = st.slider(
            "Number of Papers",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            help="How many papers to fetch"
        )
    
    with col2:
        use_sample = st.checkbox(
            "Use Sample Papers",
            value=False,
            help="Use demo papers instead of fetching from ArXiv"
        )
    
    card_end()

    # Handle search
    if search_button and query:
        spacing(20)
        
        with st.spinner("🔄 Fetching papers from ArXiv..."):
            try:
                papers, success, message = fetch_papers(query, max_results=max_results, use_sample=use_sample)
                
                if success:
                    st.session_state.papers = papers
                    st.session_state.papers_fetched = True
                    
                    if "sample" in message.lower():
                        st.warning(f"⚠️ {message}")
                    else:
                        st.success(f"✅ {message}")
                else:
                    st.session_state.papers = papers
                    st.session_state.papers_fetched = True
                    st.warning(f"⚠️ {message}")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Search error: {e}")

    # Display fetched papers
    if st.session_state.papers_fetched and st.session_state.papers:
        spacing(20)
        section_header(f"Papers Found ({len(st.session_state.papers)})", "📚")
        
        # Papers metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(metric_card(str(len(st.session_state.papers)), "Total Papers", "📄"), unsafe_allow_html=True)
        
        with col2:
            years = set(p.get('year', 'Unknown') for p in st.session_state.papers)
            st.markdown(metric_card(str(len(years)), "Years Covered", "📅"), unsafe_allow_html=True)
        
        with col3:
            all_authors = set()
            for p in st.session_state.papers:
                all_authors.update(p.get('authors', []))
            st.markdown(metric_card(str(len(all_authors)), "Unique Authors", "👥"), unsafe_allow_html=True)
        
        spacing(20)
        
        # Display papers in cards
        for idx, paper in enumerate(st.session_state.papers, 1):
            card_start()
            
            # Paper title
            st.markdown(f"""
            <h3 style="font-size: 18px; font-weight: 700; color: #F5F5F0; margin: 0 0 12px 0;">
                {idx}. {paper.get('title', 'Untitled')}
            </h3>
            """, unsafe_allow_html=True)
            
            # Authors
            authors = paper.get('authors', [])
            if authors:
                authors_str = ', '.join(authors[:3])
                if len(authors) > 3:
                    authors_str += f", +{len(authors)-3} more"
                st.markdown(f"""
                <p style="font-size: 13px; color: #C0C0C0; margin: 0 0 8px 0;">
                    <strong>Authors:</strong> {authors_str}
                </p>
                """, unsafe_allow_html=True)
            
            # Year and ArXiv ID
            year = paper.get('year', 'Unknown')
            arxiv_id = paper.get('arxiv_id', '')
            st.markdown(f"""
            <p style="font-size: 13px; color: #C0C0C0; margin: 0 0 12px 0;">
                <strong>Published:</strong> {year} | <strong>ArXiv ID:</strong> {arxiv_id}
            </p>
            """, unsafe_allow_html=True)
            
            # Summary
            summary = paper.get('summary', 'No summary available')[:500]
            if len(paper.get('summary', '')) > 500:
                summary += "..."
            st.markdown(f"""
            <p style="font-size: 14px; color: #F5F5F0; margin: 0; line-height: 1.6;">
                {summary}
            </p>
            """, unsafe_allow_html=True)
            
            spacing(12)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔗 View on ArXiv", key=f"view_{idx}", use_container_width=True):
                    st.markdown(f"[Open on ArXiv]({paper.get('url', '#')})")
            
            with col2:
                st.button(f"💾 Save Paper {idx}", key=f"save_{idx}", use_container_width=True)
            
            with col3:
                st.button(f"📋 Add to Collection {idx}", key=f"add_{idx}", use_container_width=True)
            
            card_end()
            spacing(10)
        
        # Action buttons
        spacing(20)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Confirm Selection", use_container_width=True, type="primary"):
                st.success("✅ Papers added to your collection!")
                st.balloons()
        
        with col2:
            if st.button("🔄 New Search", use_container_width=True):
                st.session_state.papers = []
                st.session_state.papers_fetched = False
                st.rerun()
        
        with col3:
            if st.button("📥 Export Papers", use_container_width=True):
                st.info("📥 Export functionality would be implemented here")
    
    elif st.session_state.papers_fetched and not st.session_state.papers:
        spacing(20)
        card_start()
        st.warning("❌ No papers found. Please try different keywords.")
        card_end()
    
    else:
        spacing(20)
        card_start()
        st.info("""
        ### 📖 How to Use:
        
        1. **Enter Keywords**: Type your search terms (e.g., "machine learning", "AI", "transformers")
        2. **Set Filters**: Choose how many papers to fetch and other options
        3. **Search**: Click the Search button to fetch papers from ArXiv
        4. **Review**: Browse the papers and their summaries
        5. **Confirm**: Click "Confirm Selection" to add to your collection
        
        **Tips:**
        - Use multiple keywords separated by spaces
        - You can try "Use Sample Papers" to test the app without ArXiv
        - Papers are fetched from ArXiv with rate limiting to avoid errors
        """)
        card_end()


if __name__ == "__main__":
    render_discover_page()