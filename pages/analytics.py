"""
Analytics Page - Advanced visualizations and insights
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from datetime import datetime
import pandas as pd

def render_analytics_page():
    """Render analytics and visualizations page"""
    
    # Hero
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">📊 Research Analytics</div>
        <div class="hero-subtitle">
            Deep insights and visualizations from your paper corpus
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.papers_fetched or not st.session_state.papers:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 60px 40px;">
            <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.3;">📊</div>
            <h2 style="color: rgba(255,255,255,0.9); margin-bottom: 16px;">No Data Available</h2>
            <p style="color: rgba(255,255,255,0.6);">
                Please search for papers first in the Discover section.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Go to Discover", use_container_width=True, type="primary"):
            st.session_state.current_page = "discover"
            st.rerun()
        return
    
    papers = st.session_state.papers
    
    # Tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "👥 Authors", "🔤 Keywords", "📊 Statistics"])
    
    with tab1:
        st.markdown("<div class='section-title'>Publication Trends</div>", unsafe_allow_html=True)
        
        # Extract years
        years = []
        for paper in papers:
            if paper.get('published'):
                try:
                    year = datetime.fromisoformat(paper['published'].replace('Z', '+00:00')).year
                    years.append(year)
                except:
                    pass
        
        if years:
            year_counts = Counter(years)
            sorted_years = sorted(year_counts.items())
            
            # Timeline chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[y[0] for y in sorted_years],
                y=[y[1] for y in sorted_years],
                mode='lines+markers',
                line=dict(color='#D4AF37', width=3),
                marker=dict(size=10, color='#FFD700'),
                fill='tozeroy',
                fillcolor='rgba(99, 102, 241, 0.2)'
            ))
            
            fig.update_layout(
                title="Publication Trend Over Time",
                xaxis_title="Year",
                yaxis_title="Number of Publications",
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F5F5F0'),
                xaxis=dict(showgrid=False, color='#F5F5F0'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#F5F5F0')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights
            col1, col2 = st.columns(2)
            with col1:
                peak_year = max(year_counts.items(), key=lambda x: x[1])
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color: #60a5fa; margin-top: 0;">🔥 Peak Year</h4>
                    <p style="font-size: 32px; font-weight: 700; margin: 10px 0;">{peak_year[0]}</p>
                    <p style="color: rgba(255,255,255,0.6);">{peak_year[1]} publications</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                growth = ((sorted_years[-1][1] - sorted_years[0][1]) / sorted_years[0][1] * 100) if len(sorted_years) > 1 else 0
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color: #a78bfa; margin-top: 0;">📈 Growth Rate</h4>
                    <p style="font-size: 32px; font-weight: 700; margin: 10px 0;">{growth:+.1f}%</p>
                    <p style="color: rgba(255,255,255,0.6);">From {sorted_years[0][0]} to {sorted_years[-1][0]}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='section-title'>Author Analysis</div>", unsafe_allow_html=True)
        
        # Author statistics
        all_authors = [author for p in papers for author in p['authors']]
        author_counts = Counter(all_authors)
        top_authors = author_counts.most_common(15)
        
        # Bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=[count for _, count in top_authors],
                y=[author for author, _ in top_authors],
                orientation='h',
                marker=dict(
                    color=[count for _, count in top_authors],
                    colorscale='Viridis',
                    showscale=True
                )
            )
        ])
        
        fig.update_layout(
            title="Top 15 Most Prolific Authors",
            xaxis_title="Number of Papers",
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5F5F0'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#F5F5F0'),
            yaxis=dict(showgrid=False, color='#F5F5F0')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Collaboration metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_authors = sum(len(p['authors']) for p in papers) / len(papers)
            st.metric("Avg Authors per Paper", f"{avg_authors:.1f}")
        with col2:
            unique_authors = len(set(all_authors))
            st.metric("Unique Authors", unique_authors)
        with col3:
            max_authors = max(len(p['authors']) for p in papers)
            st.metric("Max Authors (one paper)", max_authors)
    
    with tab3:
        st.markdown("<div class='section-title'>Keyword Analysis</div>", unsafe_allow_html=True)
        
        # Extract common words from titles
        from collections import defaultdict
        import re
        
        # Simple keyword extraction
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                    'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
                    'using', 'based', 'via'}
        
        word_freq = Counter()
        for paper in papers:
            title = paper['title'].lower()
            words = re.findall(r'\b[a-z]{4,}\b', title)
            for word in words:
                if word not in stopwords:
                    word_freq[word] += 1
        
        top_keywords = word_freq.most_common(20)
        
        # Word cloud style chart
        fig = go.Figure(data=[
            go.Bar(
                x=[word for word, _ in top_keywords],
                y=[count for _, count in top_keywords],
                marker=dict(
                    color=[count for _, count in top_keywords],
                    colorscale='Plasma'
                )
            )
        ])
        
        fig.update_layout(
            title="Top 20 Keywords in Titles",
            xaxis_title="Keyword",
            yaxis_title="Frequency",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#F5F5F0'),
            xaxis=dict(showgrid=False, color='#F5F5F0', tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#F5F5F0')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("<div class='section-title'>Statistical Summary</div>", unsafe_allow_html=True)
        
        # Create DataFrame
        data = []
        for paper in papers:
            year = ""
            if paper.get('published'):
                try:
                    year = datetime.fromisoformat(paper['published'].replace('Z', '+00:00')).year
                except:
                    pass
            
            data.append({
                'Title': paper['title'][:50] + '...' if len(paper['title']) > 50 else paper['title'],
                'Authors': len(paper['authors']),
                'Year': year,
                'First Author': paper['authors'][0] if paper['authors'] else 'Unknown'
            })
        
        df = pd.DataFrame(data)
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Full Dataset (CSV)",
            csv,
            "research_papers.csv",
            "text/csv",
            key='download-analytics-csv'
        )