"""
Generate a self-contained HTML file for the Dictionary of Symbols with:
  - Dictionary mode: alphabetical card browsing with A-Z nav
  - Quiz mode: multiple-choice (definition shown, pick the term)
  - NO images (text-only dictionary)

Adapted from generate_html.py (Alchemical Dictionary).

Reads: symbols_dictionary.json
Outputs: symbols_dictionary.html
"""

import json
import os
import html as html_module
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(SCRIPT_DIR, "symbols_dictionary.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "symbols_dictionary.html")


def slugify(text):
    """Create a URL-safe slug from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def generate_html(entries):
    """Generate the complete HTML page (no images)."""

    # Prepare entry data for JavaScript
    js_entries = []
    for entry in entries:
        term = entry["term"]
        js_entries.append({
            "term": term,
            "definition": entry["definition"],
            "is_cross_ref": entry["is_cross_ref"],
            "page": entry.get("page", 0),
            "slug": slugify(term),
            "letter": term[0].upper() if term else "?",
        })

    entries_json = json.dumps(js_entries, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dictionary of Symbols</title>
<style>
/* === RESET & BASE === */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
    --parchment: #f0ede4;
    --parchment-light: #f8f6f0;
    --parchment-dark: #c8c0ab;
    --ink: #1a1a2e;
    --ink-light: #3a3a55;
    --ink-muted: #6a6a80;
    --accent: #4a3080;
    --accent-light: #7a60b0;
    --accent-dark: #2e1860;
    --gold: #b8963e;
    --gold-light: #d4b868;
    --gold-dark: #8a6e1e;
    --red: #7a2020;
    --red-light: #a03030;
    --green: #2a6030;
    --card-bg: #fdfcf8;
    --card-shadow: 0 2px 8px rgba(26, 26, 46, 0.12);
    --card-shadow-hover: 0 6px 20px rgba(26, 26, 46, 0.22);
}}

body {{
    font-family: 'Georgia', 'Palatino Linotype', 'Book Antiqua', 'Palatino', serif;
    background: var(--parchment);
    color: var(--ink);
    line-height: 1.6;
    min-height: 100vh;
}}

/* === HEADER === */
.site-header {{
    background: linear-gradient(180deg, #1a1a2e 0%, #2a2a45 100%);
    color: var(--gold-light);
    padding: 30px 20px 20px;
    text-align: center;
    border-bottom: 3px solid var(--gold);
    position: sticky;
    top: 0;
    z-index: 100;
}}

.site-header h1 {{
    font-size: 1.8em;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gold-light);
    margin-bottom: 4px;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}}

.site-header .subtitle {{
    font-size: 0.85em;
    color: var(--parchment-dark);
    font-style: italic;
    margin-bottom: 15px;
}}

/* === MODE TOGGLE === */
.mode-toggle {{
    display: flex;
    justify-content: center;
    gap: 0;
    margin-bottom: 15px;
}}

.mode-btn {{
    padding: 8px 24px;
    border: 1px solid var(--gold-dark);
    background: transparent;
    color: var(--parchment-dark);
    font-family: inherit;
    font-size: 0.9em;
    cursor: pointer;
    transition: all 0.2s;
}}

.mode-btn:first-child {{ border-radius: 4px 0 0 4px; }}
.mode-btn:last-child {{ border-radius: 0 4px 4px 0; }}

.mode-btn.active {{
    background: var(--accent-dark);
    color: #fff;
    border-color: var(--accent);
}}

.mode-btn:hover:not(.active) {{
    background: rgba(74, 48, 128, 0.25);
}}

/* === CONTROLS === */
.controls {{
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}}

.controls input[type="text"] {{
    padding: 8px 14px;
    border: 1px solid var(--gold-dark);
    border-radius: 4px;
    background: rgba(255,255,255,0.1);
    color: var(--gold-light);
    font-family: inherit;
    font-size: 0.9em;
    width: 280px;
    outline: none;
}}

.controls input::placeholder {{
    color: var(--parchment-dark);
    opacity: 0.7;
}}

.controls select {{
    padding: 8px 12px;
    border: 1px solid var(--gold-dark);
    border-radius: 4px;
    background: rgba(255,255,255,0.1);
    color: var(--gold-light);
    font-family: inherit;
    font-size: 0.9em;
    cursor: pointer;
}}

.controls select option {{
    background: #1a1a2e;
    color: var(--gold-light);
}}

.stats {{
    font-size: 0.8em;
    color: var(--parchment-dark);
    margin-top: 5px;
}}

/* === ALPHABET NAV === */
.alpha-nav {{
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 2px;
    padding: 8px 20px;
    background: #2a2a45;
    border-bottom: 1px solid var(--gold-dark);
}}

.alpha-btn {{
    display: inline-block;
    padding: 4px 8px;
    font-size: 0.85em;
    font-weight: bold;
    color: var(--gold-light);
    background: transparent;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    font-family: inherit;
    transition: all 0.15s;
    min-width: 28px;
    text-align: center;
}}

.alpha-btn:hover {{
    background: var(--accent-dark);
    color: #fff;
}}

.alpha-btn.active {{
    background: var(--accent);
    color: #fff;
}}

.alpha-btn.disabled {{
    color: #4a4a60;
    cursor: default;
}}

/* === MAIN CONTENT === */
main {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}}

/* === LETTER SECTIONS === */
.letter-section {{
    margin-bottom: 30px;
}}

.letter-heading {{
    font-size: 2em;
    color: var(--accent);
    border-bottom: 2px solid var(--gold);
    padding-bottom: 6px;
    margin-bottom: 16px;
    letter-spacing: 0.05em;
}}

/* === CARD GRID === */
.card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 20px;
}}

/* === CARDS (no images) === */
.card {{
    background: var(--card-bg);
    border: 1px solid var(--parchment-dark);
    border-radius: 6px;
    box-shadow: var(--card-shadow);
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}}

.card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--card-shadow-hover);
}}

.card-body {{
    padding: 16px 18px;
    flex: 1;
    display: flex;
    flex-direction: column;
}}

.card-term {{
    font-size: 1.15em;
    font-weight: bold;
    color: var(--accent);
    margin-bottom: 8px;
    border-bottom: 1px solid var(--gold-light);
    padding-bottom: 5px;
}}

.card-definition {{
    font-size: 0.88em;
    line-height: 1.65;
    color: var(--ink-light);
    flex: 1;
    max-height: 200px;
    overflow-y: auto;
    padding-right: 4px;
}}

.card-definition::-webkit-scrollbar {{
    width: 5px;
}}
.card-definition::-webkit-scrollbar-thumb {{
    background: var(--parchment-dark);
    border-radius: 3px;
}}

.card-cross-ref {{
    font-style: italic;
    color: var(--gold-dark);
    font-size: 0.92em;
}}

.xref-link {{
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px dotted var(--accent);
    cursor: pointer;
}}

.xref-link:hover {{
    color: var(--accent-light);
    border-bottom-style: solid;
}}

.card-page {{
    font-size: 0.72em;
    color: var(--ink-muted);
    margin-top: 8px;
    text-align: right;
}}

/* === MODAL / EXPANDED CARD === */
.modal-overlay {{
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(10, 10, 20, 0.85);
    z-index: 200;
    overflow-y: auto;
    padding: 40px 20px;
    cursor: pointer;
}}

.modal-overlay.open {{
    display: flex;
    align-items: flex-start;
    justify-content: center;
}}

.modal-content {{
    background: var(--card-bg);
    border: 2px solid var(--gold);
    border-radius: 8px;
    max-width: 700px;
    width: 100%;
    margin: auto;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
    cursor: default;
    overflow: hidden;
}}

.modal-close {{
    position: absolute;
    top: 12px;
    right: 20px;
    font-size: 2em;
    color: var(--gold-light);
    cursor: pointer;
    background: none;
    border: none;
    font-family: inherit;
    line-height: 1;
    z-index: 201;
}}

.modal-close:hover {{
    color: #fff;
}}

.modal-body {{
    padding: 28px;
}}

.modal-term {{
    font-size: 1.6em;
    font-weight: bold;
    color: var(--accent);
    margin-bottom: 12px;
    border-bottom: 2px solid var(--gold);
    padding-bottom: 8px;
}}

.modal-definition {{
    font-size: 1em;
    line-height: 1.8;
    color: var(--ink);
}}

.modal-meta {{
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--parchment-dark);
    font-size: 0.8em;
    color: var(--ink-muted);
}}

/* === QUIZ MODE === */
#quiz-container {{
    display: none;
    max-width: 700px;
    margin: 30px auto;
    padding: 0 20px;
}}

.quiz-card {{
    background: var(--card-bg);
    border: 1px solid var(--parchment-dark);
    border-radius: 8px;
    box-shadow: var(--card-shadow);
    padding: 30px;
    text-align: center;
}}

.quiz-prompt {{
    font-size: 0.8em;
    color: var(--ink-muted);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

.quiz-definition {{
    font-size: 1em;
    line-height: 1.7;
    color: var(--ink);
    margin-bottom: 25px;
    text-align: left;
    padding: 15px;
    background: var(--parchment-light);
    border-left: 3px solid var(--accent);
    border-radius: 0 4px 4px 0;
    max-height: 200px;
    overflow-y: auto;
}}

.quiz-redacted {{
    color: var(--accent);
    letter-spacing: 0.05em;
}}

.quiz-options {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}}

.quiz-option {{
    padding: 12px 16px;
    border: 2px solid var(--parchment-dark);
    border-radius: 6px;
    background: var(--card-bg);
    font-family: inherit;
    font-size: 1em;
    color: var(--ink);
    cursor: pointer;
    transition: all 0.15s;
    text-align: center;
}}

.quiz-option:hover:not(.disabled) {{
    border-color: var(--accent);
    background: var(--parchment-light);
}}

.quiz-option.correct {{
    border-color: var(--green);
    background: #e8f5e8;
    color: var(--green);
    font-weight: bold;
}}

.quiz-option.incorrect {{
    border-color: var(--red);
    background: #fde8e8;
    color: var(--red);
}}

.quiz-option.disabled {{
    cursor: default;
    opacity: 0.7;
}}

.quiz-score {{
    font-size: 1.1em;
    color: var(--accent);
    margin-bottom: 15px;
    font-weight: bold;
}}

.quiz-next {{
    padding: 10px 30px;
    border: 2px solid var(--accent);
    border-radius: 6px;
    background: var(--accent-dark);
    color: #fff;
    font-family: inherit;
    font-size: 1em;
    cursor: pointer;
    transition: all 0.15s;
    display: none;
}}

.quiz-next:hover {{
    background: var(--accent);
    color: #fff;
}}

.quiz-reset {{
    display: inline-block;
    margin-left: 10px;
    padding: 10px 20px;
    border: 1px solid var(--parchment-dark);
    border-radius: 6px;
    background: transparent;
    color: var(--ink-muted);
    font-family: inherit;
    font-size: 0.9em;
    cursor: pointer;
}}

.quiz-reset:hover {{
    background: var(--parchment-light);
}}

/* === INSPIRE MODE === */
#inspire-container {{
    display: none;
    max-width: 800px;
    margin: 30px auto;
    padding: 0 20px;
}}

.inspire-setup {{
    background: var(--card-bg);
    border: 1px solid var(--parchment-dark);
    border-radius: 8px;
    box-shadow: var(--card-shadow);
    padding: 24px 28px;
    margin-bottom: 24px;
}}

.inspire-api-key-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
}}

.inspire-api-key-row label {{
    font-size: 0.9em;
    color: var(--ink-light);
    white-space: nowrap;
    min-width: 140px;
}}

.inspire-api-key-row input {{
    flex: 1;
    padding: 8px 12px;
    border: 1px solid var(--parchment-dark);
    border-radius: 4px;
    background: var(--parchment-light);
    font-family: monospace;
    font-size: 0.85em;
    color: var(--ink);
}}

.inspire-toggle-key {{
    background: none;
    border: 1px solid var(--parchment-dark);
    border-radius: 4px;
    padding: 6px 10px;
    cursor: pointer;
    font-size: 1em;
}}

.inspire-slider-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
}}

.inspire-slider-row label {{
    font-size: 0.95em;
    color: var(--ink-light);
    min-width: 110px;
}}

#inspire-count-display {{
    font-weight: bold;
    color: var(--accent);
    font-size: 1.1em;
}}

.inspire-slider-row input[type="range"] {{
    flex: 1;
    accent-color: var(--accent);
}}

.inspire-buttons {{
    display: flex;
    gap: 12px;
    justify-content: center;
}}

.inspire-btn {{
    padding: 12px 28px;
    border-radius: 6px;
    font-family: inherit;
    font-size: 1em;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid var(--accent);
}}

.inspire-btn-primary {{
    background: var(--accent-dark);
    color: #fff;
}}

.inspire-btn-primary:hover {{
    background: var(--accent);
}}

.inspire-btn-primary:disabled {{
    background: var(--ink-muted);
    border-color: var(--ink-muted);
    cursor: not-allowed;
}}

.inspire-btn-secondary {{
    background: transparent;
    color: var(--accent);
}}

.inspire-btn-secondary:hover {{
    background: rgba(74, 48, 128, 0.1);
}}

.inspire-symbols {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 14px;
    margin-bottom: 24px;
}}

.inspire-symbol-card {{
    background: var(--card-bg);
    border: 1px solid var(--gold-light);
    border-radius: 6px;
    padding: 14px 16px;
    box-shadow: var(--card-shadow);
}}

.inspire-symbol-card h4 {{
    color: var(--accent);
    font-size: 1em;
    margin-bottom: 6px;
    border-bottom: 1px solid var(--gold-light);
    padding-bottom: 4px;
}}

.inspire-symbol-card p {{
    font-size: 0.82em;
    color: var(--ink-light);
    line-height: 1.5;
}}

.inspire-loading {{
    text-align: center;
    padding: 40px 20px;
}}

.inspire-spinner {{
    width: 40px;
    height: 40px;
    border: 3px solid var(--parchment-dark);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: inspire-spin 0.8s linear infinite;
    margin: 0 auto 16px;
}}

@keyframes inspire-spin {{
    to {{ transform: rotate(360deg); }}
}}

.inspire-loading-text {{
    color: var(--ink-muted);
    font-style: italic;
    font-size: 0.95em;
}}

.inspire-narrative {{
    background: var(--card-bg);
    border: 2px solid var(--gold);
    border-radius: 8px;
    padding: 28px 32px;
    box-shadow: var(--card-shadow-hover);
    line-height: 1.8;
    color: var(--ink);
    font-size: 1.02em;
}}

.inspire-narrative h3 {{
    color: var(--accent);
    font-size: 1.3em;
    margin-bottom: 16px;
    border-bottom: 2px solid var(--gold);
    padding-bottom: 8px;
    text-align: center;
}}

.inspire-narrative .narrative-body p {{
    margin-bottom: 12px;
    text-indent: 1.5em;
}}

.inspire-narrative .narrative-body p:first-child {{
    text-indent: 0;
}}

.inspire-error {{
    background: #fde8e8;
    border: 1px solid var(--red);
    border-radius: 6px;
    padding: 14px 18px;
    color: var(--red);
    font-size: 0.9em;
    margin-top: 16px;
}}

/* === COPY BUTTON === */
.copy-btn {{
    background: transparent;
    border: 1px solid var(--ink-muted);
    border-radius: 4px;
    color: var(--ink-muted);
    cursor: pointer;
    font-size: 0.78em;
    padding: 4px 10px;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}}
.copy-btn:hover {{
    border-color: var(--accent);
    color: var(--accent);
}}
.copy-btn.copied {{
    border-color: #4caf50;
    color: #4caf50;
}}
.modal-body {{ position: relative; }}
.modal-copy-row {{
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
}}
.inspire-narrative {{ position: relative; }}
.narrative-copy-row {{
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--gold-light);
}}

/* === RESPONSIVE === */
@media (max-width: 768px) {{
    .site-header h1 {{ font-size: 1.3em; }}
    .card-grid {{ grid-template-columns: 1fr; }}
    .quiz-options {{ grid-template-columns: 1fr; }}
    .controls input[type="text"] {{ width: 100%; }}
    .controls {{ flex-direction: column; align-items: center; }}
    .inspire-api-key-row {{ flex-direction: column; align-items: stretch; }}
    .inspire-api-key-row label {{ min-width: unset; }}
    .inspire-symbols {{ grid-template-columns: 1fr; }}
    .inspire-buttons {{ flex-direction: column; }}
}}

/* === PRINT === */
@media print {{
    .site-header, .alpha-nav, .controls, .mode-toggle, #quiz-container, #inspire-container {{
        display: none !important;
    }}
    main {{ padding: 0; }}
    .card {{
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid #ccc;
        page-break-inside: avoid;
    }}
    .card-definition {{ max-height: none; overflow: visible; }}
    body {{ background: white; }}
}}

/* Hide sections */
.hidden {{ display: none !important; }}
</style>
</head>
<body>

<header class="site-header">
    <h1>Dictionary of Symbols</h1>
    <p class="subtitle">Based on the work by Jean Chevalier &amp; Alain Gheerbrant</p>

    <div class="mode-toggle">
        <button class="mode-btn active" id="btn-dictionary" onclick="switchMode('dictionary')">Dictionary</button>
        <button class="mode-btn" id="btn-quiz" onclick="switchMode('quiz')">Quiz</button>
        <button class="mode-btn" id="btn-inspire" onclick="switchMode('inspire')">Inspire</button>
    </div>

    <div class="controls" id="dict-controls">
        <input type="text" id="search" placeholder="Search terms or definitions..." oninput="filterEntries()">
        <select id="filter" onchange="filterEntries()">
            <option value="all">All Entries</option>
            <option value="definitions">Definitions Only</option>
            <option value="crossrefs">Cross-References</option>
        </select>
        <span class="stats" id="stats"></span>
    </div>
</header>

<nav class="alpha-nav" id="alpha-nav"></nav>

<main id="dictionary-container"></main>

<div id="quiz-container">
    <div class="quiz-card">
        <div class="quiz-score" id="quiz-score">Score: 0 / 0</div>
        <p class="quiz-prompt">What term does this definition describe?</p>
        <div class="quiz-definition" id="quiz-definition"></div>
        <div class="quiz-options" id="quiz-options"></div>
        <button class="quiz-next" id="quiz-next" onclick="nextQuestion()">Next Question</button>
        <button class="quiz-reset" onclick="resetQuiz()">Reset Score</button>
    </div>
</div>

<div id="inspire-container">
    <div class="inspire-setup">
        <div class="inspire-api-key-row">
            <label for="inspire-api-key">Anthropic API Key:</label>
            <input type="password" id="inspire-api-key" placeholder="sk-ant-..." oninput="saveApiKey(this.value)">
            <button class="inspire-toggle-key" onclick="toggleApiKeyVisibility()" title="Show/hide key">&#128065;</button>
        </div>

        <div class="inspire-slider-row">
            <label for="inspire-count">Symbols: <span id="inspire-count-display">3</span></label>
            <input type="range" id="inspire-count" min="2" max="7" value="3" oninput="document.getElementById('inspire-count-display').textContent = this.value">
        </div>

        <div class="inspire-buttons">
            <button class="inspire-btn inspire-btn-primary" id="inspire-generate" onclick="inspireGenerate()">&#9733; Inspire Me</button>
            <button class="inspire-btn inspire-btn-secondary" id="inspire-reroll" onclick="inspireReroll()" style="display:none">&#8635; Re-roll Symbols</button>
        </div>
    </div>

    <div id="inspire-symbols" class="inspire-symbols"></div>

    <div id="inspire-loading" class="inspire-loading" style="display:none">
        <div class="inspire-spinner"></div>
        <p class="inspire-loading-text">Weaving symbols into a narrative...</p>
    </div>

    <div id="inspire-narrative" class="inspire-narrative" style="display:none"></div>

    <div id="inspire-error" class="inspire-error" style="display:none"></div>
</div>

<div class="modal-overlay" id="modal-overlay" onclick="closeModal(event)">
    <button class="modal-close" onclick="closeModal(event)">&times;</button>
    <div class="modal-content">
        <div class="modal-body">
            <h2 class="modal-term" id="modal-term"></h2>
            <div class="modal-definition" id="modal-definition"></div>
            <div class="modal-meta">
                <span id="modal-page"></span>
            </div>
            <div class="modal-copy-row">
                <button class="copy-btn" onclick="copyDefinition(event)">&#x2398; Copy</button>
            </div>
        </div>
    </div>
</div>

<script>
// ============================================================
// DATA
// ============================================================
const ENTRIES = {entries_json};

// ============================================================
// STATE
// ============================================================
let currentMode = 'dictionary';
let currentLetter = null;
let quizCorrect = 0;
let quizTotal = 0;
let quizUsed = new Set();
let currentQuizEntry = null;

// Only entries with definitions (not cross-references) for quiz
const quizEntries = ENTRIES.filter(e => !e.is_cross_ref && e.definition.length > 50);

// Entries pool for Inspire mode (same filter)
const inspireEntries = quizEntries;
let inspireSymbols = [];

// ============================================================
// UTILITY
// ============================================================
function escapeHtml(str) {{
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}}

function processDefinition(text) {{
    let escaped = escapeHtml(text);
    // Convert (see also term) and (see term) to clickable links
    escaped = escaped.replace(/\\(see\\s+(?:also\\s+)?([^)]+)\\)/gi, function(match, terms) {{
        const parts = terms.split(/[;,]/).map(t => t.trim()).filter(t => t);
        const links = parts.map(t => {{
            const slug = t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
            return '<a href="#term-' + slug + '" class="xref-link">' + t + '</a>';
        }});
        return '(see ' + (match.toLowerCase().includes('also') ? 'also ' : '') + links.join('; ') + ')';
    }});
    return escaped;
}}

function slugify(text) {{
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}}

// ============================================================
// QUIZ TERM REDACTION
// ============================================================
function redactTermFromDefinition(text, term) {{
    if (!term || !text) return text;

    const escapeRegex = (s) => s.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');

    const patterns = [];

    // Full term pattern (flexible whitespace for multi-word)
    const fullPattern = escapeRegex(term).replace(/\\s+/g, '\\\\s+');
    patterns.push(fullPattern);

    // For multi-word terms, also redact individual words >= 4 chars
    const words = term.split(/\\s+/);
    if (words.length > 1) {{
        words.forEach(w => {{
            if (w.length >= 4) {{
                patterns.push(escapeRegex(w));
            }}
        }});
    }}

    // Sort longest-first, add suffix variants for plurals/possessives
    patterns.sort((a, b) => b.length - a.length);
    const suffixed = patterns.map(p => p + "(?:e?s)?(?:'s|s')?");
    const combined = '\\\\b(?:' + suffixed.join('|') + ')\\\\b';
    const regex = new RegExp(combined, 'gi');

    return text.replace(regex, '\\u2588\\u2588\\u2588\\u2588\\u2588\\u2588');
}}

function processDefinitionForQuiz(text, term) {{
    const redacted = redactTermFromDefinition(text, term);
    let html = processDefinition(redacted);
    html = html.replace(/\\u2588{{6}}/g, '<span class="quiz-redacted">\\u2588\\u2588\\u2588\\u2588\\u2588\\u2588</span>');
    return html;
}}

// ============================================================
// DICTIONARY MODE
// ============================================================
function buildDictionary() {{
    const container = document.getElementById('dictionary-container');
    const nav = document.getElementById('alpha-nav');

    // Group entries by first letter
    const groups = {{}};
    ENTRIES.forEach(e => {{
        const letter = e.letter;
        if (!groups[letter]) groups[letter] = [];
        groups[letter].push(e);
    }});

    // Build alpha nav
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    nav.innerHTML = '<button class="alpha-btn active" onclick="filterByLetter(null)">ALL</button>';
    letters.forEach(l => {{
        const has = groups[l] && groups[l].length > 0;
        const cls = has ? 'alpha-btn' : 'alpha-btn disabled';
        const onclick = has ? `onclick="filterByLetter('${{l}}')"` : '';
        nav.innerHTML += `<button class="${{cls}}" ${{onclick}}>${{l}}</button>`;
    }});

    // Build card sections
    let html = '';
    const sortedLetters = Object.keys(groups).sort();
    sortedLetters.forEach(letter => {{
        const entries = groups[letter];
        html += `<section class="letter-section" data-letter="${{letter}}" id="section-${{letter}}">`;
        html += `<h2 class="letter-heading">${{letter}}</h2>`;
        html += '<div class="card-grid">';
        entries.forEach(e => {{
            const type = e.is_cross_ref ? 'crossref' : 'definition';
            html += `<div class="card" data-term="${{escapeHtml(e.term.toLowerCase())}}" data-type="${{type}}" data-letter="${{e.letter}}" id="term-${{e.slug}}" onclick="openModal('${{e.slug}}')">`;

            html += '<div class="card-body">';
            html += `<h3 class="card-term">${{escapeHtml(e.term)}}</h3>`;

            if (e.is_cross_ref) {{
                html += `<p class="card-cross-ref">${{processDefinition(e.definition)}}</p>`;
            }} else {{
                html += `<div class="card-definition">${{processDefinition(e.definition)}}</div>`;
            }}

            html += `<div class="card-page">p. ${{e.page}}</div>`;
            html += '</div></div>';
        }});
        html += '</div></section>';
    }});

    container.innerHTML = html;
    updateStats();
}}

function filterByLetter(letter) {{
    currentLetter = letter;

    // Update nav buttons
    document.querySelectorAll('.alpha-btn').forEach(btn => {{
        btn.classList.remove('active');
        if (letter === null && btn.textContent === 'ALL') btn.classList.add('active');
        if (letter && btn.textContent === letter) btn.classList.add('active');
    }});

    filterEntries();

    // Scroll to section
    if (letter) {{
        const section = document.getElementById('section-' + letter);
        if (section) {{
            section.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
    }}
}}

function filterEntries() {{
    const query = document.getElementById('search').value.toLowerCase();
    const filterType = document.getElementById('filter').value;
    let visible = 0;
    let total = 0;

    document.querySelectorAll('.letter-section').forEach(section => {{
        const sectionLetter = section.dataset.letter;
        let sectionVisible = 0;

        // Letter filter
        if (currentLetter && sectionLetter !== currentLetter) {{
            section.classList.add('hidden');
            return;
        }}
        section.classList.remove('hidden');

        section.querySelectorAll('.card').forEach(card => {{
            total++;
            let show = true;

            // Type filter
            if (filterType === 'definitions' && card.dataset.type !== 'definition') show = false;
            if (filterType === 'crossrefs' && card.dataset.type !== 'crossref') show = false;

            // Search filter
            if (query && show) {{
                const term = card.dataset.term;
                const text = card.textContent.toLowerCase();
                if (!term.includes(query) && !text.includes(query)) show = false;
            }}

            card.style.display = show ? '' : 'none';
            if (show) {{ visible++; sectionVisible++; }}
        }});

        // Hide section header if no cards visible
        if (sectionVisible === 0 && (query || filterType !== 'all')) {{
            section.classList.add('hidden');
        }}
    }});

    updateStats(visible);
}}

function updateStats(visible) {{
    const total = ENTRIES.length;
    const defs = ENTRIES.filter(e => !e.is_cross_ref).length;
    const xrefs = ENTRIES.filter(e => e.is_cross_ref).length;
    const showing = visible !== undefined ? visible : total;
    document.getElementById('stats').textContent =
        `Showing ${{showing}} of ${{total}} entries (${{defs}} definitions, ${{xrefs}} cross-references)`;
}}

// ============================================================
// QUIZ MODE
// ============================================================
function nextQuestion() {{
    if (quizUsed.size >= quizEntries.length) {{
        quizUsed.clear();
    }}

    // Pick a random entry not yet used
    let idx;
    do {{
        idx = Math.floor(Math.random() * quizEntries.length);
    }} while (quizUsed.has(idx));
    quizUsed.add(idx);

    const correct = quizEntries[idx];

    // Pick 3 wrong answers
    const wrongIndices = new Set();
    while (wrongIndices.size < 3) {{
        const wi = Math.floor(Math.random() * quizEntries.length);
        if (wi !== idx && !wrongIndices.has(wi)) wrongIndices.add(wi);
    }}

    const options = [correct];
    wrongIndices.forEach(wi => options.push(quizEntries[wi]));

    // Shuffle options
    for (let i = options.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [options[i], options[j]] = [options[j], options[i]];
    }}

    // Show definition
    currentQuizEntry = correct;
    document.getElementById('quiz-definition').innerHTML = processDefinitionForQuiz(correct.definition, correct.term);

    // Show options
    const optionsDiv = document.getElementById('quiz-options');
    optionsDiv.innerHTML = '';
    options.forEach(opt => {{
        const btn = document.createElement('button');
        btn.className = 'quiz-option';
        btn.textContent = opt.term;
        btn.onclick = function() {{ checkAnswer(this, opt.term, correct.term); }};
        optionsDiv.appendChild(btn);
    }});

    // Hide next button
    document.getElementById('quiz-next').style.display = 'none';

    // Update score display
    updateQuizScore();
}}

function checkAnswer(btn, selected, correct) {{
    quizTotal++;
    const buttons = document.querySelectorAll('.quiz-option');

    buttons.forEach(b => {{
        b.classList.add('disabled');
        b.onclick = null;
        if (b.textContent === correct) {{
            b.classList.add('correct');
        }}
    }});

    if (selected === correct) {{
        quizCorrect++;
        btn.classList.add('correct');
    }} else {{
        btn.classList.add('incorrect');
    }}

    updateQuizScore();

    // Un-redact the definition now that the answer is revealed
    if (currentQuizEntry) {{
        document.getElementById('quiz-definition').innerHTML = processDefinition(currentQuizEntry.definition);
    }}

    document.getElementById('quiz-next').style.display = 'inline-block';
}}

function updateQuizScore() {{
    const pct = quizTotal > 0 ? Math.round((quizCorrect / quizTotal) * 100) : 0;
    document.getElementById('quiz-score').textContent =
        `Score: ${{quizCorrect}} / ${{quizTotal}}${{quizTotal > 0 ? ' (' + pct + '%)' : ''}}`;
}}

function resetQuiz() {{
    quizCorrect = 0;
    quizTotal = 0;
    quizUsed.clear();
    nextQuestion();
}}

// ============================================================
// MODE SWITCHING
// ============================================================
function switchMode(mode) {{
    currentMode = mode;

    document.getElementById('btn-dictionary').classList.toggle('active', mode === 'dictionary');
    document.getElementById('btn-quiz').classList.toggle('active', mode === 'quiz');
    document.getElementById('btn-inspire').classList.toggle('active', mode === 'inspire');

    document.getElementById('dictionary-container').style.display = mode === 'dictionary' ? '' : 'none';
    document.getElementById('dict-controls').style.display = mode === 'dictionary' ? 'flex' : 'none';
    document.getElementById('alpha-nav').style.display = mode === 'dictionary' ? 'flex' : 'none';

    document.getElementById('quiz-container').style.display = mode === 'quiz' ? 'block' : 'none';

    document.getElementById('inspire-container').style.display = mode === 'inspire' ? 'block' : 'none';

    if (mode === 'quiz') {{
        nextQuestion();
    }}
    if (mode === 'inspire') {{
        loadApiKey();
    }}
}}

// ============================================================
// MODAL / EXPANDED CARD
// ============================================================
const entryBySlug = {{}};
ENTRIES.forEach(e => {{ entryBySlug[e.slug] = e; }});

function openModal(slug) {{
    const e = entryBySlug[slug];
    if (!e) return;

    document.getElementById('modal-term').textContent = e.term;
    document.getElementById('modal-definition').innerHTML = processDefinition(e.definition);
    document.getElementById('modal-page').textContent = 'p. ' + e.page;

    document.getElementById('modal-overlay').classList.add('open');
    document.body.style.overflow = 'hidden';
}}

function closeModal(event) {{
    if (event && event.target.closest('.modal-content') && !event.target.closest('.modal-close')) return;
    document.getElementById('modal-overlay').classList.remove('open');
    document.body.style.overflow = '';
}}

// Close modal on Escape key
document.addEventListener('keydown', function(ev) {{
    if (ev.key === 'Escape') closeModal(ev);
}});

// ============================================================
// COPY TO CLIPBOARD
// ============================================================
function flashCopyBtn(btn) {{
    const orig = btn.innerHTML;
    btn.innerHTML = '&#x2714; Copied';
    btn.classList.add('copied');
    setTimeout(() => {{
        btn.innerHTML = orig;
        btn.classList.remove('copied');
    }}, 1500);
}}

function copyDefinition(event) {{
    event.stopPropagation();
    const term = document.getElementById('modal-term').textContent;
    const defEl = document.getElementById('modal-definition');
    const def = defEl.innerText || defEl.textContent;
    const text = term + '\\n\\n' + def;
    navigator.clipboard.writeText(text).then(() => {{
        flashCopyBtn(event.currentTarget);
    }});
}}

function copyNarrative(event) {{
    event.stopPropagation();
    const narEl = document.getElementById('inspire-narrative');
    const title = narEl.querySelector('h3')?.textContent || '';
    const body = narEl.querySelector('.narrative-body')?.innerText || '';
    const text = title + '\\n\\n' + body;
    navigator.clipboard.writeText(text).then(() => {{
        flashCopyBtn(event.currentTarget);
    }});
}}

// ============================================================
// INSPIRE MODE
// ============================================================
function loadApiKey() {{
    const saved = localStorage.getItem('inspire_api_key');
    if (saved) {{
        document.getElementById('inspire-api-key').value = saved;
    }}
}}

function saveApiKey(value) {{
    localStorage.setItem('inspire_api_key', value.trim());
}}

function toggleApiKeyVisibility() {{
    const input = document.getElementById('inspire-api-key');
    input.type = input.type === 'password' ? 'text' : 'password';
}}

function getApiKey() {{
    return (document.getElementById('inspire-api-key').value || '').trim();
}}

function pickRandomSymbols(count) {{
    const pool = inspireEntries.slice();
    const result = [];
    for (let i = 0; i < count && pool.length > 0; i++) {{
        const idx = Math.floor(Math.random() * pool.length);
        result.push(pool[idx]);
        pool.splice(idx, 1);
    }}
    return result;
}}

function truncateDefinition(text, maxLen) {{
    if (text.length <= maxLen) return text;
    const truncated = text.substring(0, maxLen);
    const lastPeriod = truncated.lastIndexOf('.');
    if (lastPeriod > maxLen * 0.4) {{
        return truncated.substring(0, lastPeriod + 1);
    }}
    return truncated.substring(0, truncated.lastIndexOf(' ')) + '...';
}}

function displaySymbols(symbols) {{
    const container = document.getElementById('inspire-symbols');
    container.innerHTML = symbols.map(s => {{
        const excerpt = truncateDefinition(s.definition, 180);
        return '<div class="inspire-symbol-card">' +
            '<h4>' + escapeHtml(s.term) + '</h4>' +
            '<p>' + escapeHtml(excerpt) + '</p>' +
            '</div>';
    }}).join('');
}}

function showInspireError(message) {{
    const el = document.getElementById('inspire-error');
    el.textContent = message;
    el.style.display = 'block';
}}

function hideInspireError() {{
    document.getElementById('inspire-error').style.display = 'none';
}}

function inspireReroll() {{
    hideInspireError();
    const count = parseInt(document.getElementById('inspire-count').value);
    inspireSymbols = pickRandomSymbols(count);
    displaySymbols(inspireSymbols);
    document.getElementById('inspire-narrative').style.display = 'none';
}}

async function inspireGenerate() {{
    hideInspireError();

    const apiKey = getApiKey();
    if (!apiKey) {{
        showInspireError('Please enter your Anthropic API key above.');
        return;
    }}
    if (!apiKey.startsWith('sk-ant-')) {{
        showInspireError('API key should start with "sk-ant-". Please check your key.');
        return;
    }}

    const count = parseInt(document.getElementById('inspire-count').value);
    inspireSymbols = pickRandomSymbols(count);
    displaySymbols(inspireSymbols);

    document.getElementById('inspire-reroll').style.display = '';

    await generateNarrative(inspireSymbols);
}}

async function generateNarrative(symbols) {{
    const loading = document.getElementById('inspire-loading');
    const narrativeEl = document.getElementById('inspire-narrative');
    const generateBtn = document.getElementById('inspire-generate');

    loading.style.display = 'block';
    narrativeEl.style.display = 'none';
    generateBtn.disabled = true;

    const symbolDescriptions = symbols.map(s => {{
        const excerpt = truncateDefinition(s.definition, 400);
        return s.term + ': ' + excerpt;
    }}).join('\\n\\n');

    const prompt = 'You are a visionary creative writer with deep knowledge of symbolism and mythology. Given the following ' + symbols.length + ' symbols from a Dictionary of Symbols, describe a vivid scene or vision that weaves ALL of these symbols together into one unified narrative.\\n\\nSYMBOLS:\\n' + symbolDescriptions + '\\n\\nINSTRUCTIONS:\\n- Describe the scene as if it is a living vision or dream — what do you SEE?\\n- STRICTLY FORBIDDEN: Do NOT use any of these words or concepts: painting, mural, tapestry, canvas, oil, brushwork, impasto, gold leaf, mixed-media, composition, rendered, foreground, background, chiaroscuro, gallery, artwork, piece, work, viewer, image, frame, depicted, portrayed, medium, technique, pigment, palette. Do not reference any artistic process, material, or method whatsoever.\\n- Weave ALL the symbols together into one interconnected scene — do not describe them one by one.\\n- Describe colors, light, shadow, atmosphere, mood, and spatial relationships naturally as part of the scene.\\n- Draw on the symbolic meanings to create thematic depth and interconnections.\\n- Give the scene a title.\\n- Keep the description between 200-300 words.\\n- Write in vivid, evocative prose as if narrating a dream or myth.\\n\\nRespond with ONLY the title on the first line (no label, just the title), then a blank line, then the description. No preamble, no meta-commentary.';

    const body = JSON.stringify({{
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 1024,
        messages: [{{ role: 'user', content: prompt }}],
    }});

    try {{
        const response = await fetch('https://api.anthropic.com/v1/messages', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'x-api-key': getApiKey(),
                'anthropic-version': '2023-06-01',
                'anthropic-dangerous-direct-browser-access': 'true',
            }},
            body: body,
        }});

        if (!response.ok) {{
            const errData = await response.json().catch(() => ({{}}));
            if (response.status === 401) {{
                throw new Error('Invalid API key. Please check your Anthropic API key.');
            }} else if (response.status === 429) {{
                throw new Error('Rate limited. Please wait a moment and try again.');
            }} else if (response.status === 529) {{
                throw new Error('Anthropic API is overloaded. Please try again shortly.');
            }} else {{
                throw new Error(errData.error?.message || ('API error: HTTP ' + response.status));
            }}
        }}

        const data = await response.json();
        const text = data.content[0].text.trim();

        const lines = text.split('\\n');
        const title = lines[0].replace(/^#+\\s*/, '').replace(/^\\*+|\\*+$/g, '').trim();
        const bodyText = lines.slice(1).join('\\n').trim();

        const paragraphs = bodyText.split(/\\n\\n+/).filter(p => p.trim());
        const bodyHtml = paragraphs.map(p => '<p>' + escapeHtml(p.trim()) + '</p>').join('');

        narrativeEl.innerHTML = '<h3>' + escapeHtml(title) + '</h3>' +
            '<div class="narrative-body">' + bodyHtml + '</div>' +
            '<div class="narrative-copy-row"><button class="copy-btn" onclick="copyNarrative(event)">&#x2398; Copy</button></div>';
        narrativeEl.style.display = 'block';

    }} catch (err) {{
        showInspireError(err.message || 'Failed to connect to Anthropic API.');
    }} finally {{
        loading.style.display = 'none';
        generateBtn.disabled = false;
    }}
}}

// ============================================================
// INIT
// ============================================================
buildDictionary();
</script>
</body>
</html>"""

    return html_content


def main():
    # Load dictionary data
    print(f"Loading dictionary: {DICT_PATH}")
    with open(DICT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data["entries"]
    defs = sum(1 for e in entries if not e["is_cross_ref"])
    xrefs = sum(1 for e in entries if e["is_cross_ref"])
    print(f"  Entries: {len(entries)} ({defs} definitions, {xrefs} cross-references)")

    # Generate HTML
    html = generate_html(entries)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML written to: {OUTPUT_PATH}")
    print(f"  File size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
