## vote

Start an anonymous vote with 2-10 options to choose from! (Besure to include quotes on title and options)

Usage:
`!vote <minutes> "Title" "Option 1" "Option 2" "Options up to 10"`

## endvote

Ends a currently active vote using the title of the vote. (Besure to enclose the title with quotes)

Usage:
`!endvote "title of vote"`

## create_counter

Creates a new counter voice channel with the given name. Counter types: Total members, Online members, Bots.

Usage:
`!create_counter "Counter Type" (Must be inclosed in "". Also caps are needed. This is a bug will fix later.)`

## adopt

Sends an adoption request to another member.

Usage:
`!adopt <@member>`

## marry

Sends a marriage request to another member.

Usage:
`!marry <@member>`

## family

Shows the family tree of the author.

Usage:
`!family`

## ticket

Create a new ticket channel.

Usage:
`!ticket`

## placeholder

This is a placeholder command.

Usage:
`!placeholder <usage>`

## disabled

This is a template for disabling a command!

Usage:
`!disabled`

## dbsize

Retrieves the size of all .db files in the ./data directory.

## skip

Skips the currently playing song

Usage:
`!skip`

## queue

Queues a song to be played next

Usage:
`!queue <song url>`

## volume

Sets the bots volume within a voice channel

Usage:
`!volume <value 0-100>`

## clear

Clears the song queue

Usage:
`!clear`

## join

Requests bot to join voice channel that requested user is in

Usage:
`!join`

## leave

Requests bot to leave voice channel it is in

Usage:
`!leave`

## play

Plays requested song in voice channel

Usage:
`!play <song url>`

## pause

Pauses currently playing music, resume with resume command

Usage:
`!pause`

## resume

Resumes paused music

Usage:
`!resume`

## stop

Stops the music, sometimes clears queue

Usage:
`!stop`

## ping

Shows the bot's latency and API ping.

Usage:
`!ping`

## info

Provides detailed information about the bot.

Usage:
`!info`

## !invite

Generates an invite link for the bot.

## !stats

Shows the bot's current stats, including the number of guilds, users, and more.

## !update

Shows the current uptime of the bot since last restart.

## lifetime

Shows the total lifetime uptime of the bot.

Usage:
`!lifetime`

## scrabble

Start or play a game of Scrabble! Use '!scrabble start' to start a new game and other commands to interact with the game.

## monopoly

Start or play a game of Monopoly! Use '!monopoly start' to start a new game and other commands to interact with the game.

## chess

Main chess command.

## checkers

Start or play a game of Checkers! Use '!checkers start' to start a new game and other commands to interact with the game.

Usage:
`!checkers <command> (Will add list later).`

## sorry

Start or play a game of Sorry! Use '!sorry start' to start a new game and other commands to interact with the game.

## uno

Start or play a game of Uno! Use '!uno start' to start a new game and other commands to interact with the game.

## tictactoe

Start or play a game of Tic-Tac-Toe! Use '!tictactoe start' to start a new game and '!tictactoe move <position>' to make a move.

## hangman

Start or play a game of Hangman! Use '!hangman start' to start a new game and '!hangman guess <letter>' to make a guess.

## dnd

This base of the dnd commands, few options to use: create, show, & card. More to come soon!

Usage:
`!dnd`

## roll

Rolls a dice with the specified format (e.g., 2d6).

Usage:
`!roll NdN`

## coinflip

Flips a coin and shows the result.

Usage:
`!coinflip`

## random

Shows a help message for the random group command.

## animediff

Generates an anime-style image based on the provided prompt and sends the MD5 hash of the image data.

Usage:
`!animediff <prompt>, <another prompt>, so on`

## dnddiff

Generates an dnd-style image based on the provided prompt and sends the MD5 hash of the image data.

Usage:
`!dnddiff <prompt>, <another prompt>, so on`

## imagediff

Generates a realistic image based on the provided prompt and sends the MD5 hash of the image data.

Usage:
`!imagediff <prompt>, <another prompt>, so on`

## package_info

Provides information about a pip package.

## donate

Returns the donation address for the specified method.

Usage:
`!donate <method>`

## connect_channel

Connect a the current channel to the relay channels. (It's like a large groupchat across servers!)

Usage:
`!connect_channel`

## disconnect_channel

Disconnect the channel connected to the relay channels.

Usage:
`!disconnect_channel`

## welcomemsg

Set a custom welcome message.

Usage:
`!welcomemsg <message>`

## welcomeremove

Remove the set welcome message.

Usage:
`!welcomeremove`

## disable

Disable a specific command.

Usage:
`!disable <command_name>`

## enable

Enable a previously disabled command.

Usage:
`!enable <command_name>`

## hyper

This is the hyper command.

Usage:
`!hyper <usage>`

## embed

This is the embed command.

Usage:
`!embed <message>`

## addbot

Adds a bot using its client ID.

Usage:
`!addbot <client ID>`

## balance

Check your balance or someone else's by mentioning them.

## daily

Receive your daily gold.

## invest

Invest your gold to earn more.

## uninvest

Uninvest your gold, with a 10% penalty.

## give

Give gold to someone.

## gamble

Gamble your gold for a chance to win the pot.

## jackpot

Check the current jackpot amount.

## xp

Used to check your own or someone elses xp and level!

Usage:
`!xp` or `!xp @member`

## leaderboard

Check a servers leaderboard, can take a while sometimes.

Usage:
`!leaderboard`

## lock

Locks a channel.

Usage:
`!lock`

## unlock

Unlocks a channel.

Usage:
`!unlock`

## kick

Kicks a user out of the server.

Usage:
`!kick <@mention>`

Usage:
`!setprefix <prefix you want> (This can be literaly anything you like, just please make it a normal one please.)`

## ban

Bans a user from the server.

Usage:
`!ban <@mention>`

## unban

Unbans a user.

Usage:
`!unban <userID>`

## purge

Clears a specified amount of messages in the channel.

Usage:
`!purge <number of messages>`

## mute

Mutes a user.

Usage:
`!mute <@mention>`

## unmute

Unmutes a user.

Usage:
`!unmute <@mention>`

## user

Shows info about the mentioned user.

Usage:
`!user <mention>`

## !addmod <@mention>

Adds a role to allow moderation.

## removemod

Removes a role to allow moderation.

Usage:
`!removemod <@mention>`

## show_roles

Shows the set join and verify roles for the guild.

Usage:
`!show_roles`

## set_join_role

Sets the role to give to users when they first join.

Usage:
`!set_join_role <@role>`

## set_verify_role

Sets the role to give to users when they are verified.

Usage:
`!set_verify_role <@role>`

## verify

Sends a verification CAPTCHA to the user's DMs and alerts the user to check their DMs.

Usage:
`!verify`

