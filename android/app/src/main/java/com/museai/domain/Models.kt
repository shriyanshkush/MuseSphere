package com.museai.domain

data class Exhibition(val id: Int, val title: String, val category: String, val location: String, val image: String?)
data class Booking(val id: Int, val visitDate: String, val timeSlot: String, val ticketType: String, val visitorCount: Int, val totalAmount: Double)
data class ChatMessage(val content: String, val fromUser: Boolean, val language: String = "en")
