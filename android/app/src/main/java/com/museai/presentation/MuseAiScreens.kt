package com.museai.presentation

enum class MuseAiScreen(val route: String, val title: String) {
    Splash("splash", "Splash"), Login("login", "Login"), Signup("signup", "Signup"), ForgotPassword("forgot", "Forgot Password"),
    Home("home", "Home"), AiChat("chat", "AI Assistant"), Booking("booking", "Ticket Booking"), Payment("payment", "Payment"),
    QrTicket("ticket", "QR Ticket"), History("history", "Booking History"), MuseumMap("map", "Museum Map"), Profile("profile", "Profile"), Notifications("notifications", "Notifications")
}
