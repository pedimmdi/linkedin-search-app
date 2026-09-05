import { ExternalLink, MapPin, BriefcaseBusiness } from 'lucide-react';

function renderHighlightedText(text) {
  if (!text) {
    return null;
  }

  const parts = text.split(/(<mark>.*?<\/mark>)/gi);

  return parts.map((part, index) => {
    const match = part.match(/^<mark>(.*?)<\/mark>$/i);

    if (match) {
      return (
        <mark
          key={index}
          className="rounded bg-yellow-100 px-0.5 text-inherit"
        >
          {match[1]}
        </mark>
      );
    }

    return <span key={index}>{part}</span>;
  });
}

function getFirstHighlight(highlight) {
  if (!highlight) {
    return null;
  }

  if (Array.isArray(highlight)) {
    return highlight[0] || null;
  }

  return highlight;
}

function getSkills(profile) {
  if (Array.isArray(profile.skills)) {
    return profile.skills.filter(Boolean);
  }

  if (typeof profile.skills === 'string' && profile.skills.trim()) {
    return profile.skills
      .split(',')
      .map((skill) => skill.trim())
      .filter(Boolean);
  }

  return [];
}

export default function ProfileCard({ profile }) {
  const nameHighlight = getFirstHighlight(profile.highlights?.full_name);
  const jobTitleHighlight = getFirstHighlight(profile.highlights?.job_title);
  const summaryHighlight = getFirstHighlight(profile.highlights?.summary);
  const skillsHighlight = profile.highlights?.skills || [];

  const skills = getSkills(profile);

  const displayedName =
    nameHighlight || profile.full_name || 'Unnamed profile';

  const displayedJobTitle =
    jobTitleHighlight || profile.job_title || 'Job title not available';

  const displayedSummary =
    summaryHighlight || profile.summary || 'No summary available.';

  const displayedSkills =
    skillsHighlight.length > 0
      ? skillsHighlight
      : skills.slice(0, 8);

  return (
    <article className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:border-gray-300 hover:shadow-md">
      <div className="flex flex-col gap-4">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h2 className="truncate text-lg font-semibold text-gray-900">
              {renderHighlightedText(displayedName)}
            </h2>

            <div className="mt-1 flex items-start gap-2 text-sm text-gray-600">
              <BriefcaseBusiness
                size={16}
                className="mt-0.5 shrink-0"
                aria-hidden="true"
              />

              <span>
                {renderHighlightedText(displayedJobTitle)}
              </span>
            </div>
          </div>

          {profile.linkedin_url && (
            <a
              href={profile.linkedin_url}
              target="_blank"
              rel="noreferrer"
              aria-label={`Open ${profile.full_name || 'profile'} on LinkedIn`}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition hover:border-gray-300 hover:bg-gray-50"
            >
              LinkedIn
              <ExternalLink size={15} aria-hidden="true" />
            </a>
          )}
        </div>

        {(profile.location_city || profile.location_country) && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <MapPin size={16} className="shrink-0" aria-hidden="true" />

            <span>
              {[profile.location_city, profile.location_country]
                .filter(Boolean)
                .join(', ')}
            </span>
          </div>
        )}

        <div>
          <h3 className="mb-1 text-sm font-semibold text-gray-800">
            Summary
          </h3>

          <p className="line-clamp-4 text-sm leading-6 text-gray-600">
            {renderHighlightedText(displayedSummary)}
          </p>
        </div>

        {displayedSkills.length > 0 && (
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-800">
              Skills
            </h3>

            <div className="flex flex-wrap gap-2">
              {displayedSkills.map((skill, index) => {
                const highlightedSkill = getFirstHighlight(skill);

                return (
                  <span
                    key={`${skill}-${index}`}
                    className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-700"
                  >
                    {renderHighlightedText(
                      highlightedSkill || skill,
                    )}
                  </span>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </article>
  );
}