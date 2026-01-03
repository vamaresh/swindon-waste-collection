/**
 * Individual collection item component
 */

import { Trash2, Recycle, Leaf, Bottle, Calendar, Clock } from 'lucide-react';
import type { CollectionItemProps } from '../types';

const CollectionItem = ({ collection, isNext = false }: CollectionItemProps) => {
  // Get icon based on waste type
  const getIcon = () => {
    const iconClass = "w-8 h-8";
    switch (collection.icon) {
      case 'trash-can':
        return <Trash2 className={iconClass} />;
      case 'recycle':
        return <Recycle className={iconClass} />;
      case 'leaf':
        return <Leaf className={iconClass} />;
      case 'bottle':
        return <Bottle className={iconClass} />;
      default:
        return <Trash2 className={iconClass} />;
    }
  };

  // Get color classes based on waste type
  const getColorClasses = () => {
    if (collection.type.includes('Rubbish')) {
      return {
        bg: 'bg-rubbish-light',
        text: 'text-rubbish-dark',
        border: 'border-rubbish',
        icon: 'text-rubbish-dark',
      };
    } else if (collection.type.includes('Recycling')) {
      return {
        bg: 'bg-recycling-light',
        text: 'text-recycling-dark',
        border: 'border-recycling',
        icon: 'text-recycling-dark',
      };
    } else if (collection.type.includes('Garden')) {
      return {
        bg: 'bg-garden-light',
        text: 'text-garden-dark',
        border: 'border-garden',
        icon: 'text-garden-dark',
      };
    } else if (collection.type.includes('Plastic')) {
      return {
        bg: 'bg-plastics-light',
        text: 'text-plastics-dark',
        border: 'border-plastics',
        icon: 'text-plastics-dark',
      };
    }
    return {
      bg: 'bg-gray-100',
      text: 'text-gray-800',
      border: 'border-gray-400',
      icon: 'text-gray-600',
    };
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  };

  // Get countdown text
  const getCountdownText = (days: number) => {
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    if (days < 0) return `${Math.abs(days)} days ago`;
    return `in ${days} days`;
  };

  const colors = getColorClasses();

  return (
    <div
      className={`relative bg-white rounded-lg shadow-md border-2 ${colors.border} p-6 transition-all hover:shadow-lg ${
        isNext ? 'ring-2 ring-green-500 ring-offset-2' : ''
      }`}
    >
      {isNext && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold">
          NEXT
        </div>
      )}
      
      <div className="flex items-start space-x-4">
        <div className={`p-3 rounded-full ${colors.bg} ${colors.icon}`}>
          {getIcon()}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className={`text-lg font-semibold ${colors.text} mb-1`}>
            {collection.type}
          </h3>
          
          <div className="flex items-center text-gray-600 text-sm mb-2">
            <Calendar className="w-4 h-4 mr-2" />
            <span>{formatDate(collection.date)}</span>
          </div>
          
          <div className="flex items-center text-gray-600 text-sm">
            <Clock className="w-4 h-4 mr-2" />
            <span className="font-medium">{getCountdownText(collection.days_until)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CollectionItem;
