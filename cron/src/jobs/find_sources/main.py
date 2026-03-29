import json

from context import TaskContext
from types_ import TaskPayload


def task(payload: TaskPayload, ctx: TaskContext):
    text = payload["text"]
    user_id = payload["user_id"]

    print(f"[find_sources] Processing text:\n{text}")
    response_json = ctx.llm.ask_json_with_search(
        instructions="""
You are an expert fact-checker and forensic linguist. Your task is to analyze the provided text for misinformation, factual inaccuracies, and manipulative rhetoric using external search grounding.

### OPERATIONAL PROTOCOL:
1. **Search & Verify**: For every significant claim in the article, use the Google Search tool to find corroborating or debunking evidence from reputable sources.
2. **Research Log**: Before providing the structured data, write a brief "Research Log" section. In this section, explain your findings for each claim. This is crucial for grounding accuracy.
3. **JSON Generation**: After the Research Log, provide a final analysis in a strict JSON format.

### JSON SCHEMA:
The JSON must be an array of objects. Each object must contain:
- "citation": The exact verbatim text from the article.
- "status": One of ["Verified", "Misleading", "False", "Unverified"].
- "category": One of ["Factual Error", "Logical Fallacy", "Omission of Context", "Emotional Manipulation", "Accurate"].
- "analysis": A concise (1-2 sentence) explanation of why this status was assigned.
- "sources": A list of URLs used to verify this specific citation.

### Constraints:
1. If a claim is truthful, still include it but note its accuracy.
2. If no misinformation is found, return an empty list: [].
3. "citation" must be the exact, verbatim text from the article.

### OUTPUT FORMAT:
[Research Log]
(Your text-based analysis here)

[JSON Data]
```json
[
  {
    "citation": "...",
    "status": "...",
    "category": "...",
    "analysis": "...",
    "sources": ["..."]
  }
]
        """,
        input_text=text
    )

    print(f"[find_sources] LLM response:")
    print(json.dumps(response_json, indent=4))

    database = ctx.db.get_database("factify_ai")
    collection = database["find_sources"]
    doc = {
        "text": text,
        "result": response_json,
        "user_id": user_id
    }
    result = collection.insert_one(doc)

    return result.inserted_id
