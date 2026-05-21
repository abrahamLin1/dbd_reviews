import os
import random
import sys

import discord
from discord import app_commands
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

from dbd_reviews import fetch_negative_reviews

_review_cache: list = []

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def _get_review() -> dict:
    global _review_cache
    if not _review_cache:
        print("Fetching reviews from Steam...")
        _review_cache = fetch_negative_reviews(max_reviews=100)
    return random.choice(_review_cache)


def _format_review(review: dict) -> discord.Embed:
    author_id = review["author"]["steamid"]
    hours = review["author"]["playtime_forever"] / 60
    text = review.get("review", "").strip()
    votes_helpful = review.get("votes_helpful", 0)

    if len(text) > 1024:
        text = text[:1021] + "..."

    embed = discord.Embed(
        title="Dead by Daylight — Negative Review",
        description=text,
        color=discord.Color.red(),
    )
    embed.add_field(name="Hours played", value=f"{hours:.1f}h", inline=True)
    # embed.add_field(name="Helpful votes", value=str(votes_helpful), inline=True)
    embed.set_footer(text=f"SteamID: {author_id}")
    return embed


@tree.command(name="review", description="Fetch a random negative Dead by Daylight review from Steam")
async def review_command(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        review = _get_review()
        embed = _format_review(review)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"Failed to fetch review: {e}")


@client.event
async def on_ready():
    guild_id = os.getenv("GUILD_ID")
    if guild_id:
        guild = discord.Object(id=int(guild_id))
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        print(f"Logged in as {client.user} — slash commands synced to guild {guild_id}.")
    else:
        await tree.sync()
        print(f"Logged in as {client.user} — slash commands synced globally.")


client.run(os.getenv("DISCORD_TOKEN"))
