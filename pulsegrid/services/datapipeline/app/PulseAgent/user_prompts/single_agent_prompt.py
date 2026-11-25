"""User-prompt template for single-agent article analysis."""


def single_agent_user_prompt(category_details: str, articles_details: str) -> str:
    return f"""Category Details:
                {category_details}

                Source Articles:
                {articles_details}
    """
