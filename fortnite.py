import fortnitepy
from fortnitepy.errors import *
import time as delay
import datetime
import json
import aiohttp
import time
import logging
import functools
import sys
import os
import random
import json
import os
import asyncio
import BenBotAsync
import re
import random
from colorama import init
init(autoreset=True)
from colorama import Fore, Back, Style


filename = 'config.json'


def get_device_auth_details():
    if os.path.isfile(filename):
        with open(filename, 'r') as fp:
            return json.load(fp)
    return {}

with open('config.json') as f:
    print(f' [BOT] [smh] Loading config.')
    data = json.load(f)
    print(f' [BOT] [smh] Config loaded.')

def store_device_auth_details(email, details):
    existing = get_device_auth_details()
    existing[email] = details

    with open(filename, 'w') as fp:
        json.dump(existing, fp)

email="pedromelendezr@outlook.com"
password="canada341513349"
device_auth_details = get_device_auth_details().get(email, {})
client = fortnitepy.Client(
    auth=fortnitepy.AdvancedAuth(
        email="pedromelendezr@outlook.com",
        password="canada341513349",
        prompt_exchange_code=True,
        delete_existing_device_auths=True,
        **device_auth_details
    )
)


@client.event
async def event_device_auth_generate(details, email):
    store_device_auth_details(email, details)


@client.event
async def event_ready():
    global ready
    print('Client ready as {0.user.display_name}'.format(client))
    member = client.party.me
    await member.edit_and_keep(
        functools.partial(
            fortnitepy.ClientPartyMember.set_outfit,
            asset=data['cid']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_backpack,
            asset=data['bid']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_pickaxe,
            asset=data['pid']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_banner,
            icon=data['banner'],
            color=data['banner_color'],
            season_level=data['level']
        ),
        functools.partial(
            fortnitepy.ClientPartyMember.set_battlepass_info,
            has_purchased=True,
            level=data['bp_tier']
        )
    )





@client.event
async def event_friend_request(request):
    #await request.accept()
    if data['friendaccept'].lower() == 'true':
        if request.display_name not in data['BlockList']:
            try:
                await request.accept()
                print(f" [BOT] [start] Accepted friend request from: {request.display_name}")
            except Exception as e:
                pass
        elif request.display_name in data['BlockList']:
            print(f" [BOT] [start] Never Accepted friend reqest from: " + Fore.RED + f"{request.display_name}")
    if data['friendaccept'].lower() == 'false':
        if request.display_name in data['FullAccess']:
            try:
                await request.accept()
                print(f" [BOT] [smh] Accepted friend request from: {request.display_name}")
            except Exception as e:
                pass
        else:
            print(f" [BOT] [smh] Never accepted friend request from: {request.display_name}")




@client.event
async def event_friend_message(message):

    args = message.content.split()
    split = args[1:]
    joinedArguments = " ".join(split)
    print(Fore.BLUE + ' [BOT] [' + message.author.display_name + ']  {0.content}'.format(message))
    buff = 0
    if "!git" in args[0]:
        await client.party.set_playlist(
            playlist=args[1],
            region=fortnitepy.Region.NAEAST
        )
        #await client.party.set_custom_key(
         #   key="doritos"
        #)
        user = await client.fetch_profile(message.author.display_name)
        member = client.party.members.get(user.id)
        await member.promote()
        await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        #await client.party.me.leave()
    
    if "Playlist_" in args[0]:
        try:
            await client.party.set_playlist(playlist=args[0])
        except Exception as e:
            pass
            await message.reply(f"Couldn't set gamemode to {args[0]}, as I'm not party leader.")
            print(Fore.RED + f" [DATABOT] [{getTime()}] [ERROR] Failed to set gamemode as I don't have the required permissions." + Fore.WHITE)

    if "!join" in args[0]:
        user = await client.fetch_profile(args[1], cache=False, raw=False)
        friend = client.get_friend(user.id)
        await friend.join_party()
        await message.reply(f"Joining {friend.display_name}'s party.")
        print(Fore.GREEN + f" [BOT] [{message.author.display_name}] joining party")
#set skin    
    if "!skin" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=joinedArguments,
                    backendType="AthenaCharacter"
                )
                await client.party.me.set_outfit(asset=cosmetic.id)
                await message.reply('Skin set to ' + f'{cosmetic.name}')
                print(Fore.GREEN + f" [BOT] [{message.author.display_name}] set skin to {cosmetic.name}")
            except BenBotAsync.exceptions.NotFound:
                await message.reply(f'Could not find a skin named: {joinedArguments}')
                print(Fore.GREEN + f" [BOT] [{message.author.display_name}] failed to aquire skin")
