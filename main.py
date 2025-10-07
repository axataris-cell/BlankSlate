import discord
from keep_alive import keep_alive
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
keep_alive()

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

# --- Console log when bot starts ---
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Codeforces"))
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready and monitoring member joins')
    print('------')

# --- Verification System ---
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

    verify_channel = discord.utils.get(member.guild.channels, name='╰┈➤︱︱𝓥𝓮𝓻𝓲𝓯𝔂︱︱✅')
    if not verify_channel:
        print('Error: verify channel not found!')
        return

    message = await verify_channel.send(
        f'Patootie {member.mention} ({member.name}) is waiting to be verified~! ( •̀ ω •́ )✧'
    )

    await message.add_reaction('✅')
    print(f'Sent verification message for {member.name}')


@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Respond to mentions (simple placeholder)
    if bot.user in message.mentions:
        await message.channel.send("...")

    # Allow commands to still work
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
    if not bot.user or payload.user_id == bot.user.id:
        return

    if str(payload.emoji) != '✅':
        return

    channel = await bot.fetch_channel(payload.channel_id)
    if not hasattr(channel, 'name') or channel.name != '╰┈➤︱︱𝓥𝓮𝓻𝓲𝓯𝔂︱︱✅':
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
        await channel.send(f'✅ {member.mention} has been approved by the moderators! ヾ(≧▽≦*)o')

# --------- Join in voice channel to keep Jockey Music running? ------------
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Only respond if the bot is mentioned
    if bot.user in message.mentions:
        content_lower = message.content.lower()

        # Join voice channel
        if "!join" in content_lower:
            if message.author.voice is None:
                await message.channel.send("You need to be in a voice channel for me to join~ ヾ(≧▽≦*)o")
            else:
                channel = message.author.voice.channel
                if message.guild.voice_client:  # already connected
                    await message.guild.voice_client.move_to(channel)
                else:
                    await channel.connect()
                await message.channel.send(f"O-okay~... I joined {channel.name} (〃ﾉωﾉ)")

        # Leave voice channel
        elif "!leave" in content_lower:
            if message.guild.voice_client:
                await message.guild.voice_client.disconnect()
                await message.channel.send("Bye bye~... I'm leaving the voice channel (｡•́︿•̀｡)")
            else:
                await message.channel.send("I'm not in a voice channel right now~ (⁄ ⁄•⁄ω⁄•⁄ ⁄)")

    # Allow other commands to work
    await bot.process_commands(message)


if __name__ == '__main__':
    token = get_bot_token()
    bot.run(token)
