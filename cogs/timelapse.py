from discord.ext import commands
import discord
import sqlite3
import asyncio
import datetime
import os


class TimeLapse(commands.Cog):
	perm_level = "any"  # Enums are a bit rough in Python so this will do. The permission level required to access the components in this command.

	def __init__(self, bot):
		self.bot = bot

		# Load and/or create the database file.
		start_time = int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())
		db_file = "activity.db"
		self.connect = self.init_db(db_file)
		self.cursor = self.connect.cursor()

		dukki_server = 704361803953733693
		tc = 477943536118005770
		mouse_server = 411378748164669440
		self.targets = [ # Formatted as [user_id, server_id]
			[411365470109958155, tc], # Me
			[97837178716950528, tc], # Arix
			[337793807888285698, tc], # Oken
			[268562833338269696, tc], # Six
			[431073784724848652, tc], # Baguette
			[445748129917304844, tc], # Panda
			[395708025169510400, tc], # Abstract
			[630930243464462346, dukki_server], # Pika
			[162690634111516673, dukki_server], # Void
			[565879875647438851, dukki_server], # Pidge
			[226518106497875970, dukki_server], # Davey
			[361176214188064769, dukki_server], # Mudpip
			[697834085695094796, dukki_server], # Goose
			[713465219724345395, dukki_server], # HonkBonk
		]

		self.target_ids = [x[0] for x in self.targets] # Get only the user IDs, so we can easily check if an ID is in here.

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.bot.user} has connected to Discord :)")

		# Create the first entries for the "targets"
		async_tasks = []  # Updating a user requires downloading their image, which can take time as servers and stuff. I store them in an async list so we can execute all of them at once.
		for id, guild in self.targets:
			if not self.in_db(id):
				g = self.bot.get_guild(guild)
				try:
					member = await g.fetch_member(id)  # Fetches a member. Should add them to the cache, too.
				except:
					print(f"Fetching member failed. Guild:{guild} User:{id}")
					continue
				async_tasks.append(asyncio.create_task(self.init_user_to_db(member)))  # Queue the task in the async_tasks list.

		for t in async_tasks:
			await t


	@commands.Cog.listener()
	async def on_member_update(self, before, after):
		# I'm not totally sure how caching works, because it isn't
		# explained in the documentation.
		# Afaik random servers/members of servers will be "cached",
		# meaning you may access them at any time using a "get" command.
		# However, I don't know when things are cached/uncached, or
		# really what that means.
		#
		# Especially, I'm not sure how listeners work with this.
		# When testing on my own, many people simply weren't included
		# in being "listened" to, meaning their data was never updated.
		# The Discord Python API server is honestly a bit of a shitshow
		# and is bogged down with low effort questions so nothing more
		# complicated is ever answered.
		#
		# If you happen to know, contact me! CrunchyDuck#2278
		m_id = before.id
		if m_id in self.target_ids:
			current_time = int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())  # Probably not the most efficient way to get the current Unix time but oh well!

			if not self.in_db(m_id):
				await self.init_user_to_db(before)

			# Compare before and after to check what changed.
			if before.status != after.status:
				self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (m_id, current_time, 0, str(after.status)))

			if before.display_name != after.display_name:
				self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (m_id, current_time, 1, str(after.display_name)))

			if before.activity != after.activity:
				act = after.activity.name if after.activity is not None else ""
				self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (m_id, current_time, 3, str(act)))

			try:
				self.cursor.execute("commit")
			except:
				pass

	@commands.Cog.listener()
	async def on_user_update(self, before, after):
		# Check if the avatar has changed for this user, and if so, update the database.
		m_id = before.id
		if m_id in self.target_ids:
			current_time = int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())  # Probably not the most efficient way to get the current Unix time but oh well!
			# Check if this user has an entry in the activities list already.
			if not self.in_db(m_id):
				await self.init_user_to_db(before)

			if before.avatar != after.avatar:
				print("avatar")
				fname = str(after.avatar) + ".png"
				await after.avatar_url_as(format="png", size=4096).save(f"saved_data\\{str(after.avatar)}.png")  # Download the avatar of the user.
				self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (m_id, current_time, 2, fname))
				self.cursor.execute("commit")

	def init_db(self, db_file_path):
		"""Creates/connects to the database and returns the connection"""
		connect = sqlite3.connect(db_file_path)
		cursor = connect.cursor()

		cursor.execute("begin")
		cursor.execute("CREATE TABLE IF NOT EXISTS activity ("  # An entry is created for each change that is detected.
			"id INTEGER,"  # ID of the user
			"time INTEGER,"  # Time of this event
			"change INTEGER,"  # What field has changed. 0 = status, 1 = name, 2 = profile picture, 3 = activity
			"changed_value TEXT"  # The value of the changed thing. pfp is the image hash, which is also the filename.
			")")
		cursor.execute("commit")

		return connect

	def in_db(self, id):
		"""Checks if a given user has any entries into the database."""
		self.cursor.execute("SELECT * FROM activity WHERE id = ?", (id,))
		return self.cursor.fetchone()

	async def init_user_to_db(self, member):
		"""Inputs all of the data required for a user into the database,
		for when it's their first entry."""
		mid = member.id
		start_time = int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp())

		# Initiate this member with their first values into the table
		self.cursor.execute("begin")
		self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (mid, start_time, 0, str(member.status)))
		self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (mid, start_time, 1, str(member.display_name)))
		self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (mid, start_time, 2, f"{member.avatar}.png"))
		act = member.activity.name if member.activity is not None else ""
		self.cursor.execute("INSERT INTO activity VALUES (?, ?, ?, ?)", (mid, start_time, 3, act))
		self.cursor.execute("commit")

		await member.avatar_url_as(format="png", size=4096).save(f"saved_data\\{member.avatar}.png")  # Download the avatar of the user.

	# if you're not me and you're going through my code, feel free to implement these ideas yourself.
	# I don't think I have any plans to work on this longterm, since it's just a goofy sideproject.
	# IDEA: Add a "Add target" command?
	# IDEA: Add a "timelapse" role, which will track anyone who has this role.
	# IDEA: I could have indexed what they're using (client, web, mobile) and added it as a little light by the user


def setup(bot):
	bot.add_cog(TimeLapse(bot))