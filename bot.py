import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
import os
import datetime
import json

load_dotenv()

# -- CONSTANTS -- #
TOKEN = os.getenv("DISCORD_CLIENT_TOKEN")
STAFF_ROLE = 1224419530781233296
HICOM_ROLE = 1235986054465585173
WEEKLY_REPORT_CHANNEL = 1238485805824086076

# -- Initialisation -- #
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client=client)


# -- Events -- #
@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(status=discord.Status.online,activity=discord.CustomActivity(name="Watching VRTX Development"))

    if not weeklyreport.is_running():
        weeklyreport.start()

@tasks.loop(seconds=60)
async def weeklyreport():
    now = datetime.datetime.now()
    if now.weekday() == 6 and now.hour == 17 and now.minute == 0:  # 17:00 UTC Sunday
        with open("points.json","r") as f:
            data = json.load(f)

        channel = await client.fetch_channel(WEEKLY_REPORT_CHANNEL)
        embed = discord.Embed(title="Weekly Quota Points Report",description="Weekly report on all current quota point information.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        for user in data:
            member = await client.fetch_user(user)
            embed.add_field(name=member.display_name,value=f"{data[user]} quota points",inline=False)
        await channel.send(embed=embed)

        with open("points.json","w") as f:
            json.dump({},f)
        
        embed = discord.Embed(title="Quota Point Reset",description="All quota points have been reset!").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await channel.send(embed=embed)

# -- Commands -- #
@tree.command(name="add",description="Add quota points to a user [STAFF ONLY]")
@app_commands.describe(member="User to add to",points="Number of quota points to add")
async def add(interaction:discord.Interaction,member:discord.Member,points:int):
    role = interaction.guild.get_role(STAFF_ROLE)
    if role in interaction.user.roles:
        await interaction.response.defer()
        user = str(member.id)
        with open("points.json","r") as f:
            data = json.load(f)
        
        try:
            data[user] = int(data[user])+points
        except KeyError:
            data[user] = points

        with open("points.json","w") as f:
            json.dump(data,f)

        embed = discord.Embed(title="Added Quota Points",description="Successfully added quota points to user.").add_field(name="User",value=user).add_field(name="Added",value=f"{points} quota points").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(title="Error",colour=discord.Colour.red(),description="You are not authorized to run this command.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.response.send_message(embed=embed)


@tree.command(name="remove",description="Remove quota points from a user [HICOM ONLY]")
@app_commands.describe(member="User to remove from",points="Number of quota points to remove")
async def remove(interaction: discord.Interaction,member: discord.Member,points:int):
    role = interaction.guild.get_role(HICOM_ROLE)
    if role in interaction.user.roles:
        await interaction.response.defer()
        user = str(member.id)
        with open("points.json","r") as f:
            data = json.load(f)
        
        try:
            if int(data[user])-points <= 0:
                data[user] = 0
            else:
                data[user] = int(data[user])-points
        except KeyError:
            data[user] = 0

        with open("points.json","w") as f:
            json.dump(data,f)

        embed = discord.Embed(title="Removed Quota Points",description="Successfully removed quota points from user.").add_field(name="User",value=user).add_field(name="Removed",value=f"{points} quota points").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(title="Error",colour=discord.Colour.red(),description="You are not authorized to run this command.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.response.send_message(embed=embed)

@tree.command(name="points",description="Check the quota points of a user")
@app_commands.describe(member="User to check")
async def points(interaction:discord.Interaction,member:discord.Member=None):
    await interaction.response.defer()
    if member == None:
        member = interaction.user
    user = str(member.id)
    with open("points.json","r") as f:
        data = json.load(f)
    
    try:
        pointsData = data[user]
    except KeyError:
        pointsData = 0
    
    embed = discord.Embed(title="Quota Points Check",description="Quota Points information for the requested user.").add_field(name="Username",value=f"{member.display_name} ({user})").add_field(name="Quota Points",value=f"{pointsData} quota points").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ ApolloSystems")
    await interaction.followup.send(embed=embed)

@tree.command(name="report",description="Display quota points information")
async def report(interaction: discord.Interaction):
        with open("points.json","r") as f:
            data = json.load(f)

        embed = discord.Embed(title="Quota Points Report",description="Report on all current quota point information.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        for user in data:
            member = await client.fetch_user(user)
            embed.add_field(name=member.display_name,value=f"{data[user]} quota points",inline=False)
        await interaction.response.send_message(embed=embed)

client.run(TOKEN)