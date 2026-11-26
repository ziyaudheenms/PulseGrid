"""Structured response schema for the single-agent summarizer."""

from pydantic import BaseModel, ConfigDict, Field


class DissimilaritySchema(BaseModel):
    """A material difference or factual contradiction between sources."""

    model_config = ConfigDict(extra="forbid")

    difference_topic: str = Field(description="Short label for the comparison topic.")
    how_sources_report_it: str = Field(
        description="State what each source reports; preserve attribution and scope."
    )


class SingleAgentresponseSchema(BaseModel):
    """The complete summary and source comparison returned by the agent."""

    model_config = ConfigDict(extra="forbid")

    unified_summary: str = Field(
        description="Synthesize the key event in 2–4 source-grounded sentences; retain attribution."
    )
    shared_facts: list[str] = Field(
        description="One complete sentence per fact supported by 2+ sources; name sources; [] if none."
    )
    dissimilarities: list[DissimilaritySchema] = Field(
        description="Material differences or contradictions; silence is not denial; [] if none."
    )
