import json

from context import TaskContext
from types_ import TaskPayload


def task(payload: TaskPayload, ctx: TaskContext):
    text = payload["text"]
    user_id = payload["user_id"]

    print(f"[analyze_manipulation] Processing text:\n{text}")
    response_json = ctx.llm.ask_json(
        instructions="""
You are an expert linguistic analyst specializing in forensic linguistics, media literacy, and the detection of cognitive biases and manipulative rhetoric.

Your task is to analyze the provided text for specific categories of bias and manipulation. You must output the results strictly as a JSON object. Do not include any conversational filler, markdown formatting outside of the JSON block, or introductory/concluding remarks.

### Categories to Detect:
1. **Loaded Language:** Use of emotive or high-stakes words to influence the reader's emotions (e.g., "vicious," "heroic," "disastrous").
2. **False Dilemma (Black-and-White Thinking):** Presenting only two extreme options when more exist.
3. **Appeal to Authority/Fear:** Citing vague authorities or using scare tactics to bypass critical thinking.
4. **Ad Hominem:** Attacking the character of a person rather than their argument.
5. **Framing Bias:** Presenting information in a way that highlights certain facts while ignoring others to steer the narrative.
6. **Selection/Omission Bias:** Leaving out crucial context or opposing viewpoints to create a one-sided argument.
7. **Sensationalism:** Over-hyping events or using hyperbole to provoke a reaction.

### Output Instructions:
- Every key in the root object must be one of the categories listed above.
- If a category is not detected, do not include it in the JSON.
- For each category found, the value must be an object where the keys are the exact "citations" from the text (do not put the citations in additional quotation marks).
- Each citation key must map to a list of concise, analytical reasonings.
- Reasonings must be brief (1-2 sentences) and objective.

### JSON Structure:
{
  "Category Name": {
    "Exact citation from text": [
      "Concise reasoning 1",
      "Concise reasoning 2"
    ]
  }
}
        """,
        input_text=text
    )

    print(f"[analyze_manipulation] LLM response:")
    print(json.dumps(response_json, indent=4))

    database = ctx.db.get_database("factify_ai")
    collection = database["analysis_manipulation"]
    doc = {
        "text": text,
        "result": response_json,
        "user_id": user_id
    }
    result = collection.insert_one(doc)

    return result.inserted_id