#kick user    
    if "!kick" in args[0].lower() and message.author.display_name in data['FullAccess']:
        user = await client.fetch_profile(joinedArguments)
        member = client.party.members.get(user.id)
        if member is None:
            await message.reply("Couldn't find that user, are you sure they're in the party?")
        else:
            try:
                await member.kick()
                await message.reply(f"Kicked user: {member.display_name}.")
                print(Fore.GREEN + f" [BOT] [{message.author.display_name}] Kicked user: {member.display_name}")
            except Exception as e:
                pass
                await message.reply(f"Couldn't kick {member.display_name}, as I'm not party leader.")
                print(Fore.RED + f" [BOT] [{message.author.display_name}] [ERROR] Failed to kick member as I don't have the required permissions." + Fore.WHITE)
        if message.author.display_name not in data['FullAccess']:
            await message.reply(f"You don't have access to this command!")
            print(f"[bot] [{message.author.display_name}] failed to kick member")
#unready
    if ("!unready" in args[0].lower()) or ("!sitin" in args[0].lower()):
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
            print(f"[bot] [{message.author.display_name}] failed to sitout")
        else:
            await client.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
            await message.reply('Now Unready!')
            print(Fore.GREEN + f"[bot] [{message.author.display_name}] made me unready")
#ready
    if ("!ready" in args[0].lower()) or ("!sitin" in args[0].lower()):
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
            print(f"[bot] [{message.author.display_name}] failed to sitout")
        else:
            await client.party.me.set_ready(fortnitepy.ReadyState.READY)
            await message.reply('Now ready!')
            print(Fore.GREEN + f"[bot] [{message.author.display_name}] made me ready")
#sitout            
    if "!sitout" in args[0].lower():
        try:
            if message.author.display_name in data['BlockList']:
                await message.reply("You don't have access to this command!")
            else:
                user = await client.fetch_profile(message.author.display_name)
                member = client.party.members.get(user.id)
                await member.promote()
                await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
                await message.reply('Now Sitting Out!')
                print(Fore.GREEN + f"[bot] [{message.author.display_name}] sat out")
        except Exception:
            await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
            print(Fore.GREEN + f"[bot] [{message.author.display_name}] sat out")

    if "!fakeout" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
            await message.reply('Now Sitting Out!')
            print(Fore.GREEN + f"[bot] [{message.author.display_name}] sat out")
#reboot
    if "!reboot" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            await client.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
            await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
            await client.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
            await message.reply('Now Sitting Out!')
            print(Fore.GREEN + f"[bot] [{message.author.display_name}] sat out")
#leave   
    if "!leave" in args[0].lower():
            await client.party.me.set_emote('EID_Snap')
            delay.sleep(2)
            await client.party.me.leave()
            await message.reply('Bye!')
            print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Left the party as I was requested.')
#do emote
    if "!emote" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=joinedArguments,
                    backendType="AthenaDance"
                )
                await client.party.me.clear_emote()
                if cosmetic.id == "EID_ArtGiant":
                    if buff == 1:
                        await client.party.me.set_emote(asset="EID_TakeTheL")
                        await message.reply('you know the rules and so do i')
                        print(Fore.GREEN + f"[bot] [{message.author.display_name}] took the l")
                    else:
                        await client.party.me.set_emote(asset="EID_NeverGonna")
                        await message.reply('you know the rules and so do i')
                        print(Fore.GREEN + f"[bot] [{message.author.display_name}] got rickrolled")
                else:
                    await client.party.me.set_emote(asset=cosmetic.id)
                    await message.reply('Emote set to ' + f'{cosmetic.name}')
                    print(Fore.GREEN + f"[bot] [{message.author.display_name}] emote set to " + f'{cosmetic.name}')
            except BenBotAsync.exceptions.NotFound:
                await message.reply(f'Could not find an emote named: {joinedArguments}')
                print(Fore.RED + f"[bot] [{message.author.display_name}] could not find emote")
#find skin id
    if "!findcid" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=joinedArguments,
                    backendType="AthenaCharacter"
                )
                await message.reply(f'The CID for {cosmetic.name} is: ' + f'{cosmetic.id}')
                print(Fore.GREEN + f" [BOT] [{message.author.display_name}] CID for {cosmetic.name}: {cosmetic.id}")
            except BenBotAsync.exceptions.NotFound:
                await message.reply(f'Could not find a cid for the skin: {joinedArguments}')
