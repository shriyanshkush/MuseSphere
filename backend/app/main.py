import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import routers
from app.core.config import get_settings
from app.database.session import Base, engine
import app.models  # noqa: F401
logging.basicConfig(level=logging.INFO); settings=get_settings(); Base.metadata.create_all(bind=engine)
app=FastAPI(title='MuseAI API', version='1.0.0', description='AI-powered museum ticketing, RAG assistant, payments, QR tickets, recommendations, and analytics.')
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
@app.exception_handler(Exception)
async def unhandled_exception(_:Request, exc:Exception): logging.exception('Unhandled error: %s', exc); return JSONResponse(status_code=500, content={'detail':'Internal server error'})
@app.get('/health', tags=['System'])
def health(): return {'status':'ok','service':settings.app_name}
for router in routers: app.include_router(router)
