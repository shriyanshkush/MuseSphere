package com.museai.shared.domain.models

import kotlinx.serialization.Serializable

@Serializable
data class Exhibition(
    val id: Int,
    val title: String,
    val description: String,
    val location: String,
    val category: String,
    val popularityScore: Double
)

@Serializable
data class BookingRequest(
    val visitDate: String,
    val timeSlot: String,
    val ticketType: String,
    val visitorCount: Int
)

@Serializable
data class AiChatRequest(
    val message: String,
    val language: String = "en"
)

@Serializable
data class AiChatResponse(
    val intent: String,
    val response: String,
    val language: String
)
