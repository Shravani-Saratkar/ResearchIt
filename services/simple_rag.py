import os
import google.generativeai as genai


import streamlit as st

# ------------------------------ #
# 1️⃣ Initialize
# ------------------------------ #
_topic_model = None
_embedding_model = None

API_KEY = os.getenv("GEMINI_API_KEY", None)
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    st.warning("⚠️ GEMINI_API_KEY not found in environment variables.")

# ------------------------------ #
# 2️⃣ Lazy model loader
# ------------------------------ #
def load_models():
    global _topic_model, _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    if _topic_model is None:
        _topic_model = BERTopic(
            embedding_model=_embedding_model,
            min_topic_size=2,
            nr_topics="auto"
        )
    return _topic_model

# ------------------------------ #
# 3️⃣ Gemini summarizer (KEEP AS IS - IT WORKS!)
# ------------------------------ #
def summarize_with_gemini(text, mode):
    prompt = f"""
    You are an expert research assistant.
    Perform this analysis type: {mode}.
    Provide an academic and concise summary in bullet points.

    Text:
    {text}
    """

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini summarization failed: {e}"


# ------------------------------ #
# 4️⃣ Future Topics using BERT + Gemini (FIXED)
# ------------------------------ #
def predict_future_topics(text):
    """Use BERT embeddings + Gemini to predict future research topics - CONCISE"""
    
    try:
        # Extract topics using BERTopic
        documents = [chunk.strip() for chunk in text.split("---") if len(chunk.strip()) > 50]
        
        if len(documents) < 2:
            # If not enough for BERTopic, use Gemini directly
            future_prompt = f"""
            You are an expert research forecaster.
            
            Based on these research papers, predict future research directions.
            
            Papers:
            {text[:3000]}
            
            Format your response EXACTLY like this (keep it brief and actionable):
            
            🎯 KEY FUTURE DIRECTIONS:
            
            1. [Direction Name]: [One clear sentence]
            2. [Direction Name]: [One clear sentence]
            3. [Direction Name]: [One clear sentence]
            4. [Direction Name]: [One clear sentence]
            5. [Direction Name]: [One clear sentence]
            
            💡 TOP 3 EMERGING TECHNOLOGIES:
            • [Technology 1]
            • [Technology 2]
            • [Technology 3]
            
            🔬 TOP 3 UNEXPLORED AREAS:
            • [Area 1]
            • [Area 2]
            • [Area 3]
            
            Keep each point to ONE sentence maximum.
            """
            
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model.generate_content(future_prompt)
            return f"**🚀 Future Research Topics (AI Analysis)**\n\n{response.text}"
        
        # If enough documents, use BERTopic
        topic_model = load_models()
        topics, probs = topic_model.fit_transform(documents)
        topic_info = topic_model.get_topic_info()
        
        # Remove outlier topic (-1) if exists
        topic_info = topic_info[topic_info['Topic'] != -1]
        
        if len(topic_info) == 0:
            # Fallback to Gemini if no topics found
            future_prompt = f"""
            You are an expert research forecaster.
            
            Based on these research papers, predict future research directions.
            
            Papers:
            {text[:3000]}
            
            Format your response EXACTLY like this (keep it brief):
            
            🎯 KEY FUTURE DIRECTIONS:
            
            1. [Direction Name]: [One clear sentence]
            2. [Direction Name]: [One clear sentence]
            3. [Direction Name]: [One clear sentence]
            4. [Direction Name]: [One clear sentence]
            5. [Direction Name]: [One clear sentence]
            
            💡 TOP 3 EMERGING TECHNOLOGIES:
            • [Technology 1]
            • [Technology 2]
            • [Technology 3]
            
            🔬 TOP 3 UNEXPLORED AREAS:
            • [Area 1]
            • [Area 2]
            • [Area 3]
            """
            
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model.generate_content(future_prompt)
            return f"**🚀 Future Research Topics (AI Analysis)**\n\n{response.text}"
        
        # Extract key topics (top 5 or all if less than 5)
        topic_info = topic_info.head(5)
        topic_keywords = []
        
        for idx, row in topic_info.iterrows():
            try:
                words = [word for word, _ in topic_model.get_topic(row['Topic'])[:5]]
                topic_keywords.append(", ".join(words))
            except:
                continue
        
        if len(topic_keywords) == 0:
            topic_keywords = ["general research topics"]
        
        topics_summary = "\n".join([f"- {kw}" for kw in topic_keywords])
        
        # Use Gemini to predict future directions based on identified topics
        future_prompt = f"""
        You are an expert research forecaster.
        
        Based on these research topics identified using BERT:
        {topics_summary}
        
        Format your response EXACTLY like this (keep it brief):
        
        🎯 KEY FUTURE DIRECTIONS:
        
        1. [Direction Name]: [One clear sentence]
        2. [Direction Name]: [One clear sentence]
        3. [Direction Name]: [One clear sentence]
        4. [Direction Name]: [One clear sentence]
        5. [Direction Name]: [One clear sentence]
        
        💡 TOP 3 EMERGING TECHNOLOGIES:
        • [Technology 1]
        • [Technology 2]
        • [Technology 3]
        
        🔬 TOP 3 UNEXPLORED AREAS:
        • [Area 1]
        • [Area 2]
        • [Area 3]
        
        Keep each point to ONE sentence maximum.
        """
        
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(future_prompt)
        
        result = "**🚀 Future Research Topics (BERT + AI Analysis)**\n\n"
        result += f"**📊 Current Research Topics Identified:**\n{topics_summary}\n\n"
        result += "---\n\n"
        result += response.text
        
        return result
        
    except Exception as e:
        # Final fallback - just use Gemini on the text
        try:
            future_prompt = f"""
            Predict future research directions based on these papers (be concise):
            
            {text[:3000]}
            
            Provide:
            🎯 5 KEY FUTURE DIRECTIONS (one sentence each)
            💡 3 EMERGING TECHNOLOGIES
            🔬 3 UNEXPLORED AREAS
            """
            
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model.generate_content(future_prompt)
            return f"**🚀 Future Research Topics**\n\n{response.text}"
        except:
            return f"⚠️ Future topics prediction failed: {e}\n\nTry fetching more papers or different keywords."
        
# ------------------------------ #
# 5️⃣ Unified generator (ONLY 3 COMPONENTS)
# ------------------------------ #
def generate_summary(text, mode):
    """Main function - Only Research Summary, Gap Detection, Future Topics"""
    
    text = text.strip()
    if not text:
        return "⚠️ No text provided."

    # Only 3 modes supported
    if mode == "Future Topics":
        return predict_future_topics(text)
    else:
        # Research Summary and Gap Detection use Gemini
        return summarize_with_gemini(text, mode)