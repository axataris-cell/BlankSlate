import discord
from discord.ext import commands
import os

def get_bot_token():
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        raise ValueError('DISCORD_BOT_TOKEN not found in environment variables')
    return token

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready and monitoring member joins')
    print('------')

@bot.event
async def on_member_join(member):
    print(f'New member joined: {member.name}')
    
    pending_role = discord.utils.get(member.guild.roles, name='Pending')
    if not pending_role:
        print('Creating Pending role...')
        pending_role = await member.guild.create_role(
            name='Pending',
            color=discord.Color.orange(),
            reason='Auto-created for member verification'
        )
    
    await member.add_roles(pending_role)
    print(f'Added Pending role to {member.name}')
    
    verify_channel = discord.utils.get(member.guild.channels, name='verify')
    if not verify_channel:
        print('Error: #verify channel not found!')
        return
    
    message = await verify_channel.send(
        f'User {member.mention} ({member.name}) is waiting to be verified'
    )
    
    await message.add_reaction('✅')
    print(f'Sent verification message for {member.name}')

@bot.event
async def on_raw_reaction_add(payload):
    if not bot.user or payload.user_id == bot.user.id:
        return
    
    if str(payload.emoji) != '✅':
        return
    
    channel = await bot.fetch_channel(payload.channel_id)
    if not hasattr(channel, 'name') or channel.name != 'verify':
        return
    
    if not hasattr(channel, 'fetch_message'):
        return
        
    message = await channel.fetch_message(payload.message_id)
    
    if not message.mentions:
        return
    
    user_to_verify = message.mentions[0]
    guild = bot.get_guild(payload.guild_id)
    
    if not guild:
        return
        
    member = guild.get_member(user_to_verify.id)
    
    if not member:
        return
    
    pending_role = discord.utils.get(guild.roles, name='Pending')
    member_role = discord.utils.get(guild.roles, name='Member')
    
    if not member_role:
        print('Creating Member role...')
        member_role = await guild.create_role(
            name='Member',
            color=discord.Color.green(),
            reason='Auto-created for verified members'
        )
    
    if pending_role and pending_role in member.roles:
        await member.remove_roles(pending_role)
        print(f'Removed Pending role from {member.name}')
    
    await member.add_roles(member_role)
    print(f'Added Member role to {member.name}')
    
    if hasattr(channel, 'send'):
        await channel.send(f'✅ {member.mention} has been verified!')

if __name__ == '__main__':
    token = get_bot_token()
    bot.run(token)
