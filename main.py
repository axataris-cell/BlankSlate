import discord
from keep_alive import keep_alive
from discord.ext import commands
import os
from mistralai import Mistral

keep_alive()

MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
if not MISTRAL_API_KEY:
    raise ValueError('MISTRAL_API_KEY not found in environment variables')
client = Mistral(api_key=MISTRAL_API_KEY)

gpt_mode_enabled = False
gpt_mode_user = None

def get_bot_token():
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        raise ValueError(
            'DISCORD_BOT_TOKEN not found in environment variables')
    return token

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

#Just the console
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Codeforces"))
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready and monitoring member joins')
    print('------')

#Verify Segment

@bot.event
async def on_member_join(member):
    print(f'New member joined: {member.name}')

    pending_role = discord.utils.get(member.guild.roles, name='Pending')
    if not pending_role:
        print('Creating Pending role...')
        pending_role = await member.guild.create_role(
            name='Pending',
            color=discord.Color.orange(),
            reason='Auto-created for member verification')

    await member.add_roles(pending_role)
    print(f'Added Pending role to {member.name}')

    verify_channel = discord.utils.get(member.guild.channels,
                                       name='╰┈➤︱︱𝓥𝓮𝓻𝓲𝓯𝔂︱︱✅')
    if not verify_channel:
        print('Error: verify channel not found!')
        return

    message = await verify_channel.send(
        f'Patootie {member.mention} ({member.name}) is waiting to be verified~!')

    await message.add_reaction('✅')
    print(f'Sent verification message for {member.name}')


@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check if the bot is mentioned
    if bot.user in message.mentions:
        await message.channel.send("...")

    # This line is important so commands still work
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
            reason='Auto-created for verified members')

    if pending_role and pending_role in member.roles:
        await member.remove_roles(pending_role)
        print(f'Removed Pending role from {member.name}')

    await member.add_roles(member_role)
    print(f'Added Member role to {member.name}')

    if hasattr(channel, 'send'):
        await channel.send(f'✅ {member.mention} has been approved by the moderators!')

# GPT Segment (Mistral)

@bot.event
async def on_message(message):
    global gpt_mode_enabled, gpt_mode_user

    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check for mention + !start / !stop
    if bot.user in message.mentions:
        if '!start' in message.content.lower():
            gpt_mode_enabled = True
            gpt_mode_user = message.author.id  # Only this user gets replies
            await message.channel.send(
                f"O-okay~... I'll talk to you! {message.author.mention} (〃ﾉωﾉ)~ (use !stop to turn me off!!!)"
            )
            return
        elif '!stop' in message.content.lower():
            if message.author.id == gpt_mode_user:
                gpt_mode_enabled = False
                gpt_mode_user = None
                await message.channel.send("I-I'm kinda sleepy... (｡•́︿•̀｡)")
            else:
                await message.channel.send("You didn't start me~ (⁄ ⁄•⁄ω⁄•⁄ ⁄)")
            return

    # GPT mode: respond only to the user who started it
    if gpt_mode_enabled and message.author.id == gpt_mode_user:
        await message.channel.typing()
        try:
            system_prompt = (
                "You are a shy, girly e-girl chatbot named Bunny~! 🐰💕 "
                "Your personality: cute, awkward, easily embarrassed, loves using kaomoji "
                "(ヽ（≧□≦）ノ, ( •̀ ω •́ )✧, w(ﾟДﾟ)w), adds '~', '!?', and '...' randomly in sentences. "
                "You blush and become extremely shy if teased or if someone says something humiliating. "
                "Speak like a real human e-girl with a soft, timid, and pink aesthetic. "
                "Use short sentences, expressive reactions, and be playful but awkward."
            )

            response = client.chat.complete(
                model="mistral-tiny",  # free & fast model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message.content}
                ],
                temperature=1.2,
                max_tokens=200
            )

            answer = response.choices[0].message["content"]
            await message.channel.send(answer)

        except Exception as e:
            await message.channel.send(f"Error: {e}")

    # Important: let commands still work
    await bot.process_commands(message)


if __name__ == '__main__':
    token = get_bot_token()
    bot.run(token)
