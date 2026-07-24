package com.museai.shared.network

import io.ktor.client.HttpClient
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.defaultRequest
import io.ktor.client.request.header
import io.ktor.http.ContentType
import io.ktor.http.URLProtocol
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json

object NetworkClient {
    val httpClient = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }
        
        defaultRequest {
            // Using 10.0.2.2 for Android Emulator connecting to local FastAPI
            url {
                protocol = URLProtocol.HTTP
                host = "10.0.2.2"
                port = 8000
            }
            header("Content-Type", ContentType.Application.Json)
        }
    }
}
