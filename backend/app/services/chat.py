from sqlalchemy.orm import Session
from app.ai.workflow import MuseAgentWorkflow
from app.models.entities import ChatHistory
class ChatService:
    def __init__(self, db:Session): self.db=db; self.workflow=MuseAgentWorkflow()
    def answer(self, user_id:int, message:str, language:str='en'):
        result=self.workflow.run(message, language); self.db.add(ChatHistory(user_id=user_id, message=message, response=result.response, language=language)); self.db.commit()
        return {'response':result.response,'intent':result.intent,'language':language}
