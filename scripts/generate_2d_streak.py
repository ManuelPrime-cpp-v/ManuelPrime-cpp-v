import datetime
import json
import os
import urllib.request

TOKEN = os.environ["GITHUB_TOKEN"]
USER = "ManuelPrime-cpp-v"

query = """
query($userName:String!) {
  user(login: $userName) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            color
          }
        }
      }
    }
  }
}
"""

req = urllib.request.Request(
    "https://github.com",
    data=json.dumps({"query": query, "variables": {"userName": USER}}).encode("utf-8"),
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
total = cal["totalContributions"]
weeks = cal["weeks"][-26:]  # Last 26 weeks (6 months) for crisp, wide 2D boxes

# Calculate current & longest streak
days = [d for w in cal["weeks"] for d in w["contributionDays"]]
today = datetime.date.today().isoformat()
past_days = [d for d in days if d["date"] <= today]

longest, current, temp = 0, 0, 0
for d in past_days:
    if d["contributionCount"] > 0:
        temp += 1
        longest = max(longest, temp)
    else:
        temp = 0

for d in reversed(past_days):
    if d["contributionCount"] > 0:
        current += 1
    elif d["date"] < today:
        break

# Map GitHub levels to classic dark-mode 2D green palette
def green_shade(count):
    if count == 0: return "#161B22"
    if count <= 2: return "#0E4429"
    if count <= 5: return "#006D32"
    if count <= 10: return "#26A641"
    return "#39D353"

rects = []
for w_idx, week in enumerate(weeks):
    for d_idx, day in enumerate(week["contributionDays"]):
        x = 24 + w_idx * 17
        y = 78 + d_idx * 17
        fill = green_shade(day["contributionCount"])
        rects.append(f'<rect x="{x}" y="{y}" width="13" height="13" rx="2.5" fill="{fill}"/>')

svg = f'''<svg width="490" height="215" viewBox="0 0 490 215" xmlns="http://w3.org">
  <rect x="0.5" y="0.5" width="489" height="214" rx="10" fill="#090C10" stroke="#1E293B"/>
  <text x="24" y="32" fill="#38BDF8" font-family="monospace" font-size="13" font-weight="bold">CONTRIBUTION TELEMETRY // 2D MATRIX</text>
  <text x="24" y="56" fill="#E2E8F0" font-family="sans-serif" font-size="13">
    Total: <tspan fill="#39D353" font-weight="bold">{total}</tspan>   ·   
    Current Streak: <tspan fill="#39D353" font-weight="bold">{current}d</tspan>   ·   
    Longest Streak: <tspan fill="#39D353" font-weight="bold">{longest}d</tspan>
  </text>
  {"".join(rects)}
</svg>'''

os.makedirs("assets", exist_ok=True)
with open("assets/streak-2d.svg", "w") as f:
    f.write(svg)
