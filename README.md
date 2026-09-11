# Hiver AI Support Agent

An AI-powered customer support agent that classifies intents, retrieves historical evidence, generates grounded responses, and makes safe escalation decisions. Built for the Hiver SDE Intern Take-Home Assignment.

## 🎯 Headline Results

- **Intent Classification Macro F1:** 98.97%
- **Intent Classification Accuracy:** 98.99%
- **Escalation Decision F1:** 73.26%
- **Escalation Recall:** 100%
- **Reply Quality:** 4.40/5

**Important:** These results are based on real Twitter customer support data from AmazonHelp. However, the evaluation uses heuristically-labeled data (same keyword rules for training and testing), which inflates metrics. See [docs/misleading_headline_number.md](docs/misleading_headline_number.md) for detailed analysis of limitations.

## 🏗️ Architecture

```
hiver/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # FastAPI application
│   │   ├── classifier.py # Intent classifier (TF-IDF + LR)
│   │   ├── retrieval.py  # Historical retrieval (semantic + TF-IDF)
│   │   ├── response_generator.py # Template-based responses
│   │   ├── escalation.py # Escalation policy
│   │   ├── intents.py    # Intent taxonomy
│   │   └── models.py     # Pydantic models
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js frontend
│   ├── app/
│   │   ├── page.tsx      # Home page
│   │   ├── agent/        # Agent interface
│   │   ├── evaluation/   # Evaluation dashboard
│   │   ├── failures/     # Failure analysis
│   │   └── about/        # Methodology
│   └── package.json
├── scripts/              # Data processing and training
│   ├── download_data.py  # Kaggle dataset download
│   ├── analyze_brands.py # Brand analysis
│   ├── prepare_data.py   # Data preprocessing
│   └── train.py          # Model training
├── evaluation/           # Evaluation harness
│   ├── run_evaluation.py # Main evaluation script
│   ├── judge.py          # LLM-as-judge interface
│   └── human_judge_comparison.py # Human-judge agreement
├── golden/               # Golden evaluation set
│   └── golden_200.csv    # 200 hand-labeled examples
├── tests/                # Automated tests
│   ├── test_classifier.py
│   ├── test_escalation.py
│   ├── test_response_generator.py
│   └── test_api.py
├── docs/                 # Documentation
│   ├── misleading_headline_number.md
│   ├── failure_analysis.md
│   └── decision_log.md
├── data/                 # Data directory
│   ├── raw/             # Raw dataset
│   └── processed/       # Processed data
├── models/              # Trained models
└── REPORT.md            # Technical report
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13
- Node.js 18+
- Kaggle API (optional, for dataset download)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Download dataset (optional - can manually download from Kaggle)
python ../scripts/download_data.py

# Analyze brands and select one
python ../scripts/analyze_brands.py

# Prepare data
python ../scripts/prepare_data.py

# Train classifier
python ../scripts/train.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000` and the backend at `http://localhost:8000`.

## 📊 Reproducing Headline Results

To reproduce the evaluation results with real data:

### Step 1: Download Real Dataset

```bash
# Install kagglehub
pip install kagglehub

# Download Customer Support on Twitter dataset
python scripts/download_data_real.py
```

This downloads the real ~2.8M tweet dataset from Kaggle to `data/raw/twcs.csv`.

### Step 2: Prepare Data

```bash
# Analyze brands and select AmazonHelp
python scripts/analyze_brands.py

# Process conversations and create train/dev/test splits
python scripts/prepare_data.py
```

This processes ~4,631 real AmazonHelp conversations into train/dev/test splits.

### Step 3: Create Golden Set

```bash
# Create heuristically-labeled golden set from real conversations
python scripts/create_golden_set.py
```

This creates `golden/golden_200.csv` with 200 real customer messages, stratified across 10 intents.

### Step 4: Train Models

```bash
# Train classifier on real labeled data
python scripts/train_classifier_real.py

# Build retrieval index from real conversations
python scripts/build_retrieval_real.py
```

### Step 5: Run Evaluation

```bash
# Run full evaluation
python evaluation/run_evaluation.py

# View results
cat evaluation/results/evaluation_results.json
```

**Expected runtime:** ~5-10 minutes for full pipeline on modern hardware.

**Important:** The evaluation uses heuristically-labeled data (same keyword rules for training and testing), which inflates metrics. See [docs/misleading_headline_number.md](docs/misleading_headline_number.md) for detailed analysis.

## 🔧 API Endpoints

### Health Check
```bash
GET /health
```

### Metadata
```bash
GET /metadata
```
Returns brand information, intent taxonomy, and system metadata.

### Predict
```bash
POST /predict
Content-Type: application/json

{
  "message": "Where is my order?"
}
```

Returns:
```json
{
  "intent": "order_status",
  "confidence": 0.85,
  "decision": "AUTO_HANDLE",
  "reason": "High confidence with good evidence",
  "reply": "I can help you check your order status...",
  "evidence": [...]
}
```

### Metrics
```bash
GET /metrics
```
Returns evaluation metrics (if evaluation has been run).

