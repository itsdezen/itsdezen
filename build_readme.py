import pathlib
import re
import os
from github import Github

root = pathlib.Path(__file__).parent.resolve()

TOKEN = os.environ.get("GH_TOKEN", "")
OWNER = "itsdezen"
TRACKED_REPOS = ["tili"]


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


EMOJI_RE = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # geometric shapes extended
    "\U0001F800-\U0001F8FF"  # supplemental arrows-c
    "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
    "\U0001FA00-\U0001FAFF"  # symbols and pictographs extended-a
    "☀-⛿"          # misc symbols
    "✀-➿"          # dingbats
    "️"                 # variation selector-16
    "‍"                 # zero width joiner
    "]+",
    flags=re.UNICODE,
)


def strip_emoji(text):
    if not text:
        return ""
    cleaned = EMOJI_RE.sub("", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def normalize_release_title(repo_name, release):
    title = (release.title or "").replace(repo_name, "").strip()
    title = strip_emoji(title)
    if not title:
        title = strip_emoji(release.tag_name or "").strip()
    return title or "Release"


def fetch_releases(oauth_token):
    try:
        g = Github(oauth_token)
        releases = []

        for name in TRACKED_REPOS:
            try:
                repo = g.get_repo(f"{OWNER}/{name}")
                for release in repo.get_releases()[:10]:
                    if release.prerelease or (release.tag_name or "").lower() == "nightly":
                        continue
                    releases.append({
                        "repo": repo.name,
                        "repo_url": repo.html_url,
                        "description": repo.description or "",
                        "release": normalize_release_title(repo.name, release),
                        "published_at": release.published_at.strftime("%Y-%m-%d"),
                        "url": release.html_url,
                    })
                    break
            except Exception as e:
                print(f"Error fetching releases for {name}: {e}")
                continue

        return releases
    except Exception as e:
        print(f"Error fetching releases: {e}")
        return []


def extract_current_stats(readme_content):
    match = re.search(
        r'(\d{1,3}(?:,\d{3})*) followers.*?(\d{1,3}(?:,\d{3})*) stars.*?(\d{1,3}(?:,\d{3})*) forks',
        readme_content,
    )
    if match:
        return {
            'followers': int(match.group(1).replace(',', '')),
            'stars': int(match.group(2).replace(',', '')),
            'forks': int(match.group(3).replace(',', '')),
        }
    return {'followers': 3, 'stars': 14, 'forks': 0}


def fetch_github_stats(oauth_token, current_stats=None):
    try:
        g = Github(oauth_token)
        user = g.get_user()

        total_stars = 0
        total_forks = 0

        for repo in user.get_repos(type='owner'):
            if not repo.fork:
                total_stars += repo.stargazers_count
                total_forks += repo.forks_count

        return {
            'stars': total_stars,
            'forks': total_forks,
            'followers': user.followers,
        }
    except Exception as e:
        print(f"Error fetching GitHub stats: {e}")
        return current_stats or {'stars': 14, 'forks': 0, 'followers': 3}


if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()

    current_stats = extract_current_stats(readme_contents)

    releases = fetch_releases(TOKEN)
    releases.sort(key=lambda r: r["published_at"], reverse=True)

    md = "<br>".join(
        "• [{repo} {release}]({url}) - {published_at}".format(**release)
        for release in releases[:6]
    )
    rewritten = replace_chunk(readme_contents, "recent_releases", md)

    stats = fetch_github_stats(TOKEN, current_stats)
    stats_text = (
        f"👥 {stats['followers']:,} followers &nbsp;·&nbsp; "
        f"⭐ {stats['stars']:,} stars &nbsp;·&nbsp; "
        f"🍴 {stats['forks']:,} forks"
    )
    rewritten = replace_chunk(rewritten, "github_stats", stats_text, inline=True)

    readme.open("w").write(rewritten)
