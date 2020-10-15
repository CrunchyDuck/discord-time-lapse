import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
import re
# TODO: Make sure that the user actually has a .env file with the appropriate field.
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot_prefix = "c." # Commands in chat should be prefixed with this.

intents = discord.Intents.none()
intents.members = True
intents.guilds = True
intents.presences = True
intents.messages = True
bot = commands.Bot(bot_prefix, intents=intents) # TODO: Implement multiple prefix support? (SQL database)
bot.remove_command("help") # the default help command is ugly so I overwrite it with my own. also lets me control what's shown.

# Set up logger. Modified docs version.
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# Runs all cogs on startup.
# TODO: Learn how this works so I can use this in other code things I do, hotswitching modules is really cool.
for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")


bot.run(TOKEN)