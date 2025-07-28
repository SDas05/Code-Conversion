def build_prompt(code: str, source_lang: str, target_lang: str, context: dict = None) -> str:
    """
    Build a prompt for LLM-based code conversion from source_lang to target_lang.
    Includes optional context for accuracy.
    """
    context_block = ""
    if context:
        context_block = f"Here is some additional context that may help:\n{context.get('summary', '')}\n"

    prompt = f"""You are an expert software engineer helping to translate code.

Convert the following {source_lang} code into {target_lang}.
Preserve all functionality, structure, and logic.
{context_block}

### BEGIN {source_lang} CODE
{code}
### END {source_lang} CODE

Now, write the equivalent in {target_lang} only.
Respond with ONLY the {target_lang} code, no commentary.
"""
    return prompt
