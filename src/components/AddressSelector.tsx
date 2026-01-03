/**
 * Address selector component
 */

import { MapPin } from 'lucide-react';
import type { Address } from '../types';

interface AddressSelectorProps {
  addresses: Address[];
  selectedAddress: Address | null;
  onSelect: (address: Address | null) => void;
  disabled?: boolean;
}

const AddressSelector = ({
  addresses,
  selectedAddress,
  onSelect,
  disabled = false,
}: AddressSelectorProps) => {
  if (addresses.length === 0) {
    return null;
  }

  // Don't show selector if only one address (auto-selected)
  if (addresses.length === 1) {
    return (
      <div className="w-full max-w-md bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start">
          <MapPin className="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-green-900">Selected Address</p>
            <p className="text-sm text-green-700 mt-1">{addresses[0].address}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-md">
      <label
        htmlFor="address-select"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Select your address
      </label>
      <div className="relative">
        <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
        <select
          id="address-select"
          value={selectedAddress?.uprn || ''}
          onChange={(e) => {
            const address = addresses.find((a) => a.uprn === e.target.value);
            onSelect(address || null);
          }}
          disabled={disabled}
          className="w-full pl-12 pr-4 py-3 text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all appearance-none bg-white disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          <option value="">-- Select an address --</option>
          {addresses.map((address) => (
            <option key={address.uprn} value={address.uprn}>
              {address.address}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default AddressSelector;
