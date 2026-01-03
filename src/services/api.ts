/**
 * API client for Swindon Waste Collection service
 */

import axios, { AxiosInstance } from 'axios';
import type {
  UPRNLookupRequest,
  UPRNLookupResponse,
  CollectionsResponse,
  HealthResponse,
} from '../types';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = import.meta.env.VITE_API_URL || '';
    
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Health check endpoint
   */
  async health(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/api/health');
    return response.data;
  }

  /**
   * Lookup UPRN by postcode
   */
  async lookupUPRN(postcode: string): Promise<UPRNLookupResponse> {
    const request: UPRNLookupRequest = { postcode };
    const response = await this.client.post<UPRNLookupResponse>(
      '/api/uprn-lookup',
      request
    );
    return response.data;
  }

  /**
   * Get waste collections for a UPRN
   */
  async getCollections(uprn: string): Promise<CollectionsResponse> {
    const response = await this.client.get<CollectionsResponse>(
      `/api/collections/${uprn}`
    );
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
