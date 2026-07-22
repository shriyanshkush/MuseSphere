import logging
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.workflow import MuseAgentWorkflow
from app.models.entities import ChatHistory

logger = logging.getLogger(__name__)


class ChatService:
    """
    Service layer coordinating visitor prompts with the AI LangGraph agent workflow
    and persisting multi-turn conversation logs in the database.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.workflow = MuseAgentWorkflow()

    async def answer(
        self,
        user_id: int,
        message: str,
        language: str = "en",
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Process visitor message through AI agent workflow, store chat history,
        and return intent + structured response.
        """
        result = await self.workflow.run(message, language, context)

        history_entry = ChatHistory(
            user_id=user_id,
            message=message,
            response=result.response,
            language=language,
        )
        self.db.add(history_entry)
        await self.db.commit()

        return {
            "response": result.response,
            "intent": result.intent,
            "language": language,
        }
