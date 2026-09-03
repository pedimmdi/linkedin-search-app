import { Search, X } from 'lucide-react';

export default function SearchBar({
  value,
  onChange,
  onClear,
}) {
  return (
    <div className="relative flex-1">
      <Search
        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        size={20}
        aria-hidden="true"
      />

      <input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search name, job title, skills, summary..."
        aria-label="Search profiles"
        className="w-full rounded-lg border border-gray-300 bg-white py-2.5 pl-10 pr-10 text-gray-800 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
      />

      {value && (
        <button
          type="button"
          onClick={onClear}
          aria-label="Clear search"
          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 transition hover:text-gray-700"
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}