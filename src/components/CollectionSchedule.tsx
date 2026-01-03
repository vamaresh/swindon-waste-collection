/**
 * Collection schedule component
 */

import CollectionItem from './CollectionItem';
import type { Collection } from '../types';
import { CalendarX } from 'lucide-react';

interface CollectionScheduleProps {
  collections: Collection[];
}

const CollectionSchedule = ({ collections }: CollectionScheduleProps) => {
  if (collections.length === 0) {
    return (
      <div className="w-full max-w-md bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <CalendarX className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 font-medium">No collections found</p>
        <p className="text-gray-500 text-sm mt-2">
          There are no upcoming collections for this address.
        </p>
      </div>
    );
  }

  // Sort collections by date
  const sortedCollections = [...collections].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Find the next collection (first one with days_until >= 0)
  const nextCollectionIndex = sortedCollections.findIndex(
    (c) => c.days_until >= 0
  );

  return (
    <div className="w-full max-w-2xl">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Your Collection Schedule
      </h2>
      
      <div className="space-y-4">
        {sortedCollections.map((collection, index) => (
          <CollectionItem
            key={`${collection.date}-${collection.type}`}
            collection={collection}
            isNext={index === nextCollectionIndex && nextCollectionIndex >= 0}
          />
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> Collection times may vary. Please put your bins
          out the night before your scheduled collection day.
        </p>
      </div>
    </div>
  );
};

export default CollectionSchedule;
