/**
 * Custom React hooks for managing collections data
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../services/api';
import type { Address, Collection } from '../types';

interface UseCollectionsState {
  addresses: Address[];
  selectedAddress: Address | null;
  collections: Collection[];
  loading: boolean;
  error: string | null;
  lookupPostcode: (postcode: string) => Promise<void>;
  selectAddress: (address: Address | null) => void;
  clearError: () => void;
}

export const useCollections = (): UseCollectionsState => {
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddress, setSelectedAddress] = useState<Address | null>(null);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load collections when address is selected
  useEffect(() => {
    const loadCollections = async () => {
      if (!selectedAddress) {
        setCollections([]);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await apiClient.getCollections(selectedAddress.uprn);
        setCollections(response.collections);
        
        // Cache collections in localStorage
        localStorage.setItem(
          `collections_${selectedAddress.uprn}`,
          JSON.stringify({
            data: response.collections,
            timestamp: Date.now(),
          })
        );
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load collections';
        setError(errorMessage);
        
        // Try to load from cache
        const cached = localStorage.getItem(`collections_${selectedAddress.uprn}`);
        if (cached) {
          try {
            const { data, timestamp } = JSON.parse(cached);
            // Use cache if less than 1 hour old
            if (Date.now() - timestamp < 3600000) {
              setCollections(data);
              setError(`${errorMessage} (showing cached data)`);
            }
          } catch {
            // Ignore cache errors
          }
        }
      } finally {
        setLoading(false);
      }
    };

    loadCollections();
  }, [selectedAddress]);

  const lookupPostcode = useCallback(async (postcode: string) => {
    setLoading(true);
    setError(null);
    setAddresses([]);
    setSelectedAddress(null);
    setCollections([]);

    try {
      const response = await apiClient.lookupUPRN(postcode);
      
      if (response.addresses.length === 0) {
        setError('No addresses found for this postcode');
      } else {
        setAddresses(response.addresses);
        
        // Auto-select if only one address
        if (response.addresses.length === 1) {
          setSelectedAddress(response.addresses[0]);
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to lookup postcode';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const selectAddress = useCallback((address: Address | null) => {
    setSelectedAddress(address);
    setError(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    addresses,
    selectedAddress,
    collections,
    loading,
    error,
    lookupPostcode,
    selectAddress,
    clearError,
  };
};
