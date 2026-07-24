export const API_BASE_URL = 'http://localhost:8000';

export interface Exhibition {
  id: number;
  title: string;
  description: string;
  category: string;
  popularity_score: number;
}

export interface Ticket {
  id: number;
  booking_id: number;
  qr_code: string;
}

export class ApiClient {
  private static async fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }

  static async getExhibitions(): Promise<Exhibition[]> {
    return this.fetchWithAuth('/exhibitions');
  }

  static async getRecommendations(preferences: string): Promise<any[]> {
    return this.fetchWithAuth(`/recommendations?preferences=${encodeURIComponent(preferences)}`);
  }

  static async chat(message: string, language: string = 'en') {
    return this.fetchWithAuth('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message, language }),
    });
  }

  static async bookTicket(data: any) {
    return this.fetchWithAuth('/bookings', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}
