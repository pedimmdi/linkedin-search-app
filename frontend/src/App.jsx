import { useEffect, useState } from 'react';

import {
  AlertCircle,
  Search,
  SearchX,
} from 'lucide-react';

import { fetchProfileFilters, searchProfiles } from './api/profiles';
import Filters from './components/Filters';
import Pagination from './components/Pagination';
import ProfileCard from './components/ProfileCard';
import SearchBar from './components/SearchBar';

const PAGE_SIZE = 20;

export default function App() {
  const [profiles, setProfiles] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');

  const [roles, setRoles] = useState([]);
  const [countries, setCountries] = useState([]);

  const [loading, setLoading] = useState(false);
  const [filtersLoading, setFiltersLoading] = useState(true);
  const [filtersError, setFiltersError] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();

    const loadFilters = async () => {
      try {
        setFiltersLoading(true);
        setFiltersError('');

        const data = await fetchProfileFilters({
          signal: controller.signal,
        });

        setRoles(data.roles || []);
        setCountries(data.countries || []);
      } catch (requestError) {
        if (
          requestError.name === 'CanceledError' ||
          requestError.code === 'ERR_CANCELED' ||
          requestError.name === 'AbortError'
        ) {
          return;
        }

        console.error('Failed to load filters:', requestError);

        setFiltersError(
          'Filter options could not be loaded. You can still search profiles.',
        );
      } finally {
        if (!controller.signal.aborted) {
          setFiltersLoading(false);
        }
      }
    };

    loadFilters();

    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    const timeoutId = setTimeout(async () => {
      try {
        setLoading(true);
        setError('');

        const data = await searchProfiles({
          query: searchQuery,
          role: selectedRole,
          country: selectedCountry,
          page: currentPage,
          signal: controller.signal,
        });

        setProfiles(data.results || []);
        setTotalCount(data.count || 0);
      } catch (requestError) {
        if (
          requestError.name === 'CanceledError' ||
          requestError.code === 'ERR_CANCELED' ||
          requestError.name === 'AbortError'
        ) {
          return;
        }

        console.error('Failed to search profiles:', requestError);

        if (requestError.response?.status === 503) {
          setError(
            'Search service is temporarily unavailable. Please try again in a moment.',
          );
        } else if (requestError.response?.status === 400) {
          setError(
            'The requested page is no longer available. Please try the search again.',
          );
        } else {
          setError(
            'Something went wrong while loading profiles. Please try again.',
          );
        }

        setProfiles([]);
        setTotalCount(0);
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 300);

    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [searchQuery, selectedRole, selectedCountry, currentPage]);

  const handleRoleChange = (value) => {
    setSelectedRole(value);
    setCurrentPage(1);
  };

  const handleCountryChange = (value) => {
    setSelectedCountry(value);
    setCurrentPage(1);
  };

  const resetFilters = () => {
    setSelectedRole('');
    setSelectedCountry('');
    setCurrentPage(1);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setCurrentPage(1);
  };

  const handleSearchQueryChange = (value) => {
    setSearchQuery(value);
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);
  const hasActiveFilters = Boolean(
    searchQuery || selectedRole || selectedCountry,
  );

  const clearAllSearchOptions = () => {
    setSearchQuery('');
    setSelectedRole('');
    setSelectedCountry('');
    setCurrentPage(1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="mx-auto max-w-7xl px-4 py-8 md:px-8 md:py-10">
        <header className="mb-8">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-600">
            Candidate Search
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-gray-900 md:text-4xl">
            LinkedIn Profile Search
          </h1>

          <p className="mt-2 max-w-2xl text-gray-600">
            Search candidate profiles by name, role, skills, summary, and
            location.
          </p>
        </header>

        <section
          aria-label="Profile search"
          className="mb-8 rounded-xl border border-gray-200 bg-white p-4 shadow-sm md:p-6"
        >
          <div className="flex flex-col gap-3 lg:flex-row">
            <SearchBar
              value={searchQuery}
              onChange={handleSearchQueryChange}
              onClear={clearSearch}
            />

            <Filters
              roles={roles}
              countries={countries}
              selectedRole={selectedRole}
              selectedCountry={selectedCountry}
              onRoleChange={handleRoleChange}
              onCountryChange={handleCountryChange}
              onReset={resetFilters}
            />
          </div>

          {filtersLoading && (
            <div className="mt-3 flex items-center gap-2 text-xs text-gray-400">
              <span className="h-3 w-3 animate-pulse rounded-full bg-gray-300" />
              Loading filter options...
            </div>
          )}

          {filtersError && !filtersLoading && (
            <div className="mt-3 flex items-start gap-2 text-xs text-amber-700">
              <AlertCircle
                size={15}
                className="mt-0.5 shrink-0"
                aria-hidden="true"
              />

              <span>{filtersError}</span>
            </div>
          )}
        </section>

        <section aria-live="polite">
          <div className="mb-5 flex items-center justify-between">
            <p className="text-sm font-medium text-gray-600">
              Found{' '}
              <span className="font-bold text-blue-600">
                {totalCount}
              </span>{' '}
              candidates
            </p>

            {loading && (
              <span className="text-xs font-medium text-gray-400">
                Searching...
              </span>
            )}
          </div>

          {error && (
            <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <AlertCircle
                size={20}
                className="mt-0.5 shrink-0"
                aria-hidden="true"
              />

              <div>
                <p className="font-semibold">
                  Unable to load profiles
                </p>

                <p className="mt-1">{error}</p>
              </div>
            </div>
          )}

          {loading ? (
            <div
              className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
              aria-label="Loading profiles"
            >
              {Array.from({ length: 6 }).map((_, index) => (
                <div
                  key={index}
                  className="h-72 animate-pulse rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
                >
                  <div className="mb-5 flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-gray-200" />

                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-2/3 rounded bg-gray-200" />
                      <div className="h-3 w-1/3 rounded bg-gray-200" />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="h-3 w-full rounded bg-gray-200" />
                    <div className="h-3 w-4/5 rounded bg-gray-200" />
                    <div className="h-20 w-full rounded bg-gray-200" />
                  </div>
                </div>
              ))}
            </div>
          ) : profiles.length === 0 ? (
            <div className="rounded-xl border border-gray-200 bg-white px-6 py-16 text-center shadow-sm">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-gray-400">
                {hasActiveFilters ? (
                  <SearchX size={22} aria-hidden="true" />
                ) : (
                  <Search size={22} aria-hidden="true" />
                )}
              </div>

              <h2 className="text-lg font-semibold text-gray-900">
                {hasActiveFilters
                  ? 'No profiles found'
                  : 'Start your search'}
              </h2>

              <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">
                {hasActiveFilters
                  ? 'Try changing your search query or removing one of the filters.'
                  : 'Search by candidate name, job title, skills, summary, or location.'}
              </p>

              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={clearAllSearchOptions}
                  className="mt-5 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
                >
                  Clear search
                </button>
              )}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {profiles.map((profile) => (
                  <ProfileCard
                    key={profile.id}
                    profile={profile}
                  />
                ))}
              </div>

              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            </>
          )}
        </section>
      </main>
    </div>
  );
}