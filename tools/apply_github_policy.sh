#!/usr/bin/env bash
set -euo pipefail

readonly ORGANIZATION="coe-marble"
readonly TEAM_SLUG="more"
readonly API_VERSION="2022-11-28"

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPOSITORY_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
readonly REPOSITORIES_FILE="${REPOSITORY_ROOT}/governance/rpp-repositories.txt"
readonly RULESETS_DIR="${REPOSITORY_ROOT}/governance/rulesets"

usage() {
    printf '%s\n' \
        'Usage: tools/apply_github_policy.sh [--apply]' \
        '' \
        'Preview the RPP GitHub-policy rollout by default. Pass --apply to create' \
        'the develop branch where absent, grant the MORE team push access, and' \
        'create or update the main and develop rulesets for every configured repository.'
}

apply=false
case "${1:-}" in
    "")
        ;;
    --apply)
        apply=true
        ;;
    --help|-h)
        usage
        exit 0
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac

if ! command -v gh >/dev/null; then
    echo "The GitHub CLI (gh) is required." >&2
    exit 1
fi

if [[ "${apply}" == false ]]; then
    echo "Preview only; no GitHub settings will be changed."
    echo "Run $0 --apply to create develop, grant ${TEAM_SLUG} push access, and upsert rulesets."
    sed -n '/^[^#[:space:]]/p' "${REPOSITORIES_FILE}"
    exit 0
fi

gh auth status --hostname github.com >/dev/null

api() {
    gh api -H "X-GitHub-Api-Version: ${API_VERSION}" "$@"
}

ensure_develop_branch() {
    local repository="$1"
    local main_sha

    if api "repos/${ORGANIZATION}/${repository}/git/ref/heads/develop" \
        >/dev/null 2>&1; then
        return
    fi

    main_sha="$(api "repos/${ORGANIZATION}/${repository}/git/ref/heads/main" \
        --jq '.object.sha')"
    api --method POST "repos/${ORGANIZATION}/${repository}/git/refs" \
        -f ref="refs/heads/develop" \
        -f sha="${main_sha}" >/dev/null
}

grant_more_team_push_access() {
    local repository="$1"

    api --method PUT \
        "orgs/${ORGANIZATION}/teams/${TEAM_SLUG}/repos/${ORGANIZATION}/${repository}" \
        -f permission=push >/dev/null
}

upsert_ruleset() {
    local repository="$1"
    local ruleset_file="$2"
    local ruleset_name
    local ruleset_id

    ruleset_name="$(sed -n 's/  "name": "\(.*\)",/\1/p' "${ruleset_file}")"
    ruleset_id="$(api --paginate \
        "repos/${ORGANIZATION}/${repository}/rulesets?includes_parents=false" \
        --jq ".[] | select(.name == \"${ruleset_name}\") | .id")"

    if [[ -n "${ruleset_id}" ]]; then
        api --method PUT \
            "repos/${ORGANIZATION}/${repository}/rulesets/${ruleset_id}" \
            --input "${ruleset_file}" >/dev/null
    else
        api --method POST "repos/${ORGANIZATION}/${repository}/rulesets" \
            --input "${ruleset_file}" >/dev/null
    fi
}

while IFS= read -r repository || [[ -n "${repository}" ]]; do
    if [[ -z "${repository}" || "${repository}" == \#* ]]; then
        continue
    fi

    echo "Applying policy to ${ORGANIZATION}/${repository}"
    ensure_develop_branch "${repository}"
    grant_more_team_push_access "${repository}"
    upsert_ruleset "${repository}" "${RULESETS_DIR}/main.json"
    upsert_ruleset "${repository}" "${RULESETS_DIR}/develop.json"
done < "${REPOSITORIES_FILE}"
