/**
 * Main App Component
 */

import { Toaster, toast } from 'react-hot-toast';
import { Trash2, AlertCircle } from 'lucide-react';
import PostcodeForm from './components/PostcodeForm';
import AddressSelector from './components/AddressSelector';
import CollectionSchedule from './components/CollectionSchedule';
import LoadingSpinner from './components/LoadingSpinner';
import { useCollections } from './hooks/useCollections';
import { useEffect } from 'react';

function App() {
  const {
    addresses,
    selectedAddress,
    collections,
    loading,
    error,
    lookupPostcode,
    selectAddress,
    clearError,
  } = useCollections();

  // Show error toast
  useEffect(() => {
    if (error) {
      toast.error(error, {
        duration: 5000,
        position: 'top-center',
      });
      clearError();
    }
  }, [error, clearError]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      <Toaster />
      
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-3">
            <Trash2 className="w-8 h-8 text-green-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Swindon Waste Collections
              </h1>
              <p className="text-sm text-gray-600">
                Check your waste collection dates
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col items-center space-y-8">
          {/* Postcode Form */}
          <div className="w-full flex justify-center">
            <PostcodeForm onSubmit={lookupPostcode} loading={loading} />
          </div>

          {/* Address Selector */}
          {addresses.length > 0 && (
            <div className="w-full flex justify-center">
              <AddressSelector
                addresses={addresses}
                selectedAddress={selectedAddress}
                onSelect={selectAddress}
                disabled={loading}
              />
            </div>
          )}

          {/* Loading State */}
          {loading && selectedAddress && (
            <LoadingSpinner message="Loading collections..." />
          )}

          {/* Collections Schedule */}
          {!loading && selectedAddress && collections.length > 0 && (
            <div className="w-full flex justify-center">
              <CollectionSchedule collections={collections} />
            </div>
          )}

          {/* Empty State */}
          {!loading && selectedAddress && collections.length === 0 && (
            <div className="w-full max-w-md bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <div className="flex items-start">
                <AlertCircle className="w-6 h-6 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-yellow-900">
                    No Collections Found
                  </h3>
                  <p className="text-sm text-yellow-700 mt-1">
                    We couldn't find any collection information for this address.
                    Please try another address or contact Swindon Borough Council.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Info Section */}
          {!selectedAddress && addresses.length === 0 && !loading && (
            <div className="w-full max-w-2xl mt-8">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  How to use this service
                </h2>
                <ol className="space-y-3 text-gray-700">
                  <li className="flex items-start">
                    <span className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
                      1
                    </span>
                    <span>Enter your Swindon postcode in the search box above</span>
                  </li>
                  <li className="flex items-start">
                    <span className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
                      2
                    </span>
                    <span>Select your address from the dropdown list</span>
                  </li>
                  <li className="flex items-start">
                    <span className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
                      3
                    </span>
                    <span>View your upcoming waste collection schedule</span>
                  </li>
                </ol>

                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-900 mb-2">
                    Collection Types
                  </h3>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-rubbish rounded"></div>
                      <span>Rubbish bin</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-recycling rounded"></div>
                      <span>Recycling boxes</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-garden rounded"></div>
                      <span>Garden waste</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 bg-plastics rounded"></div>
                      <span>Plastics</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>
              Data sourced from{' '}
              <a
                href="https://www.swindon.gov.uk"
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-600 hover:text-green-700 font-medium"
              >
                Swindon Borough Council
              </a>
            </p>
            <p className="mt-2">
              Scraping code adapted from{' '}
              <a
                href="https://github.com/mampfes/hacs_waste_collection_schedule"
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-600 hover:text-green-700 font-medium"
              >
                hacs_waste_collection_schedule
              </a>
              {' '}by Steffen Zimmermann (MIT License)
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
