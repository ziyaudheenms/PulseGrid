import re
import spacy

# Load spaCy once globally in your pipeline
nlp = spacy.load("en_core_web_sm")

# Universal regex patterns for numbers/scores/currencies across all categories
UNIVERSAL_PATTERNS = [
    r"\b\d+(?:\.\d+)?%",                              # Percentages (e.g., 14.5%)
    r"[$€£₹¥]\s?\d+(?:[.,]\d+)?(?:\s?(?:million|billion|trillion|cr|crore|lakh|m|b|bn))?", # Currencies
    r"\b\d+[:/-]\d+\b",                               # Scores, ratios, resolutions (e.g., 3-2, 16:9, 8/10)
    r"\bv?\d+(?:\.\d+){1,3}\b",                       # Software/patch versions (e.g., v2.4.1, Patch 1.04)
    r"\b\d+(?:\.\d+)?x\b",                            # Multipliers (e.g., 10x faster)
]

# Concrete Named Entity labels to retain
VALID_ENTITY_LABELS = {"PERSON", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "LAW", "WORK_OF_ART"}


def clean_scraped_text(text: str) -> str:
    """Removes common scraping artifacts and normalizes quotes/dashes."""
    # Remove trailing scraped metadata lines
    text = re.sub(r"(?i)(related topics|published\s*\d+.*|read more:.*)$", "", text, flags=re.MULTILINE)
    # Normalize curly quotes and dashes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("—", " ")
    return re.sub(r"\s+", " ", text).strip()


def deduplicate_entities(raw_entities: set[str]) -> set[str]:
    """Merges partial name aliases (e.g., 'iraola' into 'andoni iraola')."""
    sorted_ents = sorted(raw_entities, key=len, reverse=True)
    unique_ents = []
    for ent in sorted_ents:
        # Only add if it's not a standalone word substring of an already kept longer entity
        if not any(re.search(rf"\b{re.escape(ent)}\b", kept) for kept in unique_ents):
            unique_ents.append(ent)
    return set(unique_ents)


def compute_fact_and_entity_density(raw_text: str, category: str = "general") -> dict:
    """
    Computes Fact & Entity Density across Technical, Cinema, Gaming, and News.
    Returns raw counts, density per 100 words, and a normalized 0.0 - 1.0 score.
    """
    text = clean_scraped_text(raw_text)
    doc = nlp(text)

    # 1. Total meaningful words (exclude punctuation & whitespace)
    words = [token.text for token in doc if not token.is_punct and not token.is_space]
    total_words = len(words)
    if total_words == 0:
        return {"score": 0.0, "density_per_100": 0.0, "entities": [], "quantities": [], "concepts": []}

    # 2. Extract & Deduplicate Named Entities (Who, Where, What)
    raw_entities = set()
    for ent in doc.ents:
        if ent.label_ in VALID_ENTITY_LABELS:
            cleaned_ent = re.sub(r"^the\s+", "", ent.text.lower().strip())
            if len(cleaned_ent) > 1:
                raw_entities.add(cleaned_ent)
    unique_entities = deduplicate_entities(raw_entities)

    # 3. Extract Quantitative Anchors (Universal POS + Regex)
    unique_quantities = set()

    # 3a. Built-in spaCy numeric entities (catches spelled-out numbers like "three servers", "18 years")
    for ent in doc.ents:
        if ent.label_ in {"QUANTITY", "MONEY", "PERCENT", "TIME"}:
            unique_quantities.add(ent.text.lower().strip())

    # 3b. Universal NUM + NOUN/PROPN pairing (catches "60 FPS", "22 seconds", "165 minutes", "4K")
    for i in range(len(doc) - 1):
        if doc[i].pos_ == "NUM" and doc[i + 1].pos_ in {"NOUN", "PROPN"}:
            pair = f"{doc[i].text.lower()} {doc[i + 1].lemma_.lower()}"
            unique_quantities.add(pair)

    # 3c. Universal Symbol Regex (catches "3-2", "14.5%", "$120 million", "v2.4")
    for pattern in UNIVERSAL_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            unique_quantities.add(match.group(0).lower().strip())

    # 4. Extract Multi-Word Domain Concepts (Crucial for Technical & Gaming depth)
    # Catches technical compound nouns like "search crawlers", "ray tracing", "frame pacing"
    domain_concepts = set()
    for chunk in doc.noun_chunks:
        # Keep chunks of 2-3 content words with no pronouns/determiners
        content_tokens = [t.lemma_.lower() for t in chunk if t.pos_ in {"NOUN", "PROPN", "ADJ"} and not t.is_stop]
        if 2 <= len(content_tokens) <= 3:
            phrase = " ".join(content_tokens)
            # Exclude if already captured as a Named Entity
            if phrase not in unique_entities:
                domain_concepts.add(phrase)

    # 5. Calculate Weighted Fact Count & Smoothed Density
    # Domain concepts get 0.5 weight in Technical/Gaming, 0.25 in other categories
    concept_weight = 0.5 if category.lower() in {"technical", "gaming"} else 0.25
    total_fact_units = len(unique_entities) + len(unique_quantities) + (concept_weight * len(domain_concepts))

    # +30 smoothing prevents 20-word tweets/blurbs from getting artificially maxed out
    smoothed_density = (total_fact_units / (total_words + 30)) * 100

    # Normalize to 0.0 - 1.0 (12.0 density units per 100 words = 1.0 benchmark ceiling)
    normalized_score = min(1.0, round(smoothed_density / 12.0, 3))

    return {
        "score": normalized_score,
        "density_per_100": round(smoothed_density, 2),
        "total_words": total_words,
        "entity_count": len(unique_entities),
        "quantity_count": len(unique_quantities),
        "concept_count": len(domain_concepts),
        "entities": sorted(unique_entities),
        "quantities": sorted(unique_quantities),
        "concepts": sorted(domain_concepts)[:10],  # Top 10 sample concepts
    }


