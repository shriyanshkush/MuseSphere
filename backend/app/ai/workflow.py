import logging
from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Try importing LangGraph and Google Generative AI
try:
    import google.generativeai as genai
    from langgraph.graph import END, StateGraph
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


@dataclass
class AgentResult:
    """Structured response output from the AI workflow."""
    intent: str
    response: str
    language: str = "en"


class AgentState(TypedDict):
    """LangGraph state structure shared across routing nodes."""
    message: str
    language: str
    context: str
    intent: str
    response: str


class MuseAgentWorkflow:
    """
    Stateful conversational agent workflow built with LangGraph and Google Gemini AI.
    Routes queries across specialized domain nodes (booking, recommendations, payment,
    knowledge base RAG, and visitor support). Falls back seamlessly to offline
    rule-based routing when Gemini API key is omitted during local development.
    """
    def __init__(self):
        self.settings = get_settings()
        self.graph = None
        self.model = None
        self._init_workflow()

    def _init_workflow(self) -> None:
        """Initialize Google Gemini model and LangGraph state graph nodes."""
        if HAS_GENAI and self.settings.gemini_api_key and self.settings.gemini_api_key != "demo_key":
            try:
                genai.configure(api_key=self.settings.gemini_api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.graph = self._build_langgraph()
                logger.info("LangGraph + Google Gemini AI agent workflow initialized successfully.")
            except Exception as exc:
                logger.warning("Could not initialize Gemini AI model (%s). Using offline fallback.", exc)
                self.graph = None
        else:
            logger.info("Gemini API key not configured or set to demo. Using deterministic offline agent router.")

    def _build_langgraph(self) -> Any:
        """Construct the LangGraph state machine structure."""
        workflow = StateGraph(AgentState)

        # Define processing nodes
        workflow.add_node("detect_intent", self._node_detect_intent)
        workflow.add_node("generate_response", self._node_generate_response)

        # Define transitions
        workflow.set_entry_point("detect_intent")
        workflow.add_edge("detect_intent", "generate_response")
        workflow.add_edge("generate_response", END)

        return workflow.compile()

    def _node_detect_intent(self, state: AgentState) -> Dict[str, Any]:
        """LangGraph node: Classifies visitor query intent using Gemini."""
        prompt = (
            "Classify the following visitor query into exactly one of these categories: "
            "booking, recommendation, payment, knowledge, support.\n\n"
            f"Query: \"{state['message']}\"\n\n"
            "Return only the single category word in lowercase without punctuation."
        )
        try:
            res = self.model.generate_content(prompt)
            intent = res.text.strip().lower()
            if intent not in {"booking", "recommendation", "payment", "knowledge", "support"}:
                intent = "support"
        except Exception:
            intent = self._fallback_detect_intent(state["message"])
        return {"intent": intent}

    def _node_generate_response(self, state: AgentState) -> Dict[str, Any]:
        """LangGraph node: Generates context-aware reply using Gemini."""
        prompt = (
            f"You are MuseSphere, an intelligent, helpful museum assistant.\n"
            f"Visitor Intent: {state['intent']}\n"
            f"Target Language Code: {state['language']}\n"
            f"Retrieved Museum Knowledge Base Context:\n{state.get('context', 'No extra documents.')}\n\n"
            f"Visitor Query: \"{state['message']}\"\n\n"
            "Provide a concise, polite, and accurate response to the visitor in their target language."
        )
        try:
            res = self.model.generate_content(prompt)
            return {"response": res.text.strip()}
        except Exception:
            return {"response": self._fallback_generate_response(state["intent"], state["message"])}

    def _fallback_detect_intent(self, text: str) -> str:
        """Rule-based intent classifier for offline fallback."""
        lowered = text.lower()
        if any(w in lowered for w in ["book", "ticket", "reserve", "slot"]):
            return "booking"
        if any(w in lowered for w in ["recommend", "exhibit", "suggest", "popular", "gallery"]):
            return "recommendation"
        if any(w in lowered for w in ["pay", "razorpay", "cost", "price", "checkout"]):
            return "payment"
        if any(w in lowered for w in ["timing", "hour", "open", "close", "holiday", "where", "location", "rule"]):
            return "knowledge"
        return "support"

    def _fallback_generate_response(self, intent: str, message: str) -> str:
        """High-quality deterministic responses when running offline without Gemini."""
        if intent == "booking":
            return (
                "I can certainly help you reserve museum tickets! Please provide your preferred visit date "
                "(YYYY-MM-DD), entry time slot (e.g., 10:00), ticket type (adult, child, student, senior), "
                "and number of visitors."
            )
        if intent == "recommendation":
            return (
                "Based on current popularity and visitor ratings, our top recommendations include: "
                "1) Ancient Civilizations (Gallery A), 2) Modern Art & Sculpture (Hall B), and "
                "3) Space Discovery & Robotics (Science Wing)."
            )
        if intent == "payment":
            return (
                "After initiating your ticket booking, you can complete the secure checkout using Razorpay "
                "(supporting UPI, Credit/Debit Cards, and Net Banking). Upon verified settlement, your "
                "digital QR ticket pass is generated automatically."
            )
        if intent == "knowledge":
            return (
                "The museum is open Tuesday through Sunday from 10:00 AM to 6:00 PM (closed on Mondays). "
                "General admission is INR 300 for adults, INR 150 for children, and INR 200 for students with valid ID."
            )
        return (
            "Welcome to MuseSphere AI! Ask me anything about ticket reservations, current exhibitions, "
            "daily timings, event schedules, or museum policies."
        )

    async def run(self, message: str, language: str = "en", context: str = "") -> AgentResult:
        """
        Execute the AI agent workflow asynchronously.
        """
        if self.graph is not None:
            try:
                state: AgentState = {
                    "message": message,
                    "language": language,
                    "context": context,
                    "intent": "support",
                    "response": ""
                }
                # Run LangGraph compiled state machine
                output = self.graph.invoke(state)
                return AgentResult(
                    intent=output.get("intent", "support"),
                    response=output.get("response", self._fallback_generate_response("support", message)),
                    language=language
                )
            except Exception as exc:
                logger.warning("LangGraph execution encountered error (%s). Falling back to rule router.", exc)

        # Offline / Fallback Execution
        intent = self._fallback_detect_intent(message)
        response = self._fallback_generate_response(intent, message)
        return AgentResult(intent=intent, response=response, language=language)
