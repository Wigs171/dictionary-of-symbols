"""
Extract entries from 'Dictionary of Symbols' (reprint edition) PDF.

The PDF has uniform formatting (all LiberationSerif 15pt), so entry
detection uses BLOCK-LEVEL analysis: each text block from PyMuPDF
represents a paragraph, and entries only begin at the START of a block.

This prevents mid-sentence text from being falsely detected as headings.

Entry pattern: a lowercase term followed by capitalized definition text,
appearing at the beginning of a new text block.

Outputs: symbols_dictionary.json
"""

import fitz  # PyMuPDF
import json
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(SCRIPT_DIR, "dictionary-of-symbols-reprint-edition.pdf")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "symbols_dictionary.json")

# Page range for dictionary content (0-indexed)
# Pages 1-8 are blank/front matter/contributors
# Dictionary starts on page 9 (0-indexed: 8) with "abracadabra"
# Bibliography starts around page 1816
DICT_START_PAGE = 8    # 0-indexed (= page 9 in PDF)
DICT_END_PAGE = 1804   # exclusive; bibliography starts on page 1804

# Common sentence starters that should NOT be treated as proper noun headings.
# These appear at the start of continuation blocks and would be falsely
# detected by Pattern 2 (capitalized word + capitalized word).
SENTENCE_STARTERS = {
    "the", "a", "an", "in", "on", "at", "by", "for", "to", "of",
    "it", "its", "this", "that", "these", "those", "they", "them",
    "he", "she", "his", "her", "we", "our", "but", "and", "or",
    "if", "as", "so", "yet", "nor", "not", "no", "all", "any",
    "both", "each", "every", "some", "such", "than",
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "from", "with", "into", "upon", "over", "under", "through",
    "between", "among", "about", "during", "before", "after",
    "since", "while", "when", "where", "which", "what", "who",
    "how", "there", "here", "thus", "hence", "therefore",
    "however", "moreover", "furthermore", "nevertheless",
    "according", "although", "because", "whether", "like",
    "many", "most", "much", "more", "less", "few", "other",
    "another", "only", "just", "even", "still", "also", "too",
}


def is_running_header(text):
    """Detect ALL-CAPS running headers like 'AUTOMOBILE', 'DREAM', 'SWASTIKA'."""
    stripped = text.strip().rstrip('.')
    if not stripped:
        return False
    alpha_chars = [c for c in stripped if c.isalpha()]
    if not alpha_chars:
        return False
    upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
    if upper_ratio >= 0.9 and 2 <= len(stripped) <= 50:
        return True
    return False


def is_page_number(text):
    """Detect standalone page numbers like '311', '59'."""
    stripped = text.strip()
    return bool(re.match(r'^\d{1,4}$', stripped))


def get_block_text(block):
    """Extract all text from a block dict, line by line."""
    if block["type"] != 0:  # non-text block
        return ""
    lines = []
    for line in block["lines"]:
        line_text = ""
        for span in line["spans"]:
            line_text += span["text"]
        lines.append(line_text)
    return "\n".join(lines)


def get_block_first_line(block):
    """Get just the first line of text from a block."""
    if block["type"] != 0:
        return ""
    for line in block["lines"]:
        text = ""
        for span in line["spans"]:
            text += span["text"]
        return text.strip()
    return ""


def _is_valid_term(term):
    """
    Check if a detected term looks like a real dictionary headword
    rather than a sentence fragment.

    Real headwords: "abracadabra", "aqua vitae", "fiery curtain",
                    "Abraham", "Aurora Borealis"
    Fragments:      "death and resurrection of", "pura in the",
                    "very", "blue for", "Cabeiri The"
    """
    words = term.split()
    if not words:
        return False

    first_word = words[0].lower()
    last_word = words[-1].lower()

    # First word is a common sentence starter
    if first_word in SENTENCE_STARTERS:
        return False

    # Last word is a function word (preposition, article, conjunction)
    # Real headwords don't end with these
    FRAG_ENDERS = {
        "the", "a", "an", "of", "in", "on", "at", "to", "for", "by",
        "with", "from", "and", "or", "but", "as", "is", "was", "are",
        "were", "be", "been", "being", "has", "had", "have", "its",
        "his", "her", "he", "she", "it", "they", "we", "our", "their",
        "that", "this", "those", "these", "which", "who", "whom",
        "not", "no", "nor", "so", "than", "if", "st",
    }
    if last_word in FRAG_ENDERS:
        return False

    # Too many words — headwords are typically 1-4 words
    if len(words) > 5:
        return False

    # Internal function words suggest a sentence fragment
    # "death and resurrection of" has "and" + "of"
    # But "aqua vitae" or "lapis lazuli" are fine
    if len(words) >= 3:
        internal_words = [w.lower() for w in words[1:]]
        FRAG_INTERNALS = {
            "the", "a", "an", "is", "was", "are", "were", "be",
            "that", "which", "who", "whom", "has", "had", "have",
            "not", "also", "been", "being", "its", "his", "her",
            "their", "our", "my", "your", "can", "could", "would",
            "should", "will", "shall", "may", "might", "must",
            "do", "does", "did", "very", "just", "even", "still",
        }
        internal_frag_count = sum(1 for w in internal_words if w in FRAG_INTERNALS)
        if internal_frag_count >= 2:
            return False
        # If internal words contain "the", "is", "was" — very likely a fragment
        if any(w in {"the", "is", "was", "are", "were"} for w in internal_words):
            return False

    return True