# --- Quick Test on Your X Snippet ---
if __name__ == "__main__":
    sample_x = """
    The November 3 midterm results gave Democrats full control of Congress, setting the stage for what could be one of the most divided U.S. governments this decade, with Republicans in the White House.\nTuesday’s results suggest that anger over data centers, the large facilities that house the computers powering AI, is becoming a political force. With Democrats now in control of Congress, that could lead to new limits on where data centers can be built and how much say local communities have.\nData centers became a ballot-box issue in various states. An NBC exit poll showed how concerned voters are about AI: More than half of respondents believe that AI will do more harm than good, while almost 80% are against the building of data centers in their neighborhoods. Almost 60%, meanwhile, said data centers were a crucial or major factor in their vote. Nadine Smith, president and CEO of the racial justice organization Color of Change, called Tuesday’s election a referendum on “who this economy is built for.”\n“National security matters,” Smith said, referring to a common argument from data center supporters that the infrastructure is essential for the U.S. to stay ahead in war and in its rivalry with China. “And so do the families in South Memphis breathing exhaust from the gas turbines powering an AI supercomputer.” (She was referring to xAI’s data center in Memphis, Tennessee, which uses gas turbines for power.)\nVoters in several states pushed back against the AI buildout, even as pro-AI super PACs spent millions hoping to sway them this midterm. The anti-data center backlash was especially felt in states like Ohio, where OpenAI has eyed a $500 billion data center, backed by more than $100 billion in financing from Nvidia. In fact, the Ohio county where Meta had planned a 700,000-square-foot facility just passed a ban on data centers, and local communities across the state overwhelmingly voted against data center buildout measures.\nAnalysts at Morgan Stanley predict that Democratic governor-elect Amy Acton will also pose a major risk to Ohio’s data center buildout. Elsewhere, candidates in Texas, Maine, Michigan, Nevada, Georgia, and South Carolina all won seats after taking a stance against the rapid buildout of data centers. “It is clear that money does not buy outcomes,” said Anshi Bhatt, a tech and policy researcher, adding that in modern politics, creating a “local villain” is one way to build campaign momentum.\nLikely next steps include more construction moratoriums or requiring data centers to pay for their own power grid upgrades instead of passing those costs on to nearby communities. Goldman Sachs, in fact, predicts data center construction delays in states like Georgia and Texas because of Democratic gains.\nDemocratic control of Congress could also improve the odds for bills like the one Sen. Bernie Sanders and Rep. Alexandria Ocasio-Cortez introduced earlier this year, though any such bill would also face a possible veto. It proposes a nationwide moratorium on new data centers until Congress adds new guardrails and ensures that the buildout does not raise electricity costs, harm the environment, or proceed without community approval.\nThere are also bills like the GRID Savings Act, proposed by New Mexico Sen. Martin Heinrich, which would prevent grid infrastructure costs from being passed on to communities during large AI data center buildouts.\nThe environment is also a major concern, especially at xAI’s data center in Memphis and at the data centers throughout Virginia, known as the world capital of data centers, where gas turbines are used for power. Maia Woluchem, program director at Data & Society, a nonprofit research group, believes that changes to energy regulations, land rights, and other environmental policies could affect the data center buildout, especially as congressional Democrats look further into the Trump administration’s rollback of certain energy protections, as the New York Times reported they might.\n“Regardless of federal action, I could imagine that we will see additional movement at the state and local level, given the momentum that’s been building from the ground up,” Woluchem continued, citing governor-elect Gina Hinojosa, who supports a statewide moratorium on data centers, as an example. Both Hinojosa and Gov. Greg Abbott called for some limits, but Hinojosa centered much of her campaign on opposing data centers, a notable choice in Texas, whose electrical grid has proved vulnerable over the past decade.\nBut the hard part is still to come. Smith, for example, is now expecting a fight, or even more executive orders, to bypass what Congress is now likely to block. “Even among Democrats, a blanket freeze is contested,” she said, referring to some Democrats’ worry that a moratorium could slow AI progress and hurt national security.\nShe also expects AI lobbyists to start calling lawmakers. “Democrats ran on making Big Tech pay,” Smith said. “Our job is to make sure they remember it once the cameras leave.”\nThe backlash runs deeper than the buildings themselves, which aren’t new. One private equity executive told me recently that people don’t necessarily hate data centers, but rather AI, and that data centers have become a stand-in for people’s fears and anxieties about the technology. “It does look like the results are pointing to a real frustration with tech power at minimum,” Woluchem said, noting that this is also a bipartisan issue.\nFor the past month, people have told me they are worried about data centers’ effect on the environment and about their lack of say in whether they’re built.\nAmazon, for example, built a data center in Gilroy, California, without many residents knowing, by satisfying a 45-year-old zoning law. Vague or outdated zoning laws, along with requirements that local officials sign nondisclosure agreements (NDAs) barring them from discussing data center projects, have only fueled people’s outrage about the buildout. Data centers have also received billions in tax breaks, and although many tech companies have touted the benefits, such as jobs and community programs, for many people, that simply wasn’t enough.\nPeople want to know they still have a say in what happens in their communities. Many also fear that AI buildouts will mainly enrich a few wealthy people while their communities suffer and living costs rise.\n“If AI infrastructure is truly a national priority, then the companies building it can afford to pay for their own power, meet clean air standards, disclose what they use, and build with the consent of the people who live next door,” Smith said. “Families should never be subsidizing the richest corporations in history through their utility bills.”
    """
    result = compute_fact_and_entity_density(sample_x, category="technical")
    for k, v in result.items():
        print(f"{k}: {v}")
