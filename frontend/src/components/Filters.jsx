export default function Filters({
  roles,
  countries,
  selectedRole,
  selectedCountry,
  onRoleChange,
  onCountryChange,
  onReset,
}) {
  const hasActiveFilters = selectedRole || selectedCountry;

  return (
    <div className="flex w-full flex-col gap-3 md:w-auto md:flex-row">
      <select
        value={selectedRole}
        onChange={(event) => onRoleChange(event.target.value)}
        aria-label="Filter by job role"
        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-gray-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 md:w-56"
      >
        <option value="">All Job Roles</option>

        {roles.map((role) => (
          <option key={role} value={role}>
            {role}
          </option>
        ))}
      </select>

      <select
        value={selectedCountry}
        onChange={(event) => onCountryChange(event.target.value)}
        aria-label="Filter by country"
        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-gray-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 md:w-52"
      >
        <option value="">All Countries</option>

        {countries.map((country) => (
          <option key={country} value={country}>
            {country}
          </option>
        ))}
      </select>

      {hasActiveFilters && (
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-600 transition hover:bg-gray-50 hover:text-gray-900"
        >
          Reset
        </button>
      )}
    </div>
  );
}