# Discord Verification Bot

## Overview
This is a Discord bot that automatically manages member verification for Discord servers. When new members join, they receive a "Pending" role and must be verified by admins before gaining full access.

## Features
1. **Auto-role assignment**: New members automatically get a @Pending role when they join
2. **Verification system**: Bot posts a verification message in #verify channel
3. **Admin verification**: Admins click ✅ reaction to verify users
4. **Role management**: Verified users get @Pending removed and @Member role added

## Setup Requirements

### 1. Discord Bot Token
The bot token is already configured in Replit Secrets as `DISCORD_BOT_TOKEN`.

### 2. Enable Privileged Intents (CRITICAL)
**You must enable these in the Discord Developer Portal for the bot to work:**

1. Go to https://discord.com/developers/applications
2. Select your bot application
3. Click "Bot" in the left sidebar
4. Scroll down to "Privileged Gateway Intents"
5. Enable these two intents:
   - ✅ **SERVER MEMBERS INTENT** - Required for member join events
   - ✅ **MESSAGE CONTENT INTENT** - Required for reading messages
6. Click "Save Changes"

### 3. Discord Server Setup
Your Discord server needs:
- A channel named `verify` (the bot will post verification messages here)
- The bot must have permissions to:
  - Manage Roles
  - Send Messages
  - Add Reactions
  - Read Message History

The bot will automatically create `@Pending` and `@Member` roles if they don't exist.

### 4. Invite Bot to Server
Use this URL format to invite your bot:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=268445760&scope=bot
```
Replace `YOUR_CLIENT_ID` with your bot's client ID from the Developer Portal.

## How It Works
1. User joins the server → Gets @Pending role automatically
2. Bot sends message in #verify: "User @username is waiting to be verified"
3. Bot adds ✅ reaction to the message
4. Admin clicks ✅ reaction
5. Bot removes @Pending role and adds @Member role to the user
6. Bot confirms verification in the channel

## Current Status
- Bot code: ✅ Complete
- Dependencies: ✅ Installed
- Token: ✅ Configured
- **Privileged Intents: ⚠️ Needs to be enabled in Discord Developer Portal**

## Running the Bot
The bot runs automatically via the "Discord Bot" workflow. Once privileged intents are enabled, the bot will start successfully and monitor for new members.
