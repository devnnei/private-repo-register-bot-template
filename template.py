import discord
import requests
import asyncio

# 🔑 Tokens
DISCORD_TOKEN = "your bot token"
GITHUB_TOKEN = "your github token"
OWNER = "by nnei " # you can replace this if you want :(
REPO = "https://github.com/{ownerofrepo}/{repo}"
CHANNEL_ID = 9999999999999999999  # replace with channel ID

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_commit = None

async def fetch_commits():
    global last_commit
    url = f"https://api.github.com/repos/devnnei/grillin/commits"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"❌ GitHub API error: {r.status_code}")
        return

    commits = r.json()
    if not commits:
        print("⚠️ No commits found")
        return

    latest = commits[0]["sha"]
    print(f"🔎 Latest commit: {latest[:7]}")

    if latest != last_commit:
        commit = commits[0]
        author = commit["commit"]["author"]["name"]
        message = commit["commit"]["message"]
        url = commit["html_url"]

        embed = discord.Embed(
            title="📌 New Commit",
            description=f"[{message}]({url})",
            color=discord.Color.green()
        )
        embed.add_field(name="Author", value=author, inline=True)
        embed.add_field(name="SHA", value=latest[:7], inline=True)
        embed.set_footer(text=f"{OWNER}/{REPO}")

        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
            print(f"✅ Sent new commit: {latest[:7]}")
        else:
            print("❌ Channel not found")

        last_commit = latest
    else:
        print("⏸ No new commits")

@client.event
async def on_ready():
    global last_commit
    print(f"✅ Logged in as {client.user}")

    # initialize last_commit on startup
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        commits = r.json()
        if commits:
            last_commit = commits[0]["sha"]
            print(f"🔄 Starting at commit {last_commit[:7]}")

    while True:
        await fetch_commits()
        await asyncio.sleep(10)  # check every 10s

client.run(DISCORD_TOKEN)
