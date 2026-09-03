import {
  Briefcase,
  ExternalLink,
  MapPin,
  User,
} from 'lucide-react';

function getInitials(name) {
  if (!name) {
    return 'NA';
  }

  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();
}

function renderHighlightedText(text, highlights) {
  if (!text) {
    return null;
  }

  if (!highlights?.length) {
    return text;
  }

  return (
    <>
      {highlights.map((item, index) => (
        <span key={`${item}-${index}`}>
          {index > 0 && ' ... '}
          <span
            dangerouslySetInnerHTML={{
              __html: item,
            }}
          />
        </span>
      ))}
    </>
  );
}

export default function ProfileCard({ profile }) {
  const initials = getInitials(profile.full_name);

  const highlightedSummary =
    profile.highlight?.summary?.length > 0
      ? profile.highlight.summary
      : null;

  return (
    <article className="flex h-full flex-col justify-between rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div>
        <div className="mb-5 flex items-start gap-3">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-blue-100 font-semibold text-blue-700">
            {profile.full_name ? initials : <User size={22} />}
          </div>

          <div className="min-w-0">
            <h2 className="truncate text-lg font-semibold text-gray-900">
              {profile.full_name || 'Unknown candidate'}
            </h2>

            {profile.job_title_role && (
              <span className="mt-1 inline-block rounded bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                {profile.job_title_role}
              </span>
            )}
          </div>
        </div>

        <div className="mb-4 space-y-2 text-sm text-gray-600">
          {profile.job_title && (
            <div className="flex items-start gap-2">
              <Briefcase
                size={16}
                className="mt-0.5 shrink-0 text-gray-400"
                aria-hidden="true"
              />

              <span>{profile.job_title}</span>
            </div>
          )}

          {(profile.location_city || profile.location_country) && (
            <div className="flex items-start gap-2">
              <MapPin
                size={16}
                className="mt-0.5 shrink-0 text-gray-400"
                aria-hidden="true"
              />

              <span>
                {[profile.location_city, profile.location_country]
                  .filter(Boolean)
                  .join(', ')}
              </span>
            </div>
          )}
        </div>

        {(highlightedSummary || profile.summary) && (
          <div className="mb-4 rounded-lg border border-gray-100 bg-gray-50 p-3 text-sm leading-6 text-gray-600">
            {highlightedSummary
              ? renderHighlightedText(
                  profile.summary,
                  highlightedSummary,
                )
              : profile.summary}
          </div>
        )}

        {profile.skills && (
          <div className="mb-4 flex flex-wrap gap-1.5">
            {profile.skills
              .split(',')
              .map((skill) => skill.trim())
              .filter(Boolean)
              .slice(0, 6)
              .map((skill) => (
                <span
                  key={skill}
                  className="rounded bg-gray-100 px-2 py-1 text-[11px] font-medium text-gray-700"
                >
                  {skill}
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
          className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-gray-200 bg-gray-50 py-2.5 text-xs font-medium text-gray-700 transition hover:bg-gray-100"
        >
          View LinkedIn Profile

          <ExternalLink
            size={14}
            aria-hidden="true"
          />
        </a>
      )}
    </article>
  );
}