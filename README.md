# 🐍 PyTutor AI — AI Python Code Tutor

An interactive web-based Python tutor built with **Django** for **CSCI 111.13 Final Project**.

Students learn fundamental Python programming across **5 levels**, complete **fill-in-the-blank (missing-line) exercises** with an **in-browser Python compiler (Pyodide)**, and receive **step-by-step guidance from an AI tutor** that works with either **Local LLMs (Ollama / LM Studio)** or **Free Cloud APIs (Google Gemini / Groq / OpenRouter)**.

---

## ✨ Features

- **5 Structured Levels** (1 missing-line exercise per level):
  1. **Level 1 (`print()`)** — Printing Output
  2. **Level 2 (`Variables`)** — Variables and Data Types (`str`, `int`, `float`, `bool`)
  3. **Level 3 (`input()`)** — Getting User Input & `int()` type conversion
  4. **Level 4 (`Conditionals`)** — `if`, `elif`, and `else` statements
  5. **Level 5 (`Loops`)** — `for` loops with `range()` and `while` loops
- **In-Browser Python Compiler (Pyodide):**
  - Runs real Python in the browser inside a Web Worker (with a 5-second timeout to stop infinite loops).
  - Supports `input()` via the **Input** box (one value per line).
- **Constraint-Based Grading + Tutor Flow:**
  - Checks AST rules (`must_call`, `must_use`, `must_assign`) + program output across multiple test inputs, allowing multiple valid solutions.
  - **Minimal Feedback** on the first 1–2 mistakes → **Up to 3 Escalating AI Hints per level** → **Solution Review** (explains the student's mistake, reveals the working code, and marks the level as incorrect) if the student still gets it wrong after all 3 hints.
- **Switchable AI Backend (Online or Local) + Built-in Fallback:**
  - Switch anytime on the **AI Settings** page between **Ollama**, **LM Studio**, **Google Gemini**, **Groq**, **OpenRouter**, or **No AI (built-in hints)**.
- **No Login Required:**
  - Progress, attempt counts, hints used, and typed code are saved automatically in the browser (`localStorage`), with a **↺ Reset Progress** button.

---

## 🚀 1. How to Install and Run the Website

### Prerequisites
- **Python 3.10+** installed on your computer
- Internet connection on the first run (so the browser can load Pyodide and syntax highlighting)

### Step-by-Step Setup

1. **Open a terminal (PowerShell or Command Prompt)** in the project folder:
   ```powershell
   cd AIED-FINAL-PROJECT
   ```

2. **Create and activate a virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations (this also seeds all 5 levels and exercises):**
   ```bash
   python manage.py migrate
   ```
   *(Tip: If you ever edit [`lessons/seed_data.py`](lessons/seed_data.py), run `python manage.py seed_lessons` to update the database.)*

5. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

6. **Open the website in your browser:**
   👉 **http://127.0.0.1:8000**

---

## 🤖 2. Setting Up the AI Tutor (Local vs. Online)

You can configure the AI either through the website's **AI Settings** page (`http://127.0.0.1:8000/settings/`) or by creating a `.env` file on the server.

> **Note:** Even if you don't set up any AI, the website still works 100% using its built-in hints!

---

### Option A: Local AI (Recommended for 8–16 GB RAM & 4 GB+ VRAM)

Running a local model is completely free, private, and requires no API keys.

#### Using Ollama (Default)
1. Download and install **Ollama** from [https://ollama.com/download](https://ollama.com/download).
2. Open a terminal and pull a coding model:
   - **For 8–16 GB RAM + 4 GB+ VRAM (Recommended):**
     ```bash
     ollama pull qwen2.5-coder:7b
     ```
   - **For lower-spec laptops / faster responses:**
     ```bash
     ollama pull qwen2.5-coder:1.5b
     ```
     *(or `ollama pull llama3.2:3b`)*
3. Make sure Ollama is running in the background (`ollama serve` or the Ollama desktop app).
4. On the website, go to **AI Settings** (`http://127.0.0.1:8000/settings/`):
   - **Provider:** `Ollama (local, on this computer)`
   - **Model:** Automatically detects your installed Ollama model (or pick one from the dropdown suggestions)
   - **Server URL:** Leave blank (defaults to `http://localhost:11434/v1`)
   - Click **Test connection** (it will test the model and auto-save).

#### Using LM Studio
1. Download **LM Studio** from [https://lmstudio.ai](https://lmstudio.ai).
2. Download any instruction/coding model (e.g., Qwen 2.5 Coder or Llama 3.2).
3. Go to the **Developer / Local Server** tab in LM Studio, load the model, and click **Start Server** (default port `1234`).
4. On the website, go to **AI Settings**:
   - **Provider:** `LM Studio (local, on this computer)`
   - **Server URL:** Leave blank (defaults to `http://localhost:1234/v1`)
   - Click **Test connection** and **Save**.

---

### Option B: Online Cloud AI (Free Tiers)

If your computer doesn't have enough RAM/VRAM for a local LLM, use any of these free online providers:

| Provider | Default Model | Where to get a Free API Key |
|---|---|---|
| **Google Gemini** | `gemini-2.5-flash` | [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| **Groq** | `llama-3.1-8b-instant` | [https://console.groq.com/keys](https://console.groq.com/keys) |
| **OpenRouter** | `meta-llama/llama-3.3-70b-instruct:free` | [https://openrouter.ai/keys](https://openrouter.ai/keys) |

#### How to connect an Online Provider:
1. Click the link above to create a free API key.
2. On the website, open **AI Settings** (`http://127.0.0.1:8000/settings/`).
3. Select **Google Gemini**, **Groq**, or **OpenRouter** under **Provider**.
4. Paste your **API key** into the API Key box.
5. Click **Test connection** (this verifies your key and saves your settings in your browser).

#### Optional: Server-Wide `.env` Configuration
If you want the server to have a default API key so students don't need to paste one in the browser:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and fill in your preferred provider and key:
   ```env
   DEFAULT_AI_PROVIDER=gemini
   GEMINI_API_KEY=your_api_key_here
   ```
3. Restart `python manage.py runserver`.

---

## 🧑‍🎓 3. How to Use the Website (Student Guide)

1. **Choose a Level:** Start at **Level 1** on the home page. Levels 2–5 unlock sequentially as you finish each level.
2. **Read the Lesson:** The left panel explains how the Python concept works step by step with examples.
3. **Fill in the Missing Lines:** In the `main.py` editor on the right, type only the missing line(s) of code in the highlighted input boxes.
4. **Test with ▶ Run:**
   - Click **▶ Run** (or press `Ctrl+Enter`) to run your code in the browser.
   - If the program uses `input()`, type test values in the **Input** box (one value per line).
5. **Check with ✓ Submit:**
   - Click **✓ Submit** to grade your code against all test cases and constraints.
   - **1st–2nd mistake:** The tutor gives short feedback (syntax line, missing function/loop constraint, or output comparison).
   - **Need help?** Click **💡 Hint** (up to **3 hints per level**). Each hint gets more specific without giving away the answer.
   - **Still wrong after all 3 hints?** Submitting an incorrect answer after using all 3 hints triggers **Solution Review**: the AI explains your mistake, fills in the working solution, and marks the level as `Solution shown` so you can move on to the next level.
6. **View Your Grade (`Report` page):**
   - Finish all 5 levels and click **Report** (or **🏆 See your grade**) to see your final grade and personalized AI feedback:
     - **A:** 0 hints used and 0 incorrect attempts across all 5 levels
     - **B+:** 1–5 hints used (or 0 hints with some incorrect attempts)
     - **B:** 6–9 hints used
     - **C:** 10–12 hints used
     - **D:** 13–15 hints used, or any level ended with the solution revealed
7. **Reset Anytime:** Click **↺ Reset Progress** in the top navigation bar to clear your browser's saved progress and start fresh from Level 1.

---

## 🧪 Running Automated Tests

To run the test suite (checks all 5 levels' solutions, constraint checker, grading rules, tutor flow, and AI safety checks):

```bash
python manage.py test
```
