# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types


MODEL = "gemini-2.5-flash"


async def generate_memories_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        pass
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    q = query.lower()
    if "sf" in q or "san francisco" in q:
        tz_identifier = "America/Los_Angeles"
    elif "ny" in q or "new york" in q:
        tz_identifier = "America/New_York"
    elif "london" in q:
        tz_identifier = "Europe/London"
    elif "tokyo" in q:
        tz_identifier = "Asia/Tokyo"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


import copy
import threading
from google.adk.code_executors import AgentEngineSandboxCodeExecutor

# Monkey-patch AgentEngineSandboxCodeExecutor to handle thread locks during cloudpickle & deepcopy deployment operations
def _deepcopy(self, memo):
    cls = self.__class__
    result = cls.__new__(cls)
    memo[id(self)] = result

    d = {}
    for k, v in self.__dict__.items():
        if k == "_agent_engine_creation_lock":
            continue
        d[k] = copy.deepcopy(v, memo)
    object.__setattr__(result, "__dict__", d)
    result._agent_engine_creation_lock = threading.Lock()

    if hasattr(self, "__pydantic_private__") and self.__pydantic_private__:
        priv = {}
        for pk, pv in self.__pydantic_private__.items():
            if pk == "_agent_engine_creation_lock":
                continue
            try:
                priv[pk] = copy.deepcopy(pv, memo)
            except Exception:
                priv[pk] = pv
        object.__setattr__(result, "__pydantic_private__", priv)
    return result


def _getstate(self):
    state = self.__dict__.copy()
    state.pop("_agent_engine_creation_lock", None)
    return state


def _setstate(self, state):
    self.__dict__.update(state)
    self._agent_engine_creation_lock = threading.Lock()


AgentEngineSandboxCodeExecutor.__deepcopy__ = _deepcopy
AgentEngineSandboxCodeExecutor.__getstate__ = _getstate
AgentEngineSandboxCodeExecutor.__setstate__ = _setstate


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from .a2ui_utils import a2ui_callback
from .firestore_tools import (
    add_to_watchlist,
    get_watchlist,
    update_watchlist_item,
)
from .image_tools import generate_concept_poster
from .media_tools import search_books
from .rag_tools import search_complete_herbal

REASONING_ENGINE_NAME = "projects/356173146024/locations/us-east1/reasoningEngines/3668023566818869248"
SANDBOX_RESOURCE_NAME = "projects/356173146024/locations/us-east1/reasoningEngines/3668023566818869248/sandboxEnvironments/43998057297084416"

code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    agent_engine_resource_name=REASONING_ENGINE_NAME,
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description="You are a helpful AI assistant and personalized concierge for PlotTwist (books, movies, recommendation lists, watchlist management, concept art).",
    workflow_description=(
        "ALWAYS format your response as an A2UI JSON array whenever the user asks for "
        "watchlist items, recommendations, book search results, movie details, or item lists. "
        "Analyze the request, execute tools if needed, and return structured A2UI JSON."
    ),
    ui_description=(
        "CRITICAL MANDATE: You MUST output an A2UI JSON surface array whenever presenting "
        "watchlist items, search results, recommendations, or item summaries. "
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

base_instruction = (
    "DO NOT mention or reference Frozen, Frozen Storybook, Olaf, or Sven unless explicitly requested in the user's current message."
    "\n\nWhen the user asks for a brand new book concept blending Interstellar and Blade Runner (or similar sci-fi noir prompt):"
    "\n1. Title the book 'Neon Horizon'."
    "\n2. Provide a well-proportioned 3-Chapter Outline (Chapter 1: The Event Horizon Case, Chapter 2: Echoes in Neon, Chapter 3: Singularity Noir) with 2 to 3 engaging, well-paced sentences per chapter (neither too brief nor overly verbose), and brief Character Profiles (Detective Jax Vance, Dr. Elena Thorne)."
    "\n3. Call generate_concept_poster('Neon Horizon') to generate the concept poster."
    "\n4. Call add_to_watchlist('Neon Horizon', 'book', 'Plan to Read') to save the new book concept to Google Cloud Firestore."
    "\n5. Present the book concept cleanly, and ALWAYS include the generated poster image markdown link ![Concept Poster](URL) from the tool response."
    "\n\nYou remember all of the user's stated preferences and facts from previous conversations. "
    "Use search_books to look up real book details, synopses, and information. "
    "Use search_complete_herbal to search Nicholas Culpeper's 'The Complete Herbal' ebook corpus for herbal remedies, remedies for ailments, and plant descriptions. "
    "Use generate_concept_poster to generate high-quality concept posters or cover art for books, movies, or story concepts. "
    "Use get_watchlist to view items, add_to_watchlist to save new books/movies to Firestore, and update_watchlist_item to update status or ratings. "
    "You can execute Python code safely in a sandbox using code execution when calculations, data manipulation, or algorithmic analysis are required."
)

AGENT_INSTRUCTION = f"{a2ui_instruction}\n\nAdditional Instructions:\n{base_instruction}"


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AGENT_INSTRUCTION,
    code_executor=code_executor,
    tools=[
        get_weather,
        get_current_time,
        PreloadMemoryTool(),
        search_books,
        search_complete_herbal,
        generate_concept_poster,
        add_to_watchlist,
        get_watchlist,
        update_watchlist_item,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

