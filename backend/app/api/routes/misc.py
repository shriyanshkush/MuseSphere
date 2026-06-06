from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.ai.rag import KnowledgeBase
from app.core.security import get_current_user, require_admin
from app.database.session import get_db
from app.ml.recommendation import RecommendationEngine
from app.ml.sentiment import analyze_sentiment
from app.models.entities import Booking, Exhibition, Feedback, KnowledgeDocument, Payment, PaymentStatus, Ticket, User
from app.repositories.domain import ChatRepository, ExhibitionRepository, KnowledgeRepository
from app.schemas.dtos import ChatRequest, ChatResponse, FeedbackIn, FeedbackOut, KnowledgeQuery, RecommendationRead, TicketRead
from app.services.chat import ChatService
router=APIRouter(); kb=KnowledgeBase()
@router.get('/tickets/{booking_id}', response_model=TicketRead, tags=['QR Tickets'])
def get_ticket(booking_id:int, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    booking=db.get(Booking, booking_id)
    if not booking or booking.user_id!=user.id: raise HTTPException(404, 'Booking not found')
    ticket=db.scalar(select(Ticket).where(Ticket.booking_id==booking_id))
    if not ticket: raise HTTPException(404, 'Ticket is available after payment confirmation')
    return ticket
@router.post('/chat/message', response_model=ChatResponse, tags=['AI Chatbot'])
def chat(data:ChatRequest, user:User=Depends(get_current_user), db:Session=Depends(get_db)): return ChatService(db).answer(user.id, data.message, data.language or user.language)
@router.get('/chat/history', tags=['AI Chatbot'])
def history(user:User=Depends(get_current_user), db:Session=Depends(get_db)): return ChatRepository(db).history(user.id)
@router.post('/knowledge/upload', status_code=201, tags=['RAG Knowledge Base'])
async def upload(file:UploadFile=File(...), _:User=Depends(require_admin), db:Session=Depends(get_db)):
    text=(await file.read()).decode('utf-8', errors='ignore'); chunks=kb.chunk(text); doc=KnowledgeDocument(filename=file.filename or 'document.txt', content=text, chunks={'items':chunks})
    db.add(doc); db.commit(); db.refresh(doc); return {'id':doc.id,'filename':doc.filename,'chunks':len(chunks)}
@router.post('/knowledge/query', tags=['RAG Knowledge Base'])
def query(data:KnowledgeQuery, _:User=Depends(get_current_user), db:Session=Depends(get_db)): return {'query':data.query,'answer':f"Based on museum knowledge: {kb.retrieve(KnowledgeRepository(db).list(100,0), data.query)}"}
@router.get('/recommendations', response_model=list[RecommendationRead], tags=['ML Recommendations'])
def recommendations(preferences:str='', user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    ranked=RecommendationEngine().recommend(ExhibitionRepository(db).list(100,0), [p.strip() for p in preferences.split(',') if p.strip()])
    return [{'exhibition_id':e.id,'title':e.title,'score':s,'reason':'Matched your preferences and museum popularity trends'} for s,e in ranked]
@router.post('/feedback/analyze', response_model=FeedbackOut, tags=['Sentiment Analysis'])
def feedback(data:FeedbackIn, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    sentiment,score=analyze_sentiment(data.text); db.add(Feedback(user_id=user.id, text=data.text, sentiment=sentiment, score=score)); db.commit(); return {'sentiment':sentiment,'score':score}
@router.get('/analytics/dashboard', tags=['Admin Analytics'])
def dashboard(_:User=Depends(require_admin), db:Session=Depends(get_db)):
    visitors=db.scalar(select(func.coalesce(func.sum(Booking.visitor_count),0))) or 0; revenue=db.scalar(select(func.coalesce(func.sum(Payment.amount),0)).where(Payment.status==PaymentStatus.paid)) or 0; popular=db.scalars(select(Exhibition).order_by(Exhibition.popularity_score.desc()).limit(5)).all()
    return {'daily_visitors':visitors,'monthly_visitors':visitors,'revenue':revenue,'popular_exhibits':[{'title':i.title,'score':i.popularity_score} for i in popular],'peak_hours':[{'slot':'10:00','visitors':visitors}],'most_asked_questions':['museum timing','book tickets','today exhibitions'],'language_distribution':{'en':70,'hi':10,'fr':8,'es':7,'de':5},'conversion_rate':0.42}
