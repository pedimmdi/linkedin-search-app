import { useEffect, useState } from 'react';

import { AlertCircle, LoaderCircle } from 'lucide-react';

import { fetchProfileFilters, searchProfiles } from './api/profiles';
import Filters from './components/Filters';
import ProfileCard from './components/ProfileCard';
import SearchBar from './components/SearchBar';

export default function App() {
  const [profiles, setProfiles] = useState([]);
  const [totalCount, setTotalCount] = useState(0);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');

  const [roles, setRoles] = useState([]);
  const [countries, setCountries] = useState([]);

  const [loading, setLoading] = useState(false);
  const [filtersLoading, setFiltersLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const controller = new AbortController();

    const loadFilters = async () => {
      try {
        setFiltersLoading(true);

        const data = await fetchProfileFilters({
          signal: controller.signal,
        });

        setRoles(data.roles || []);
        setCountries(data.countries || []);
      } catch (requestError) {
        if (requestError.name !== 'CanceledError') {
          console.error('Failed to load filters:', requestError);
        }
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
          page: 1,
          signal: controller.signal,
        });

        setProfiles(data.results || []);
        setTotalCount(data.count || 0);
      } catch (requestError) {
        if (
          requestError.name === 'CanceledError' ||
          requestError.code === 'ERR_CANCELED'
        ) {
          return;
        }

        console.error('Failed to search profiles:', requestError);

        if (requestError.response?.status === 503) {
          setError(
            'Search service is temporarily unavailable. Please try again in a moment.',
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
  }, [searchQuery, selectedRole, selectedCountry]);

  const resetFilters = () => {
    setSelectedRole('');
    setSelectedCountry('');
  };

  const clearSearch = () => {
    setSearchQuery('');
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
              onChange={setSearchQuery}
              onClear={clearSearch}
            />

            <Filters
              roles={roles}
              countries={countries}
              selectedRole={selectedRole}
              selectedCountry={selectedCountry}
              onRoleChange={setSelectedRole}
              onCountryChange={setSelectedCountry}
              onReset={resetFilters}
            />
          </div>

          {filtersLoading && (
            <p className="mt-3 text-xs text-gray-400">
              Loading filter options...
            </p>
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
          </div>

          {error && (
            <div className="mb-6 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <AlertCircle
                size={20}
                className="mt-0.5 shrink-0"
                aria-hidden="true"
              />

              <div>
                <p className="font-semibold">Unable to load profiles</p>
                <p className="mt-1">{error}</p>
              </div>
            </div>
          )}

          {loading ? (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
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
                <LoaderCircle size={22} />
              </div>

              <h2 className="text-lg font-semibold text-gray-900">
                No profiles found
              </h2>

              <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">
                Try changing your search query or removing one of the
                filters.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {profiles.map((profile) => (
                <ProfileCard
                  key={profile.id}
                  profile={profile}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}