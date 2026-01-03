/**
 * TypeScript type definitions for the application
 */

export interface Address {
  uprn: string;
  address: string;
}

export interface Collection {
  date: string; // ISO date format
  type: string;
  icon: string;
  days_until: number;
}

export interface UPRNLookupRequest {
  postcode: string;
}

export interface UPRNLookupResponse {
  addresses: Address[];
}

export interface CollectionsResponse {
  collections: Collection[];
  uprn: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export type WasteType = 'Rubbish bin' | 'Recycling boxes' | 'Garden waste bin' | 'Plastics';

export interface CollectionItemProps {
  collection: Collection;
  isNext?: boolean;
}
