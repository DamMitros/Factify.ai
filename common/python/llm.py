import os
import json
import re

from openai import OpenAI as OpenAIClient
from google.genai import Client as GeminiClient, types

LM_USE_GEMINI = os.getenv("LM_USE_GEMINI", "false").lower() == "true"
LM_API_BASE_URL = os.getenv("LM_API_BASE_URL")
LM_API_KEY = os.getenv("LM_API_KEY")
LM_MODEL = os.getenv("LM_MODEL")


class LLM:
    _openai_client: OpenAIClient | None = None
    _gemini_client: GeminiClient | None = None

    _model_id: str

    def __init__(self):
        print(f"[LLM] {LM_MODEL=}")
        self._model_id = LM_MODEL

        if LM_USE_GEMINI:
            print("[LLM] ✨ Using Gemini")
            self._gemini_client = GeminiClient(api_key=LM_API_KEY)
        else:
            print(f"[LLM] {LM_API_BASE_URL=}")
            self._openai_client = OpenAIClient(base_url=LM_API_BASE_URL, api_key=LM_API_KEY)

    def _ask_openai_client(self, instructions: str, input_text: str) -> str:
        response = self._openai_client.responses.create(
            model=self._model_id,
            instructions=instructions,
            input=input_text,
        )

        return response.output_text

    def _ask_gemini(self, instructions: str, input_text: str) -> str:
        response = self._gemini_client.models.generate_content(
            model=self._model_id,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
            ),
            contents=input_text,
        )

        return response.text

    def _ask_gemini_with_search(self, instructions: str, input_text: str) -> str:
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        response = self._gemini_client.models.generate_content(
            model=self._model_id,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                tools=[grounding_tool],
            ),
            contents=input_text,
        )

        print(f"[LLM] 🎯 Candidates count: {len(response.candidates)}")
        for i, candidate in enumerate(response.candidates):
            print(f"[LLM] Candidate {i}: {candidate.grounding_metadata}")

        return response.text

    def ask(self, instructions: str, input_text: str) -> str:
        if self._openai_client is not None:
            return self._ask_openai_client(instructions, input_text)

        return self._ask_gemini(instructions, input_text)

    def ask_json(self, instructions: str, input_text: str) -> dict | list:
        response_text = self.ask(instructions, input_text)

        try:
            return json.loads(response_text)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[LLM] ⚠️ Failed to parse JSON response:\n{response_text}")

            raise e

    def ask_with_search(self, instructions: str, input_text: str) -> str:
        if self._gemini_client is None:
            raise Exception("Gemini is required for search functionality")

        return self._ask_gemini_with_search(instructions, input_text)

    def ask_json_with_search(self, instructions: str, input_text: str) -> dict | list:
        if self._gemini_client is None:
            raise Exception("Gemini is required for search functionality")

        response_text = self.ask_with_search(instructions, input_text)

        json_match = re.search(r"```json\s+(.*?)\s+```", response_text, re.DOTALL)

        if json_match:
            json_string = json_match.group(1)
            print(f"[LLM] 🙏 Found JSON string in response:\n{json_string}")

            try:
                return json.loads(json_string)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"[LLM] ⚠️ Failed to parse JSON from response:\n{response_text}")

                raise e
        else:
            print(f"[LLM] ⚠️ No JSON found in response:\n{response_text}")

            raise Exception("No JSON found in response")
