package com.museai.shared.data

import com.museai.shared.domain.models.Exhibition
import com.museai.shared.network.NetworkClient
import io.ktor.client.call.body
import io.ktor.client.request.get
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class ExhibitionRepository {
    private val client = NetworkClient.httpClient

    fun getExhibitions(): Flow<List<Exhibition>> = flow {
        try {
            val response: List<Exhibition> = client.get("/exhibitions").body()
            emit(response)
        } catch (e: Exception) {
            e.printStackTrace()
            emit(emptyList())
        }
    }
}
