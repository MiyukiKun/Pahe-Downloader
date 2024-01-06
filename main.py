from config import bot
from telethon import events
import pahe, kwik_token, helper
from FastTelethonhelper import fast_upload
import os
from mongodb import AutoAnimeDB

AutoAnimeDB = AutoAnimeDB()

@bot.on(events.NewMessage(pattern="/start"))
async def _(event):
    await event.reply("Go Away.")


@bot.on(events.NewMessage(pattern="/search"))
async def _(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message('What is the name of the anime you want?')
        anime_name = await conv.get_response()
        anime_name = anime_name.raw_text
        await conv.send_message('loading...')
        options = pahe.search_apahe(anime_name)["data"]
        txt = "Choose from options below, reply a number only\n"
        for n, i in enumerate(options):
            txt += f"{n+1}. {i['title']}\n"
        
        await conv.send_message(txt)
        answer = await conv.get_response()
        answer = int(answer.raw_text) - 1
        choice = options[answer]
        txt=f"Title:{choice['title']}\nType:{choice['type']}\nEpisodes:{choice['episodes']}\nStatus:{choice['status']}"
        await conv.send_message(txt, file=choice["poster"])
        
        await conv.send_message("The episode range you want. example: 1-6")
        range = await conv.get_response()
        range = list(map(int, range.raw_text.split("-")))
        eps_ids = pahe.mid_apahe(choice["session"], range)
        eps_list = pahe.dl_apahe1(choice["session"], eps_ids)
        resolutions = "Choose option to download. Reply with number only\n0.All resolutions\n"
        for n, i in enumerate(eps_list[1]):
            resolutions += f"{n+1}. {i[1]} {i[2]}\n"

        await conv.send_message(resolutions)
        resolution_choice = await conv.get_response()
        try:
            resolution_choice = int(resolution_choice.raw_text) - 1
        except:
            resolution_choice = resolution_choice.raw_text

        await conv.send_message("Send me file name you want on these files in the following format.\nAnime Name - S1 UwU RES LANG.mkv\n UwU will be replaced by ep number.\nRES will be replaced by resolution\nLANG will be replaced by either sub/dub")
        name_format = await conv.get_response()
        name_format = name_format.raw_text.strip()
        thumb = choice["poster"]
        thumb = await helper.DownLoadFile(thumb, file_name=f"{anime_name} thumb.png")

    if resolution_choice == -1:
        for k, v in eps_list.items():
            for i in v:
                dl_link = pahe.dl_apahe2(i[0])
                dl_link = kwik_token.get_dl_link(dl_link)
                ep_num = k + range[0] - 1
                res = i[1].split()[0]
                lang = i[2]
                file_name = name_format.replace("UwU", str(ep_num)).replace("RES", res).replace("LANG", lang)
                # reply = await event.reply(f"Starting download {file_name}")
                
                file = await helper.DownLoadFile(dl_link, file_name=file_name)
                res_file = await fast_upload(client = bot, file_location = file)  #, reply = reply)
                await bot.send_message(event.chat_id, f"{file_name.replace('.mkv', '').replace('.mp4', '')}", file=res_file, force_document=True, thumb=thumb)
                # await reply.delete()
                os.remove(file)
    
    elif resolution_choice == "sub" or resolution_choice == "dub":
        for k, v in eps_list.items():
            counter = 0
            for i in reversed(v):
                if counter == "3":
                    break
                res = i[1]
                lang = i[2]
                if resolution_choice != lang.lower():
                    continue
                counter += 1
                dl_link = pahe.dl_apahe2(i[0])
                dl_link = kwik_token.get_dl_link(dl_link)
                file_name = name_format.replace("UwU", str(k)).replace("RES", res).replace("LANG", lang)
                # reply = await event.reply(f"Starting download {file_name}")
                
                file = await helper.DownLoadFile(dl_link, file_name=file_name)
                res_file = await fast_upload(client = bot, file_location = file)       # , reply = reply)
                await bot.send_message(event.chat_id, f"{file_name.replace('.mkv', '').replace('.mp4', '')}", file=res_file, force_document=True, thumb=thumb)
                # await reply.delete()
                os.remove(file)
    
    else:
        for k, v in eps_list.items():
            dl_link = pahe.dl_apahe2(v[resolution_choice][0])
            dl_link = kwik_token.get_dl_link(dl_link)
            ep_num = k + range[0] - 1
            res = v[resolution_choice][1]
            lang = v[resolution_choice][2]
            file_name = name_format.replace("UwU", str(ep_num)).replace("RES", str(res)).replace("LANG", lang)
            # reply = await event.reply(f"Starting download {file_name}")
            file = await helper.DownLoadFile(dl_link, file_name=file_name)

            res_file = await fast_upload(client = bot, file_location = file)    # , reply = reply)
            await bot.send_message(event.chat_id, f"{file_name.replace('.mkv', '').replace('.mp4', '')}", file=res_file, force_document=True, thumb=thumb)
            os.remove(file)
            # reply.delete()


@bot.on(events.NewMessage(pattern="/update"))
async def _(event):
    animedb = AutoAnimeDB.full()
    main_reply = await event.reply("Processing....")
    for n, anim in enumerate(animedb):
        await main_reply.edit(f"checking for updates of {anim['_id']} ({n+1}/{len(animedb)})")
        anime_name = anim['_id']
        if "---" in anime_name:
            anime = pahe.search_apahe(anime_name.split('---')[0])["data"][int(anime_name.split('---')[-1])]
            anime_name = anime_name.split('---')[0]
        else:
            anime = pahe.search_apahe(anime_name)["data"][0]
        
        num_of_eps = int(pahe.get_total_episodes(anime['session'], anim['lang']))
        if anim['eps_done'] < num_of_eps:
            eps_ids = pahe.mid_apahe(anime['session'], [anim['eps_done']+1, num_of_eps])
            eps_list = pahe.dl_apahe1(anime["session"], eps_ids)
            thumb = anime["poster"]
            thumb = await helper.DownLoadFile(thumb, file_name=f"{anime_name} thumb.png")
            name_format = anim['file_name_format']
            for k, v in eps_list.items():
                ep_num = k + anim['eps_done'] - 1
                await bot.send_message(event.chat_id, name_format.replace("UwU", str(ep_num+1)).replace("RES", "").replace("LANG", "").replace('.mkv', ''))
                counter = 0
                for i in reversed(v):
                    if counter == "3":
                        break
                    res = i[1]
                    lang = i[2]
                    if anim['lang'].lower() != lang.lower():
                        continue
                    counter += 1
                    dl_link = pahe.dl_apahe2(i[0])
                    dl_link = kwik_token.get_dl_link(dl_link)
                    file_name = name_format.replace("UwU", str(ep_num+1)).replace("RES", res).replace("LANG", lang)
                    # reply = await event.reply(f"Starting download {file_name}")
                    
                    file = await helper.DownLoadFile(dl_link, file_name=file_name)
                    res_file = await fast_upload(client = bot, file_location = file)       # , reply = reply)
                    await bot.send_message(event.chat_id, f"{file_name.replace('.mkv', '').replace('.mp4', '')}", file=res_file, force_document=True, thumb=thumb)
                    # await reply.delete()
                    os.remove(file)
                AutoAnimeDB.modify({"_id": anim['_id']}, {"eps_done": ep_num+1})
            os.remove(thumb)
    await event.reply("Updated successfully")

@bot.on(events.NewMessage(pattern="/add_anime"))
async def _(event):
    if event.raw_text == "/add_anime":
        await event.reply("/add_anime\nanime name\nfile name format\nsub/dub\n\n\n\nfile format example\nAnime Name - S1 UwU RES LANG.mkv\n UwU will be replaced by ep number.\nRES will be replaced by resolution\nLANG will be replaced by either sub/dub")
        return
    _, anime_name, file_name_format, lang = event.raw_text.split("\n")
    AutoAnimeDB.add({"_id": anime_name, "eps_done": 0, "file_name_format":file_name_format, "lang":lang})
    await event.reply("Anime added to watchlist")

@bot.on(events.NewMessage(pattern="/rm_anime"))
async def _(event):
    anime_name = event.raw_text.split("\n")[1]
    AutoAnimeDB.remove({"_id": anime_name})
    await event.reply("Anime removed from watchlist")

@bot.on(events.NewMessage(pattern="/show_watchlist"))
async def _(event):
    db = AutoAnimeDB.full()
    txt = ''
    for i in db:
        txt += f"{i['_id']}\nEps downloaded: {i['eps_done']}\n{i['file_name_format']}\n{i['lang']}\n\n\n"
    await event.reply(txt)
    


bot.start()

bot.run_until_disconnected()