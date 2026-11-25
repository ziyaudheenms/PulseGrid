"""
This agent analyzes similarities, conflicts, and framing across every article in a collection.

This prompt is used for collections with up to two articles.
"""


def single_agent_summarizer_task_spec_prompt() -> str:
    task_spec_prompt = """

    TASK-SPECIFIC INSTRUCTIONS:
    Analyze the complete set of supplied articles as one collection. Do not select only the
    most detailed, recent, or apparently reliable article as your basis.

    1. COMPLETE SOURCE INVENTORY AND COMPARISON
       - Identify every supplied article by its outlet/source name. Treat each article as a
         distinct source, even if several articles report the same event.
       - Read the full text of every article before writing the result. Compare every source
         against every other source on the material claims; do not stop after finding one
         shared fact or one disagreement.
       - For each important claim, check which sources explicitly support it, qualify it,
         contradict it, or do not address it. Reconcile the collection as a whole rather
         than describing articles independently.
       - Before finalizing, verify that every supplied source was considered against the
         rest of the collection. Do not invent a finding just to mention a source that
         contributes no material agreement, disagreement, or framing difference.
       - Base the result only on the supplied articles. Do not add outside facts, inferred
         explanations, or claims absent from the source text.

    2. SHARED FACTS
       - Include only material claims explicitly supported by at least two articles.
       - Combine equivalent wording without losing meaningful differences in dates,
         quantities, attribution, certainty, or scope.
       - Make source coverage clear in each item (name the supporting sources when the
         input provides names). Do not imply that every source supports a fact if one or
         more do not.
       - Write shared_facts point by point: each array item must be one standalone,
         complete sentence describing one distinct shared fact. Put separate facts in
         separate items; do not combine unrelated facts into one sentence or paragraph.
       - Do not put an uncorroborated claim here merely because it appears plausible.

    3. FACTUAL CONFLICTS AND QUALIFICATIONS
       - Report material factual disagreements, including incompatible figures, dates,
         causes, sequences, or descriptions. For each, state what each relevant source
         reports and identify the source by its supplied name.
       - Preserve the conditions attached to figures and claims (for example, peak-load
         tests versus average normal traffic). Do not collapse measurements from different
         conditions into one directly comparable number.
       - Distinguish an actual contradiction from different levels of detail, different
         measurement scopes, or a claim that another article simply does not mention.
         Silence is not a denial: describe a source as not specifying a detail only when
         that absence is relevant, and never frame it as contradictory evidence.
       - Do not force a conflict where the articles are compatible. If there are no
         material factual conflicts, return an empty factual_conflicts array.

    4. FRAMING AND SUMMARY
       - Assess meaningful differences in emphasis or interpretation only when the text
         supports them. Describe each outlet's angle neutrally; do not infer intent or
         editorial bias from omission alone.
       - Write unified_summary as a detailed but crisp synthesis, typically 2-4 sentences.
         Explain the central event, its reported context or impact, and the most important
         evidence or qualification needed to understand how the sources compare. Attribute
         source-specific figures or claims, and preserve the conditions under which they
         were reported. Avoid vague generalities, repetition of the arrays, and unsupported
         conclusions; every sentence should add material information.
       - When multiple sources report different quantities for the same metric under
         comparable conditions, summarize the span using the lowest and highest reported
         values (for example, reports of 45%, 50%, and 55% become "reported estimates
         ranged from 45% to 55%"). Make clear that this is the range of source-reported
         figures, not a single verified measurement, and retain relevant attribution.
       - Do not combine quantities into one range when their metrics, populations,
         timeframes, methods, or conditions differ. In that case, keep the figures
         distinct and explain the relevant difference in scope. Preserve the individual
         source figures and qualifications in factual_conflicts when applicable.
       - Ensure every specific claim and comparison is traceable to the supplied sources.

    5. REQUIRED OUTPUT
       Return only valid JSON with exactly these top-level keys and value types:
       - "unified_summary": a string.
       - "shared_facts": an array of strings.
       - "factual_conflicts": an array of objects. Each object has exactly:
         "conflict_topic" (string) and "how_sources_report_it" (string).
       Do not add markdown fences, introductory text, citations to outside material, or
       additional keys. Use [] for an empty array. Keep source names and relevant
       qualifications in the strings so readers can trace the comparison.

    FEW-SHOT EXAMPLE
    The following illustrates the required structure and the distinction between
    differently scoped measurements and an article that does not report a number.

    Input comparison:
    - Source A says Discord moved its Read States service from Go to Rust and reports a
      40% p99 tail-latency reduction in peak-load tests.
    - Source B says Discord moved its Read States service from Go to Rust and reports a
      25% average latency reduction across normal traffic.
    - Source C says Discord moved its Read States service from Go to Rust but gives no
      latency-reduction percentage.
    - The collection explains that Go garbage-collection cycles caused regular latency
      spikes.

    Output:
    {
      "unified_summary": "Discord migrated its Read States service from Go to Rust after Go's garbage-collection cycles caused regular latency spikes.",
      "shared_facts": [
        "The sources report that Discord moved its Read States service from Go to Rust.",
        "The sources attribute regular latency spikes to Go's garbage-collection cycles."
      ],
      "factual_conflicts": [
        {
          "conflict_topic": "Reported latency improvement",
          "how_sources_report_it": "Source A reports a 40% reduction in p99 tail latency in peak-load tests, while Source B reports a 25% average reduction across normal traffic. These figures use different measures and conditions, so they are not necessarily contradictory or directly comparable. Source C does not report a percentage; that omission is not a conflicting claim."
        }
      ]
    }

    Apply this method and output structure to the actual supplied collection, not to the
    example. Include every supplied source in the comparison process.
    """
    return task_spec_prompt