package com.museai.data

import com.museai.domain.Booking
import com.museai.domain.ChatMessage
import com.museai.domain.Exhibition

interface MuseAiRepository {
    suspend fun featuredExhibitions(): List<Exhibition>
    suspend fun createBooking(date: String, slot: String, type: String, visitors: Int): Booking
    suspend fun sendChat(message: String, language: String? = null): ChatMessage
}
