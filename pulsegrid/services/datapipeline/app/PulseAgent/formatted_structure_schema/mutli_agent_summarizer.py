"""Structured output schemas for the multi-agent summarizer."""

from pydantic import BaseModel, ConfigDict, Field, RootModel


class SimilaritiesResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    similarities: list[str] = Field(
        description="One complete sentence per fact supported by 2+ sources; [] if none."
    )


class DissimilaritySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    difference_topic: str = Field(description="Short label for the comparison topic.")
    how_sources_report_it: str = Field(
        description="State what each source reports; preserve attribution and scope."
    )


class DissimilaritiesResponseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dissimilarities: list[DissimilaritySchema] = Field(
        description="Material differences or contradictions; silence is not denial; [] if none."
    )


class UltimateSummarySchema(RootModel[str]):
    root: str = Field(
        description="Concise source-grounded summary in plain text; preserve attribution and scope."
    )