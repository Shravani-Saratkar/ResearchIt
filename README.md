# 🔬 ResearchIt v2.0 - AI-Powered Research Intelligence Platform

A modern, dark-themed research intelligence platform with advanced features for academic paper discovery, gap detection, and proposal generation.

## ✨ Features

### 🔍 **Paper Discovery**
- Multi-source paper search (ArXiv)
- Advanced filtering and sorting
- Real-time statistics
- Beautiful visualizations

### 📊 **Analytics Dashboard**
- Publication trend analysis
- Author collaboration networks
- Keyword extraction
- Interactive charts and graphs

### 🎯 **Gap Detection**
- AI-powered gap identification
- Research summary generation
- Future topic prediction
- Systematic gap analysis framework

### 📝 **Proposal Generator** (Coming Soon)
- Auto-generate research proposals
- Multiple export formats
- Citation formatting
- Budget and timeline estimation

### 💬 **AI Assistant**
- Interactive Q&A about papers
- Contextual understanding
- Suggested questions
- Conversation history

## 🚀 Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd researchit_v2
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

To get a Gemini API key:
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and paste it into your .env file

### 4. Run the application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
researchit_v2/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── components/            # Reusable UI components
│   ├── __init__.py
│   ├── sidebar.py         # Navigation sidebar
│   └── theme.py           # Dark theme styling
│
├── pages/                 # Application pages
│   ├── __init__.py
│   ├── discover.py        # Paper discovery page
│   ├── analytics.py       # Analytics and visualizations
│   ├── gaps.py            # Gap detection page
│   ├── proposal.py        # Proposal generator page
│   └── assistant.py       # AI assistant chatbot
│
├── services/              # Backend services
│   ├── __init__.py
│   └── simple_rag.py      # RAG system for AI analysis
│
└── utils/                 # Utility functions
    └── __init__.py
```

## 🎨 UI Features

### Modern Dark Theme
- Glassmorphism effects
- Gradient accents
- Smooth animations
- Responsive design

### Key Design Elements
- ✅ Dark gradient background
- ✅ Glass-morphic cards with backdrop blur
- ✅ Neon-style gradient buttons
- ✅ Smooth hover transitions
- ✅ Custom scrollbars
- ✅ Modern typography (Inter font)

## 💡 Usage Guide

### 1. Discover Papers
1. Navigate to "Discover Papers" from the sidebar
2. Enter your research topic (e.g., "machine learning")
3. Set the number of papers to fetch (5-100)
4. Click "Search Papers"
5. Browse, filter, and sort results

### 2. View Analytics
1. After fetching papers, go to "Analytics"
2. Explore tabs:
   - **Trends**: Publication timeline
   - **Authors**: Top authors and collaboration metrics
   - **Keywords**: Most common terms
   - **Statistics**: Detailed data table

### 3. Detect Gaps
1. Navigate to "Gap Detection"
2. Choose analysis type:
   - Research Summary
   - Gap Detection
   - Future Topics
3. View AI-generated insights
4. Download results as text files

### 4. Chat with AI Assistant
1. Go to "AI Assistant"
2. Ask questions about your papers
3. Use suggested questions or type your own
4. View conversation history

## 🔧 Configuration

### Customizing the Theme
Edit `components/theme.py` to modify:
- Color schemes
- Gradient effects
- Card styles
- Typography

### Adding New Pages
1. Create a new file in `pages/`
2. Define a `render_<page_name>_page()` function
3. Import it in `app.py`
4. Add navigation in `components/sidebar.py`

## 🚀 Advanced Features (Roadmap)

### Coming Soon:
- ✅ Systematic gap detection with 8 dimensions
- ✅ Full research proposal generation
- ✅ Multi-source integration (PubMed, IEEE, etc.)
- ✅ Citation network visualization
- ✅ PDF full-text analysis
- ✅ Collaboration matchmaking
- ✅ Research impact prediction

## 📝 Environment Variables

Required:
- `GEMINI_API_KEY`: Your Google Gemini API key

Optional:
- `MAX_PAPERS`: Maximum papers to fetch (default: 100)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)

## 🐛 Troubleshooting

### Common Issues:

**1. "GEMINI_API_KEY not found"**
- Make sure you've created a `.env` file
- Verify the API key is correctly formatted
- Restart the Streamlit server after adding the key

**2. Papers not loading**
- Check your internet connection
- ArXiv may be rate-limiting (try fewer papers)
- Try different search terms

**3. Styling not working**
- Clear browser cache
- Make sure `components/theme.py` is loaded
- Check browser console for CSS errors

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for your research!

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
- Paper data from [ArXiv](https://arxiv.org/)
- NLP processing with [BERTopic](https://maartengr.github.io/BERTopic/)

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for the research community**

🔬 ResearchIt v2.0 - Empowering Research Discovery
