from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    """Verify application health endpoint returns 200 OK and system status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "MuseSphere API"


def test_auth_booking_chat_flow():
    """Verify complete user lifecycle: registration, login, booking creation, and AI interaction."""
    email = "visitor@example.com"
    password = "StrongPass!123"

    # Register visitor
    reg_response = client.post(
        "/auth/register",
        json={"name": "Aarav Sharma", "email": email, "password": password},
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["email"] == email

    # Login and obtain token pair
    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Verify profile endpoint
    profile_response = client.get("/auth/profile", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["name"] == "Aarav Sharma"

    # Create ticket reservation
    booking_response = client.post(
        "/bookings",
        json={
            "visit_date": "2026-08-10",
            "time_slot": "10:00",
            "ticket_type": "adult",
            "visitor_count": 2,
        },
        headers=headers,
    )
    assert booking_response.status_code == 201
    booking_data = booking_response.json()
    assert booking_data["total_amount"] == 600.0
    assert booking_data["status"] == "pending_payment"

    # Send message to AI chatbot
    chat_response = client.post(
        "/chat/message",
        json={"message": "What is the museum timing and ticket price?"},
        headers=headers,
    )
    assert chat_response.status_code == 200
    chat_data = chat_response.json()
    assert chat_data["intent"] in {"knowledge", "booking", "support"}
    assert len(chat_data["response"]) > 0