#find emote id
    if "!findeid" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=joinedArguments,
                    backendType="AthenaDance"
                )
                await message.reply(f'The EID for {cosmetic.name} is: ' + f'{cosmetic.id}')
                print(Fore.GREEN + f" [BOT] [smh] EID for {cosmetic.name}: {cosmetic.id}")
            except BenBotAsync.exceptions.NotFound:
                await message.reply(f'Could not find a eid for the emote: {joinedArguments}')
#skin by skin id
    if "CID_" in args[0]:
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            await client.party.me.set_outfit(
                asset=args[0]
            )
            await message.reply(f'Skin set to {args[0]}')
            print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Skin set to ' + args[0])
#emote by emote id
    if "EID_" in args[0]:
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            result = args[0].lower()
            rng = random.randint(1, 2)
            if result == "eid_artgiant":
                if rng == 2:
                    await client.party.me.clear_emote()
                    await client.party.me.set_emote(
                        asset="EID_NeverGonna"
                    )
                    print(Fore.GREEN + f"[bot] [{message.author.display_name}] got rickrolled.")
                else:
                    await client.party.me.clear_emote()
                    await client.party.me.set_emote(
                        asset="EID_Texting"
                    )
                    print(Fore.GREEN + f"[bot] [{message.author.display_name}] took the l.")
            else:
                await client.party.me.clear_emote()
                await client.party.me.set_emote(
                    asset=args[0]
                )
                print(Fore.GREEN + f"[bot] [{message.author.display_name}] emote set to " + f'{args[0]}')
            #await message.reply(Fore.GREEN + f'[bot] [{message.author.display_name}]Emote set to ' + args[0] + ".")
            #print(Fore.GREEN + f' [BOT] [{message.author.display_name}] emote set to ' + args[0])
            
#stop emoting
    if "!stop" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply("You don't have access to this command!")
        else:
            await client.party.me.clear_emote()
            await message.reply('Stopped emoting.')
            print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Stopped emoting')
#get skin with variant via variant coordinates (ie. !step skye 2 1)
    if "!step" in args[0].lower():
        if message.author.display_name in data['BlockList']:
            await message.reply('nice try, ' + message.author.display_name)
            time.sleep(1)
            await message.reply("but it seems that you do not have access to the " + args[1] + " skin.")
            print(Fore.GREEN + f' [BOT] [{message.author.display_name}] failed to set skin to ' + args[1])
            #print('[PYBOT]' + message.author.display_name + ' tried to change the skin to' + args[1])
        else:
            try:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=args[1],
                    backendType="AthenaCharacter"
                )
                await client.party.me.set_outfit(
                    asset=cosmetic.id,
                    variants=client.party.me.create_variants(
                        progressive=args[2],
                        material=args[3],
                        ))
                await message.reply('Skin set to ' + f'{joinedArguments}')
            except BenBotAsync.exceptions.NotFound:
                await message.reply(f'Could not find a skin named: {joinedArguments}')
            except IndexError:
                cosmetic = await BenBotAsync.get_cosmetic(
                    lang="en",
                    searchLang="en",
                    matchMethod="contains",
                    name=args[1],
                    backendType="AthenaCharacter"
                )
                await client.party.me.set_outfit(
                    asset=cosmetic.id,
                    variants=client.user.party.me.create_variants(
                        progressive=1,
                        material=1
                        ))
                await message.reply(f"skin is set, but style is set to default. please enter varient coordinates (eg. 1 1)")
                print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Skin set to ' + args[1] + 'including variant coordinates')
