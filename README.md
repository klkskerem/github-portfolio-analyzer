# GitHub Portfolio & Tech Stack Analyzer

An automated, two-stage LLM pipeline and CLI tool designed to audit GitHub developer profiles, filter software repositories using structured JSON schemas, and synthesize an executive-level engineering portfolio report with real-time terminal streaming.

Powered by **Gemini (**`gemini-3.1-flash-lite`**)** via OpenAI-compatible endpoints.

---

## Architecture & Pipeline Flow

```text
GitHub Profile (?tab=repositories)
           │
           ▼
┌─────────────────────────┐
│    Rule-based Scraper   │  Scrapes anchor tags and raw repository links
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Stage 1: LLM Filter    │  Enforces JSON schema output
│ (gemini-3.1-flash-lite) │  Discards non-project links (stars, issues, followers)
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│     Data Aggregator     │  Fetches individual README files
│  (Budget Token Control) │  Truncates per-repo text (1,200 chars/repo)
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Stage 2: Tech Lead LLM │  Senior Tech Lead persona evaluates architecture,
│ (gemini-3.1-flash-lite) │  modularity, and cross-platform tech stack
└──────────┬──────────────┘
           │
           ▼
   Terminal Output (Real-time HTTP Stream / Daktilo Effect)
```

---



## Key Engineering Features

- **Two-Stage LLM Chaining:** Decouples repository classification from technical analysis to optimize prompt focus and eliminate hallucinations.
- **Deterministic JSON Output:** Utilizes `response_format={"type": "json_object"}` in Stage 1 to guarantee structured, machine-readable data parsing.
- **Token Budget Optimization:** Enforces strict truncation boundaries (`1,200` characters per repository, `6,000` total prompt limit) to minimize latency and API costs.
- **Real-time UX via Streaming:** Implements Server-Sent Events (`stream=True`) with unbuffered output (`flush=True`) in the terminal for near-zero Time to First Token (TTFT).

---



## Tech Stack

- **Language:** Python 3.12+
- **LLM Engine:** Google Gemini (`gemini-3.1-flash-lite`)
- **SDK / API Integration:** OpenAI Python SDK (via Google Generative Language OpenAI-compatible endpoint)
- **Web Scraping:** BeautifulSoup4, Requests
- **Environment & Security:** `python-dotenv`

---



## Getting Started



### 1. Prerequisites & Installation

Clone the repository and set up a virtual environment:

```bash
git clone [https://github.com/klkskerem/github-portfolio-analyzer.git](https://github.com/klkskerem/github-portfolio-analyzer.git)
cd github-portfolio-analyzer
python -m venv .venv
```

Activate the virtual environment:

- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```



### 2. Environment Setup

Create a `.env` file in the root directory (refer to `.env.example`):

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---



## Usage

Run the analyzer directly from your terminal:

```bash
# Run with default profile
python main.py

# Analyze any public GitHub profile
python main.py --username klkskerem --name Kerem

# Analyze other developers
python main.py --username torvalds --name Linus
```

---



## Generated Report Structure

The final analysis stream generates a standardized 4-part technical report:

1. **Executive Summary:** Core technical profile, specialization, and engineering focus.
2. **Featured Projects:** Project breakdown, architectural roles, and inferred implementations.
3. **Tech Stack Matrix:** Markdown matrix classifying Languages, Frameworks, Backend/APIs, and Workflows.
4. **Engineering Strengths:** In-depth evaluation of design patterns (e.g., BFF, Modularity, Separation of Concerns).