def detect_entry_heading(first_line):
    """
    Detect if a block's first line starts a new dictionary entry.

    ONLY called on the first line of each text block, NOT on every line.
    This is the key difference from the previous version that produced
    19,653 false entries.

    Pattern: lowercase term word(s) followed by capitalized sentence.
    Examples:
        'abracadabra This charm was used...'
        'mandrake The mandrake is a fertility symbol...'
        'fiery curtain The fiery curtain constitutes...'
        'aureole See halo.'
        'tower (see also house; ziggurat) The tower...'
    """
    line = first_line.strip()
    if len(line) < 5:
        return None

    # Pattern 1: lowercase term + space + uppercase start of definition
    # Matches: "abracadabra This charm..." or "aqua vitae The alchemists..."
    # Also handles parenthetical cross-refs: "tower (see also house) The tower..."
    # For long parentheticals like "bird (see also anqa; bustard; cock; ...)"
    # we match just the term before the parenthetical.
    m = re.match(
        r'^([a-z][a-z\s,\'\-]+?)'       # lowercase term (lazy)
        r'(?:\s*\([^)]*\))?'            # optional CLOSED parenthetical
        r'\s+'                           # separator
        r'([A-Z\'\"].*)',                # definition starts uppercase
        line
    )
    if m:
        term = m.group(1).strip().rstrip('.,')
        rest = m.group(2)
        if 2 <= len(term) <= 50 and len(rest) >= 10:
            if _is_valid_term(term):
                return term

    # Pattern 1b: lowercase term + LONG parenthetical that doesn't close on first line
    # Matches: "bird (see also anqa; bustard; cock; crane; crow; ..."
    m = re.match(
        r'^([a-z][a-z\s,\'\-]+?)\s+\(',  # term + open paren
        line
    )
    if m:
        term = m.group(1).strip().rstrip('.,')
        # Check if this looks like "(see also ...)" or "(see ...)"
        paren_content = line[m.end()-1:]  # from the '('
        if re.match(r'\([Ss]ee\s', paren_content):
            if 2 <= len(term) <= 50 and _is_valid_term(term):
                return term

    # Pattern 2: Capitalized proper noun term + definition
    # Matches: "Abraham The Old Testament..." or "Aurora Borealis A manifestation..."
    # BUT NOT: "The African legend..." or "Both St John..."
    #
    # Strategy: greedily capture capitalized words, then trim trailing
    # articles/starters that belong to the definition, not the term.
    m = re.match(
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'  # Capitalized words (greedy)
        r'\s+'                                   # separator
        r'([A-Z][a-z].*)',                        # definition starts
        line
    )
    if m:
        raw_term = m.group(1).strip()
        # Trim trailing words that belong to the definition, not the name.
        # "Abraham The Old" -> just "Abraham"
        # "Aurora Borealis" -> stays "Aurora Borealis" (both are proper nouns)
        # "Snow White" -> stays "Snow White"
        # Strategy: trim trailing words whose lowercase form is a common
        # English word (articles, adjectives, adverbs, etc.)
        TRIM_LOWER = {
            "the", "a", "an", "in", "on", "at", "as", "or", "and",
            "its", "this", "that", "these", "those", "all", "old",
            "one", "two", "for", "but", "not", "from", "with", "new",
            "first", "second", "third", "last", "next", "other",
            "great", "good", "long", "high", "deep", "early", "late",
            "most", "many", "some", "each", "every", "such",
        }
        parts = raw_term.split()
        while len(parts) > 1 and parts[-1].lower() in TRIM_LOWER:
            parts.pop()
        term = " ".join(parts)
        # Recalculate rest (everything after the trimmed term)
        rest = line[len(term):].strip()
        if len(term) <= 35 and len(rest) >= 10:
            if not is_running_header(term):
                if _is_valid_term(term):
                    return term

    # Pattern 3: Cross-reference: "aureole See halo." or "mandorla See under almond."
    m = re.match(
        r'^([a-z][a-z\s,\'\-]+?)\s+[Ss]ee\s+',
        line
    )
    if m:
        term = m.group(1).strip().rstrip('.,')
        if 2 <= len(term) <= 50:
            return term

    # Pattern 4: lowercase term + parenthetical cross-ref only
    # Matches: "anqa (see also simurg)" with no further text
    m = re.match(
        r'^([a-z][a-z\s,\'\-]+?)\s+\([Ss]ee\s+(?:also\s+)?[^)]+\)',
        line
    )
    if m:
        term = m.group(1).strip().rstrip('.,')
        if 2 <= len(term) <= 50:
            return term

    return None


