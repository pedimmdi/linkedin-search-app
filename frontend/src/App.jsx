import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, Briefcase, ExternalLink, User } from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8000/api/profiles/search/';

export default function App() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  // Filter States
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');

  // Dropdown Options from Backend
  const [roles, setRoles] = useState([]);
  const [countries, setCountries] = useState([]);

  // Fetch profiles from backend API
  const fetchProfiles = async () => {
    setLoading(true);
    try {
      const response = await axios.get(API_BASE_URL, {
        params: {
          q: searchQuery,
          role: selectedRole,
          country: selectedCountry,
        },
      });

      setProfiles(response.data.results || []);
      setTotalCount(response.data.count || 0);

      if (response.data.filters) {
        setRoles(response.data.filters.roles || []);
        setCountries(response.data.filters.countries || []);
      }
    } catch (error) {
      console.error('Error fetching profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchProfiles();
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, selectedRole, selectedCountry]);

  return (
    <div className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <header className="mb-8 text-center md:text-left">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">LinkedIn Profiles Search</h1>
        <p className="text-gray-600">Search and filter candidate profiles live from backend API.</p>
      </header>

      {/* Search & Filters */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 space-y-4 md:space-y-0 md:flex md:gap-4 md:items-center">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search name, job title, summary, skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-800"
          />
        </div>

        {/* Role Filter */}
        <div className="w-full md:w-60">
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="w-full py-2.5 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-700 bg-white"
          >
            <option value="">All Job Roles</option>
            {roles.map((role, idx) => (
              <option key={idx} value={role}>{role}</option>
            ))}
          </select>
        </div>

        {/* Country Filter */}
        <div className="w-full md:w-52">
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="w-full py-2.5 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-gray-700 bg-white"
          >
            <option value="">All Countries</option>
            {countries.map((country, idx) => (
              <option key={idx} value={country}>{country}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Result Counter */}
      <div className="mb-6">
        <p className="text-sm font-medium text-gray-600">
          Found <span className="text-blue-600 font-bold">{totalCount}</span> candidates
        </p>
      </div>

      {/* Grid Display */}
      {loading ? (
        <div className="text-center py-16 text-gray-500 font-medium">Loading candidate profiles...</div>
      ) : profiles.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-gray-200 text-gray-500">
          No profiles found matching your filters.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {profiles.map((profile) => (
            <div
              key={profile.id}
              className="bg-white rounded-xl border border-gray-200 p-6 flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-lg">
                      <User className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg leading-tight">
                        {profile.full_name || 'N/A'}
                      </h3>
                      {profile.job_title_role && (
                        <span className="inline-block mt-1 text-xs font-medium bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                          {profile.job_title_role}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  {profile.job_title && (
                    <div className="flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-gray-400 shrink-0" />
                      <span className="line-clamp-1">{profile.job_title}</span>
                    </div>
                  )}

                  {(profile.location_city || profile.location_country) && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400 shrink-0" />
                      <span>
                        {[profile.location_city, profile.location_country].filter(Boolean).join(', ')}
                      </span>
                    </div>
                  )}
                </div>

                {profile.summary && (
                  <p className="text-xs text-gray-500 line-clamp-3 mb-4 bg-gray-50 p-2.5 rounded border border-gray-100">
                    {profile.summary}
                  </p>
                )}

                {profile.skills && (
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {profile.skills.split(',').slice(0, 5).map((skill, i) => (
                      <span key={i} className="text-[11px] bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {profile.linkedin_url && (
                <a
                  href={profile.linkedin_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-flex items-center justify-center gap-2 w-full py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 font-medium text-xs rounded-lg border border-gray-200 transition-colors"
                >
                  View LinkedIn Profile <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}