/**
 * Postcode input form component
 */

import { useState, FormEvent } from 'react';
import { Search } from 'lucide-react';

interface PostcodeFormProps {
  onSubmit: (postcode: string) => void;
  loading?: boolean;
}

const PostcodeForm = ({ onSubmit, loading = false }: PostcodeFormProps) => {
  const [postcode, setPostcode] = useState('');
  const [error, setError] = useState('');

  const validatePostcode = (value: string): boolean => {
    // UK postcode regex
    const postcodeRegex = /^[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}$/i;
    return postcodeRegex.test(value.trim());
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    const trimmedPostcode = postcode.trim();
    
    if (!trimmedPostcode) {
      setError('Please enter a postcode');
      return;
    }

    if (!validatePostcode(trimmedPostcode)) {
      setError('Please enter a valid UK postcode');
      return;
    }

    setError('');
    onSubmit(trimmedPostcode);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md">
      <div className="space-y-4">
        <div>
          <label
            htmlFor="postcode"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Enter your postcode
          </label>
          <div className="relative">
            <input
              type="text"
              id="postcode"
              value={postcode}
              onChange={(e) => {
                setPostcode(e.target.value.toUpperCase());
                setError('');
              }}
              placeholder="e.g. SN1 1XX"
              className="w-full px-4 py-3 pr-12 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none transition-all"
              disabled={loading}
              autoComplete="postal-code"
            />
            <Search className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          </div>
          {error && (
            <p className="mt-2 text-sm text-red-600">{error}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={loading || !postcode.trim()}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              Searching...
            </>
          ) : (
            'Find Collections'
          )}
        </button>
      </div>
    </form>
  );
};

export default PostcodeForm;