def extract_entries(doc):
    """Extract all dictionary entries from the PDF using block-level analysis."""
    entries = []
    current_term = None
    current_definition_lines = []
    current_page = 0

    for page_num in range(DICT_START_PAGE, min(DICT_END_PAGE, len(doc))):
        page = doc[page_num]
        page_dict = page.get_text("dict")
        blocks = page_dict.get("blocks", [])

        for block in blocks:
            if block["type"] != 0:  # skip image blocks
                continue

            # Get full block text
            full_text = get_block_text(block).strip()
            if not full_text:
                continue

            first_line = get_block_first_line(block)
            if not first_line:
                continue

            # Skip ALL-CAPS running headers (entire block is a header)
            if is_running_header(full_text):
                continue

            # Skip page numbers
            if is_page_number(full_text.strip()):
                continue

            # Check if this block starts a new entry
            # CRITICAL: we only check the FIRST LINE of the block
            detected_term = detect_entry_heading(first_line)

            if detected_term:
                # Save previous entry
                if current_term and current_definition_lines:
                    definition = ' '.join(current_definition_lines)
                    definition = clean_definition(definition)
                    if definition:
                        is_xref = is_cross_reference(definition)
                        entries.append({
                            "term": current_term,
                            "definition": definition,
                            "page": current_page + 1,  # 1-indexed
                            "is_cross_ref": is_xref,
                        })

                # Start new entry
                current_term = detected_term
                current_page = page_num

                # Extract definition text (everything after the term on first line,
                # plus all remaining lines in this block)
                rest_of_first = first_line[len(detected_term):].strip()

                # Get all lines from the block
                block_lines = []
                for line_obj in block["lines"]:
                    lt = ""
                    for span in line_obj["spans"]:
                        lt += span["text"]
                    block_lines.append(lt.strip())

                # First line's remainder is start of definition
                # Then add lines 2+ from this block
                def_parts = []
                if rest_of_first:
                    def_parts.append(rest_of_first)
                for bl in block_lines[1:]:
                    if bl and not is_running_header(bl) and not is_page_number(bl):
                        def_parts.append(bl)

                current_definition_lines = def_parts

            else:
                # Continuation block for current entry
                if current_term is not None:
                    # Add all lines from this block to the definition
                    for line_obj in block["lines"]:
                        lt = ""
                        for span in line_obj["spans"]:
                            lt += span["text"]
                        lt = lt.strip()
                        if lt and not is_running_header(lt) and not is_page_number(lt):
                            current_definition_lines.append(lt)

    # Don't forget the last entry
    if current_term and current_definition_lines:
        definition = ' '.join(current_definition_lines)
        definition = clean_definition(definition)
        if definition:
            is_xref = is_cross_reference(definition)
            entries.append({
                "term": current_term,
                "definition": definition,
                "page": current_page + 1,
                "is_cross_ref": is_xref,
            })

    return entries


def clean_definition(text):
    """Clean up extracted definition text."""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove soft hyphens
    text = text.replace('\xad', '').replace('\u00ad', '')
    # Fix common OCR artifacts
    text = text.replace('  ', ' ')
    return text


def is_cross_reference(definition):
    """Check if a definition is just a cross-reference."""
    d = definition.strip()
    # "See halo." or "See under almond." or "(see also simurg)"
    if re.match(r'^[Ss]ee\s+', d) and len(d) < 120:
        return True
    if re.match(r'^\([Ss]ee\s+', d) and len(d) < 120:
        return True
    return False