### Examples
```bash
GET /examples
```
Returns example messages and their classifications.

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_classifier.py
python tests/test_escalation.py
python tests/test_response_generator.py
python tests/test_api.py
```

## 📈 Evaluation

Run the full evaluation:

```bash
python evaluation/run_evaluation.py
```

This will:
- Load the golden evaluation set (200 examples)
- Evaluate intent classification metrics
- Evaluate escalation decision metrics
- Compare against baselines (majority class, TF-IDF + LR)
- Run LLM-as-judge evaluation
- Save results to `evaluation/results/evaluation_results.json`

## 🚢 Deployment

### Backend (Render)

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use the `render.yaml` configuration (Python 3.12)
4. Deploy

The backend will be available at your Render service URL.

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Use the `vercel.json` configuration
3. Set `NEXT_PUBLIC_API_URL` environment variable to your backend URL (e.g., `https://your-backend.onrender.com`)
4. Deploy

The frontend will be available at your Vercel domain.

### Deployment Notes

- **Python Version:** Render uses Python 3.12 for deployment
- **Dependencies:** All dependencies are pinned in `backend/requirements.txt`
- **Data Storage:** Render disk storage (1GB) is configured for models and data
- **CORS:** Backend allows all origins for development (configure for production)
- **Health Check:** `/health` endpoint is available for monitoring

## 📚 Documentation

- **REPORT.md** - Comprehensive technical report with methodology, results, and analysis
- **docs/misleading_headline_number.md** - Analysis of headline metric limitations
- **docs/failure_analysis.md** - Top 5 failure modes with examples
- **docs/decision_log.md** - 15 key design decisions with rationale

## 🎨 Frontend Pages

- **Home** (`/`) - Navigation to all features
- **Agent** (`/agent`) - Interactive agent interface
- **Evaluation** (`/evaluation`) - Metrics dashboard
- **Failures** (`/failures`) - Failure analysis display
- **About** (`/about`) - Methodology documentation

## 🔬 Intent Taxonomy

1. **order_status** - Order tracking and delivery inquiries
2. **order_issue** - Problems with received orders
3. **refund_request** - Refund and return requests
4. **billing_issue** - Payment and billing problems
5. **account_access** - Login and account access issues
6. **account_issue** - Account settings and updates
7. **product_info** - Product information and availability
8. **general_inquiry** - General questions and policies
9. **complaint** - Customer dissatisfaction and feedback
10. **escalation_required** - Legal threats, security issues, regulatory complaints

## ⚙️ Configuration

### Backend Environment Variables
- `PORT` - Server port (default: 8000)
- `PYTHON_VERSION` - Python version (default: 3.12)

### Frontend Environment Variables
- `NEXT_PUBLIC_API_URL` - Backend API URL

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI
- **Classifier:** TF-IDF + Logistic Regression (scikit-learn)
- **Retrieval:** Sentence-Transformers + FAISS (with TF-IDD fallback)
- **Server:** Uvicorn

### Frontend
- **Framework:** Next.js 14
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **HTTP Client:** Axios

### Data Processing
- **Dataset:** Customer Support on Twitter (Kaggle)
- **Processing:** pandas, numpy
- **Model Persistence:** joblib

## 📝 Key Features

- **Intent Classification:** TF-IDF + Logistic Regression with confidence estimates
- **Historical Retrieval:** Semantic search with sentence-transformers and FAISS
- **Grounded Responses:** Template-based responses grounded in historical evidence
- **Safe Escalation:** Conservative escalation policy with clear reasons
- **Evaluation Harness:** Comprehensive evaluation with baselines and LLM-as-judge
- **No External AI APIs:** All functionality uses open-source libraries
- **Deterministic Operation:** Reproducible results without API dependencies

## ⚠️ Limitations

- **Heuristic Labels:** Training labels and golden set are generated via keyword heuristics, not human-labeled. This creates circular evaluation that inflates metrics. See [docs/misleading_headline_number.md](docs/misleading_headline_number.md) for detailed analysis.
- **Circular Evaluation:** The classifier is tested against data labeled with the same rules it was trained on, inflating performance metrics. Real performance with human labels would likely be 30-40 percentage points lower.
- **Template-based Responses:** No generative AI due to API constraints. Responses use intent-specific templates.
- **Single-turn Conversations:** No conversation history or context tracking.
- **Deterministic Judge:** LLM-as-judge uses deterministic rubric, not a true LLM. No human agreement measurement.
- **Single Brand:** Evaluation uses only AmazonHelp data. May not generalize to other brands.
- **Windows PyTorch Issues:** On Windows development, PyTorch DLL loading errors may occur. The system falls back to TF-IDF retrieval automatically. Deployment on Linux (Render) works correctly with sentence-transformers.
- **Class Imbalance:** Training data is heavily imbalanced (59% general_inquiry), which affects classifier behavior.

## 🤝 Contributing

This is a take-home assignment project. For questions or feedback, please refer to the repository issues.

## 📄 License

This project is for educational purposes as part of the Hiver SDE Intern Take-Home Assignment.

## 📧 Contact

For questions about this assignment, please contact the Hiver team.

---

**Repository:** https://github.com/Sreevalli20/hiver
**Assignment:** Hiver SDE Intern Take-Home Assignment
