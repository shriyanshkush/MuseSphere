from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_health():
    assert client.get('/health').json()['status'] == 'ok'

def test_auth_booking_chat_flow():
    email = 'visitor@example.com'
    client.post('/auth/register', json={'name':'Visitor','email':email,'password':'StrongPass123'})
    login = client.post('/auth/login', json={'email':email,'password':'StrongPass123'})
    assert login.status_code == 200
    token = login.json()['access_token']; headers={'Authorization': f'Bearer {token}'}
    booking = client.post('/bookings', json={'visit_date':'2026-06-07','time_slot':'10:00','ticket_type':'adult','visitor_count':2}, headers=headers)
    assert booking.status_code == 201
    chat = client.post('/chat/message', json={'message':'What is the museum timing?'}, headers=headers)
    assert chat.json()['intent'] == 'knowledge'
