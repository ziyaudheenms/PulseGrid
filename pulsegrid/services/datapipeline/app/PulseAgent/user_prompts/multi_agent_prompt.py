"""User-prompt templates for multi-agent article comparison and summarization."""


def multi_agent_comparison_user_prompt(
    category_details: str,
    articles_details: str,
) -> str:
    return f"""Category Details:
{category_details}

Source Articles:
{articles_details}
"""


def multi_agent_summary_user_prompt(
    category_details: str,
    articles_details: str,
    similarities: str,
    dissimilarities: str,
) -> str:
    return f"""Category Details:
{category_details}

Source Articles:
{articles_details}

Similarities:
{similarities}

Dissimilarities:
{dissimilarities}
"""
