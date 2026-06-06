package com.museai.presentation

object ScreenCatalog {
    val implementedFeatures = mapOf(
        MuseAiScreen.Splash to listOf("animated museum logo", "loading animation", "auto navigation"),
        MuseAiScreen.Login to listOf("email validation", "password validation", "Google Sign-In placeholder"),
        MuseAiScreen.Home to listOf("featured exhibitions", "events", "today shows", "search", "quick booking", "AI card"),
        MuseAiScreen.AiChat to listOf("ChatGPT-style messages", "markdown", "suggested prompts", "voice", "multilingual", "image upload"),
        MuseAiScreen.Booking to listOf("date", "time slot", "ticket category", "visitor count", "dynamic pricing", "availability"),
        MuseAiScreen.Payment to listOf("Razorpay", "UPI", "cards", "net banking"),
        MuseAiScreen.QrTicket to listOf("QR code", "booking ID", "visitor info", "download"),
        MuseAiScreen.Profile to listOf("language", "dark mode", "notifications")
    )
}