def post_process_entries(entries):
    """Clean up and validate extracted entries."""
    cleaned = []
    seen_terms = set()

    # Additional single-word exclusions: common English words that are
    # definitely not symbol headwords (caught at post-processing stage)
    SINGLE_WORD_EXCLUSIONS = {
        "very", "also", "just", "even", "still", "yet", "only",
        "often", "always", "never", "rather", "quite",
        "traditional", "finally", "similarly", "conversely",
        "originally", "essentially", "generally", "consequently",
        "alternatively", "accordingly", "subsequently", "nevertheless",
        "furthermore", "moreover", "whereas", "whereby", "thereby",
        "nonetheless", "otherwise", "indeed", "certainly",
        "perhaps", "probably", "possibly", "apparently", "recently",
        "clearly", "obviously", "simply", "merely", "purely",
        "primarily", "mainly", "largely", "partly", "partly",
        "already", "sometimes", "everywhere", "anywhere", "nowhere",
    }

    for entry in entries:
        term = entry["term"]
        definition = entry["definition"]

        # Skip very short or garbage terms
        if len(term) < 2:
            continue

        # Skip entries where definition is too short (likely noise)
        if len(definition) < 10 and not entry["is_cross_ref"]:
            continue

        # Skip terms that look like sentence fragments
        if term.endswith(('.', ':', ';')):
            continue

        # Skip terms that are too long to be real headwords
        if len(term) > 60:
            continue

        # Skip single-word terms that are common English (not symbols)
        if len(term.split()) == 1 and term.lower() in SINGLE_WORD_EXCLUSIONS:
            continue

        # Re-validate term structure (catches edge cases missed earlier)
        if not _is_valid_term(term):
            continue

        # Skip duplicate terms (keep first occurrence)
        term_lower = term.lower()
        if term_lower in seen_terms:
            # Might be a continuation - append to previous entry
            for prev in reversed(cleaned):
                if prev["term"].lower() == term_lower:
                    prev["definition"] += " " + definition
                    break
            continue
        seen_terms.add(term_lower)

        cleaned.append(entry)

    return cleaned


def main():
    print(f"Opening PDF: {PDF_PATH}")
    doc = fitz.open(PDF_PATH)
    print(f"  Total pages: {len(doc)}")
    print(f"  Extracting pages {DICT_START_PAGE+1}-{min(DICT_END_PAGE, len(doc))}")
    print()

    # Extract entries
    entries = extract_entries(doc)
    print(f"  Raw entries extracted: {len(entries)}")

    # Post-process
    entries = post_process_entries(entries)
    print(f"  After cleanup: {len(entries)}")

    # Count types
    defs = sum(1 for e in entries if not e["is_cross_ref"])
    xrefs = sum(1 for e in entries if e["is_cross_ref"])
    print(f"  Definitions: {defs}")
    print(f"  Cross-references: {xrefs}")

    # Show first few entries
    print()
    print("First 10 entries:")
    for e in entries[:10]:
        xr = " [XREF]" if e["is_cross_ref"] else ""
        defn = e['definition'][:80].encode('ascii', 'replace').decode()
        print(f"  p.{e['page']:4d}  {e['term'][:35]:35s}{xr}  {defn}...")

    # Show some entries from the middle
    mid = len(entries) // 2
    print()
    print(f"Entries around #{mid}:")
    for e in entries[mid:mid+5]:
        xr = " [XREF]" if e["is_cross_ref"] else ""
        defn = e['definition'][:80].encode('ascii', 'replace').decode()
        print(f"  p.{e['page']:4d}  {e['term'][:35]:35s}{xr}  {defn}...")

    # Show last few entries
    print()
    print("Last 5 entries:")
    for e in entries[-5:]:
        xr = " [XREF]" if e["is_cross_ref"] else ""
        defn = e['definition'][:80].encode('ascii', 'replace').decode()
        print(f"  p.{e['page']:4d}  {e['term'][:35]:35s}{xr}  {defn}...")

    # Save output
    data = {
        "metadata": {
            "source": "Dictionary of Symbols (reprint edition)",
            "total_entries": len(entries),
            "entries_with_definitions": defs,
            "cross_references": xrefs,
        },
        "entries": entries,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"  File size: {os.path.getsize(OUTPUT_PATH) / 1024:.0f} KB")

    doc.close()


if __name__ == "__main__":
    main()
