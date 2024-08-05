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
WEEKLY_REPORT_CHANNEL = 1254797706677977100 

# -- Initialisation -- #
client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client=client)

# -- Events -- #
@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(status=discord.Status.online,activity=discord.CustomActivity(name="Watching VRTX Development"))

    with open("settings.json","r") as f:
        settings = json.load(f)
    
    global STAFF_ROLE,MAIN_GROUP,SECONDARY_GROUP
    STAFF_ROLE,MAIN_GROUP,SECONDARY_GROUP = settings["STAFF_ROLE"],settings["MAIN_GROUP"],settings["SECONDARY_GROUP"]

# -- Commands -- #
@tree.command(name="infractions-add",description="Add infractions to a user [STAFF ONLY]")
@app_commands.describe(member="User to add to",points="Number of infractions to add")
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

        embed = discord.Embed(title="Added infractions",description="Successfully added infractions to user.").add_field(name="User",value=user).add_field(name="Added",value=f"{points} infractions").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(title="Error",colour=discord.Colour.red(),description="You are not authorized to run this command.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.response.send_message(embed=embed)


@tree.command(name="infractions-remove",description="Remove infractions from a user [STAFF ONLY]")
@app_commands.describe(member="User to remove from",points="Number of infractions to remove")
async def remove(interaction: discord.Interaction,member: discord.Member,points:int):
    role = interaction.guild.get_role(STAFF_ROLE)
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

        embed = discord.Embed(title="Removed infractions",description="Successfully removed infractions from user.").add_field(name="User",value=user).add_field(name="Removed",value=f"{points} registered infractions").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(title="Error",colour=discord.Colour.red(),description="You are not authorized to run this command.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        await interaction.response.send_message(embed=embed)

@tree.command(name="infractions-check",description="Check the infractions of a user")
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
    
    embed = discord.Embed(title="Infractions Check",description="Infraction information for the requested user.").add_field(name="Username",value=f"{member.display_name} ({user})").add_field(name="Infractions",value=f"{pointsData} infractions").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ ApolloSystems")
    await interaction.followup.send(embed=embed)

@tree.command(name="infractions-report",description="Display infractions information")
async def report(interaction: discord.Interaction):
        with open("points.json","r") as f:
            data = json.load(f)

        embed = discord.Embed(title="Infractions Report",description="Report on all current infactions.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")
        for user in data:
            member = await client.fetch_user(user)
            embed.add_field(name=member.display_name,value=f"{data[user]} infractions",inline=False)
        await interaction.response.send_message(embed=embed)

@tree.command(name="settings",description="Edit settings")
@app_commands.describe(setting="Setting to edit",value="Value to update the setting")
@app_commands.choices(setting=[app_commands.Choice("Staff Role"),app_commands.Choice("Main Group"),app_commands.Choice("Secondary Group")])
async def settings(interaction: discord.Interaction, setting: str,value: int):
    with open("settings.json","r") as f:
        settings = json.load(f)

    embed = discord.Embed(title="Settings Update",description=f"Settings succesfully updated by {interaction.user.display_name}.").set_footer(text="VRTX Bot | Developed by JaguarSympathy @ Apollo Systems")

    match setting:
        case "Staff Role":
            settings["STAFF_ROLE"] = value
            STAFF_ROLE = value
            embed.add_field(name="Staff Role Update",value=f"Set `STAFF ROLE` to `{value}`.")
        case "Main Group":
            settings["MAIN_GROUP"] = value
            MAIN_GROUP = value
            embed.add_field(name="Main Group Update",value=f"Set `MAIN GROUP ID` to `{value}`.")
        case "Secondary Group":
            settings["SECONDARY_GROUP"] = value
            SECONDARY_GROUP = value
            embed.add_field(name="Secondary Group Update",value=f"Set `SECONDARY GROUP ID` to `{value}`.")

    with open("settings.json","w") as f:
        json.dump(settings,f)

    await interaction.response.send_message(embed=embed)

client.run(TOKEN)