#variant coordinates but with cids
    if "!stepcid" in args[0]:
        try:
            if message.author.display_name in data['BlockList']:
                await message.reply(message.author.display_name + " is restricted from using CIDS")
            else:
                await client.party.me.set_outfit(
                    asset=args[1],
                    variants=client.party.me.create_variants(
                            progressive=args[2],
                            material=args[3]
                            ))
                await message.reply(f'Skin set')
                print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Skin set to ' + args[1])
        except IndexError:
            await client.party.me.set_outfit(
                asset=args[1],
                variants=client.party.me.create_variants(
                        progressive=1,
                        material=1
                        ))
            await message.reply(f'Skin set to {args[1]}, but style is set to default.')
            print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Skin set to the default varient of ' + args[0]) 

    if "!hdeef" in args[0]:
        try:
            if message.author.display_name in data['BlockList']:
                await message.reply(message.author.display_name + " is restricted from using CIDS")
            else:
                await client.party.me.set_outfit(
                    asset="CID_NPC_Athena_Commando_F_RebirthDefault_Henchman",
                    variants=client.party.me.create_variants(
                            progressive=args[1],
                            material=args[2]
                            ))
                await message.reply(f'Skin set')
                print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Skin set to ' + args[1])
        except IndexError:
            await client.party.me.set_outfit(
                asset="CID_NPC_Athena_Commando_F_RebirthDefault_Henchman",
                variants=client.party.me.create_variants(
                        progressive=1,
                        material=1
                        ))
            await message.reply(f'Skin set to {args[1]}, but style is set to default.')
            print(Fore.GREEN + f' [BOT] [{message.author.display_name}] Skin set to the default varient of ' + args[0])

    if "!remove" in args[0].lower() and message.author.display_name in data['FullAccess']:
        user = await client.fetch_profile(joinedArguments)
        friends = client.friends
        if user is None:
            await message.reply(f"I can't find a player with the name of {joinedArguments}.")
            print(Fore.RED + f" [PYBOT] [{message.author.display_name}] [ERROR] Unable to find a player with the name {joinedArguments}")
        else:
            try:
                if (user.id in friends):
                    await client.remove_or_decline_friend(user.id)
                    await message.reply(f"Sucessfully removed {user.display_name} as a friend.")
                    print(Fore.GREEN + f" [PYBOT] [{message.author.display_name}] {client.user.display_name} removed {user.display_name} as a friend.")
                else: 
                    await message.reply(f"I don't have {user.display_name} as a friend.")
                    print(Fore.RED + f" [PYBOT] [{message.author.display_name}] [ERROR] {client.user.display_name} tried removing {user.display_name} as a friend, but the client doesn't have the friend added." + Fore.WHITE)
            except Exception as e:
                pass
                print(Fore.RED + f" [BOT] [{message.author.display_name}] [ERROR] Something went wrong removing {joinedArguments} as a friend." + Fore.WHITE)
        if message.author.display_name not in data['FullAccess']:
            await message.reply(f"You don't have access to this command!")

    if "!reveal" in args[0].lower() and message.author.display_name in data['FullAccess']:

        friends = client.friends
        onlineFriends = []
        offlineFriends = []
        try:
            for f in friends:
                friend = client.get_friend(f)
                if friend.is_online():
                    onlineFriends.append(friend.display_name)
                else:
                    offlineFriends.append(friend.display_name)
            print(f" [PYBOT] [{message.author.display_name}] " + Fore.WHITE + "Friends List: " + Fore.GREEN + f"{len(onlineFriends)} Online " + Fore.WHITE + "/" + Fore.LIGHTBLACK_EX + f" {len(offlineFriends)} Offline " + Fore.WHITE + "/" + Fore.LIGHTWHITE_EX + f" {len(onlineFriends) + len(offlineFriends)} Total")
            for x in onlineFriends:
                if x is not None:
                    print(Fore.GREEN + " " + x + Fore.WHITE)
            for x in offlineFriends:
                if x is not None:
                    print(Fore.LIGHTBLACK_EX + " " + x + Fore.WHITE)
        except Exception as e:
            print(e)
            #pass
        await message.reply("Check the command window for the list of my friends.")   
        if message.author.display_name not in data['FullAccess']:
            await message.reply(f"You don't have access to this command!")

    if "!promote" in args[0].lower() and message.author.display_name in data['FullAccess']:
        if len(args) != 1:
            user = await client.fetch_profile(joinedArguments)
            member = client.party.members.get(user.id)
        if len(args) == 1:
            user = await client.fetch_profile(message.author.display_name)
            member = client.party.members.get(user.id)
        if member is None:
            await message.reply("Couldn't find that user, are you sure they're in the party?")
        else:
            try:
                await member.promote()
                await message.reply(f"Promoted user: {member.display_name}.")
                print(Fore.GREEN + f" [BOT] [promote] Promoted user: {member.display_name}")
            except Exception as e:
                pass
                await message.reply(f"Couldn't promote {member.display_name}, as I'm not party leader.")
                print(Fore.RED + f" [BOT] [promote] [ERROR] Failed to promote member as I don't have the required permissions." + Fore.WHITE)
        if message.author.display_name not in data['FullAccess']:
            await message.reply(f"You don't have access to this command!")

    if "!customs" in args[0]:
        await client.party.set_custom_key(
            key=args[1]
        )

        await message.reply(f'Custom matchmaking code set to: {args[1]}')
    
    if "!reed" in args[0].lower():
        tpl = client.party.playlist_info
        gg = list(tpl)
        await message.reply(gg[0])
           
@client.event
async def event_party_invite(invitation):
    await invitation.accept()
    print(Fore.GREEN + f' [BOT] [invite] Accepted party invite from {invite.sender.display_name}')


client.run()
