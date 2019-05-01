# coding: utf-8
# remade by cnsr based on livechan API and anna bot code
# added telegram integration
# bot starts receiving incoming data only after sending any outcoming message
# kinda works but not really

# imports
from time import sleep
from api import *
import os
import telebot
import re
import sys
import random
import config
from urllib2 import urlopen
import hbot
import requests
import pyowm
import urllib
from bs4 import BeautifulSoup, Comment
from randomcat import cat as rkot
from imgur import cat as rkit
from twitter import kat as rkat
import weather2 as wttr
from crypto import crypto, money, detailed
from htranslate import translate as ht
from tts import tts
from switcher import switch, switchback
from pydick import meaning
from PIL import Image
import pickle
import emoji_flags
members = pickle.load(open('members'))
try:
    ids = pickle.load(open('ids'))
except:
    ids = {}
tbot = telebot.TeleBot(config.token)
nsfw = False

tripmap = {}
for l in open('/home/ph/livechan-js/public/js/chat.js'):
    if l.startswith('flags_hover_strings'):
        tripmap[l.split('"')[1]] = l.split('"')[3]


# loads region codes
regioncodes = json.load(open('regioncodes.json'))

# if you don't input channel to connect to
if len(sys.argv) < 2:
    print("Usage: python bot.py [channel]")
    exit()
# if you did it just werks
channel = sys.argv[1]

# if nswf doesnt send the images
try:
    if sys.argv[2] == 'nsfw':
        nsfw = True
        print('NSFW is on!')
except IndexError:
    print('NSFW is off!')


# writes image on disk so it could be read by api later
def send_image(url):
    url = url.replace('/home/ph/livechan-js/public/',
                      'https://kotchan.org/')
    f = open('out.jpg', 'wb')
    f.write(urllib2.urlopen(url).read())
    f.close()


def send_file(url, extension):
    url = url.replace('/home/ph/livechan-js/public/',
                      'https://kotchan.org/')
    f = open('out' + extension, 'wb')
    f.write(urllib2.urlopen(url).read())
    f.close()


base_url = 'http://www.worldtimeserver.com/current_time_in_'


class Opener(urllib.FancyURLopener):
    version = 'App/1.7'


def process_chat(*args):
    # uncomment for debug:
    # print(args)
    try:
        # get vars from args
        ident = args[0]["identifier"]
        message = args[0]["body"]
        name = args[0]["name"]
        count = str(args[0]["count"])
        convo = args[0]["convo"]
        country_name = args[0]["country_name"]
        country = args[0]["country"]
        trip = args[0].get("trip", '')
        # checks if file exists an gets the extension of it
        if "image" in args[0].keys():
            extension = os.path.splitext(args[0]["image"])[-1].lower()
        else:
            extension = ''

        # scrapes and returns a random cat image/gif from random.cat
        if re.match('^[.](kit|whale)$', message):
            msg = '>>' + count
            f = random.choice([rkot, rkit, rkot, rkat])()
            post_chat(msg, channel, name=config.name, trip=config.Trip, convo=convo, file=f)

        # returns one of many 8ball messages
        if re.match('^[.]8ball', message):
            random.shuffle(hbot.ball)
            mesg = random.choice(hbot.ball)
            post_chat('>>' + count + '\n' + mesg, channel, name=config.name, trip=config.Trip, convo=convo, file='')

        # matches cryptocurrencies, returns their data
        if re.match('^[#][a-zA-Z]+$', message):
            msg = detailed(message[1:])
            if msg:
                post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip, convo=convo, file='')

        # matches crypto but just returns price data
        if re.match('^[$][a-zA-Z]+$', message):
            msg = crypto(message[1:])
            if msg:
                post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip, convo=convo, file='')

        # returns punto switcher-like string if someone fucked up and typed in russian
        sreq = re.compile('\.(sw|switch) ([\s\S]+)').match(message)
        if sreq:
            msg = switch(sreq.group(2))
            if msg:
                post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip, convo=convo, file='')

        # same but from english
        ssreq = re.compile('\.(bs|bswitch) ([\s\S]+)').match(message)
        if ssreq:
            msg = switchback(ssreq.group(2))
            if msg:
                post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip, convo=convo, file='')


        # in case it fucks up and sends empty message 
        help_msg = 'no help message defined'

        # money getter
        mreq = re.compile('\.(m|money) (.+)').match(message)
        if mreq:
            try:
                m = mreq.group(2).upper().split(' ')
                if not m[0].isnumeric():
                    m = [1] + m
                msg = money(m)
                if msg:
                    post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip, convo=convo, file='')
            except Exception as e:
                print(e)


        meanreq = re.compile('\.(meaning|dict|d) (\D+)').match(message)
        if meanreq:
            msg = meaning(meanreq.group(2))
            post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip, convo=convo, file='')


        # gets weather, sometimes off
        # could be cleaned up but i won't bother right now
        wreq = re.compile('\@(weather|w)( (.+))?').match(message)
        if wreq:
            try:
                w = wreq.group(2)
                if not w:
                    w = regioncodes[country]
                if re.match('us', country[:2].lower()):
                    wttr.weather(w, murrica=False)
                else:
                    wttr.weather(w)
                msg = 'Weather in ' + w
                post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip,
                      convo=convo, file='weather.png')
            except Exception as e:
                print(str(e))

        # translates text into english
        treq = re.compile('(\.t )([\s\S]+)').match(message)
        if treq:
            try:
                msg = ht(treq.group(2))
                post_chat('>>' + count + '\n' + msg, channel, name=config.name, trip=config.Trip, convo=convo, file='')
            except Exception as e:
                print(str(e))

        ttsreq = re.compile('([.]tts )([\s\S]+)').match(message)
        if ttsreq:
            try:
                tts(ttsreq.group(2))
                post_chat('>>' + count, channel, name=config.name, trip=config.Trip, convo=convo, file='tts.ogg')
            except Exception as e:
                print(str(e))



        # checks messages for bot commands
        for (k, v) in hbot.answers.iteritems():
            if re.match(k, message):
                help_msg = hbot.answers[k]
                out_msg = '>>' + count + '\n' + help_msg
                post_chat(out_msg, channel, name=config.name,
                        trip=config.Trip,convo=convo, file='')

        @tbot.message_handler(commands=['setname', 'seticon'])
        def handle_set(message):
            cmd, val = message.text.split(None, 1)
            id = message.from_user.id
            oldval = members.get(id, [message.from_user.first_name, 'bug'])
            if cmd == '/setname':
                oldval[0] = val
            elif cmd == '/seticon':
                oldval[1] = val
            members[id] = oldval
            pickle.dump(members, open('members', 'w'))

        # handles text messages only, text + photo will only be handled as photo by next handler
	#telegram area, comment out
        @tbot.message_handler(func=lambda incM: True)
        def handle_text(incM):
            id = incM.from_user.id
            text = incM.text
            if incM.reply_to_message:
                origid = (incM.reply_to_message.caption or incM.reply_to_message.text).split()[0]
                text = '>>%s\n%s' % (origid, text)
            name, trip = members.get(id, [incM.from_user.first_name, 'bug'])
            post_chat(text, channel, name=name, trip=trip,
                      convo="General", file='')
            requests.get('https://api.telegram.org/bot{0}/deletemessage?message_id={1}&chat_id={2}'.format(config.token, incM.message_id, config.user_id))

        @tbot.message_handler(content_types=['sticker'])
        def handle_sticker(message):
            f = tbot.download_file(tbot.get_file(message.sticker.file_id).file_path)
            open('sticker.webp', 'w').write(f)
            f = Image.open('sticker.webp')
            f.save('sticker.jpg', 'JPEG')

            id = message.from_user.id
            name, trip = members.get(id, [message.from_user.first_name, 'bug'])

            post_chat('', channel, name=name,
                      trip=trip, convo='General', file='sticker.jpg') 
            requests.get('https://api.telegram.org/bot{0}/deletemessage?message_id={1}&chat_id={2}'.format(config.token, message.message_id, config.user_id))




        # only handles photos, doesnt work with text
        @tbot.message_handler(content_types=['photo', 'text'])
        def handle_image(message):
            message_id = message.message_id
            id = message.from_user.id
            name, trip = members.get(id, [message.from_user.first_name, 'bug'])
            file_id = message.photo[-1].file_id
            imageIn = tbot.get_file(file_id)
            image_file = requests.get('https://api.telegram.org/file/bot' + config.token + '/' + imageIn.file_path)
            with open('in.jpg', 'wb') as f:
                f.write(image_file.content)
            post_chat(message.caption or '', channel, name=name,
                      trip=trip, convo='General', file='in.jpg') 
            requests.get('https://api.telegram.org/bot{0}/deletemessage?message_id={1}&chat_id={2}'.format(config.token, message.message_id, config.user_id))

        @tbot.message_handler(content_types=['video', 'video_note'])
        def handle_image(message):
            message_id = message.message_id
            id = message.from_user.id
            name, trip = members.get(id, [message.from_user.first_name, 'bug'])
            if message.video_note:
                file_id = message.video_note.file_id
            else:
                file_id = message.video.file_id
            imageIn = tbot.get_file(file_id)
            image_file = requests.get('https://api.telegram.org/file/bot' + config.token + '/' + imageIn.file_path)
            with open('in.mp4', 'wb') as f:
                f.write(image_file.content)
            post_chat(message.caption or '', channel, name=name,
                      trip=trip, convo='General', file='in.mp4') 
            requests.get('https://api.telegram.org/bot{0}/deletemessage?message_id={1}&chat_id={2}'.format(config.token, message.message_id, config.user_id))

        # only sends posts from 'General' conversation
        if convo == "General" and not name.endswith('_'):
            if "image" in args[0].keys():
                out_image = args[0]["image"]
                if args[0]["image_filename"].startswith('anna'):
                    out_image = ''
            else:
                out_image = ''

            # msg = str(count) + '| ' + name + ' | ' + tripmap.get(trip, '') + ' | '  + country + " " + regioncodes.get(country, '') + ":\n" + message
            country2 = emoji_flags.get_flag(country.split('-')[0])
            if '-' in country:
                country2 = '%s-%s' % (country2, country.split('-')[1])
            msg = '%s %s %s %s:\n%s' % (count, name, tripmap.get(trip, ''), country2, message)

            # this doesnt work smh
            try:
                if extension != '.webm':
                    reply_to_message_id = ids.get(message.startswith('>>') and message.lstrip('>').split()[0])
                    if out_image and extension and extension not in ['.webm', '.gif', '.ogg', '.mp3', '.mp4']:
                        send_image(out_image)
                        newmsg = tbot.send_photo(config.user_id, open('out.jpg', 'rb'), caption=msg, reply_to_message_id=reply_to_message_id)
                    else:
                        newmsg = tbot.send_message(config.user_id, msg, reply_to_message_id=reply_to_message_id)#, parse_mode="Markdown")
                    ids[count] = newmsg.message_id
                    pickle.dump(ids, open('ids', 'w'))
                for st in re.findall(r'\[st\]([\w\d\-\.]+)\[\/st\]', msg):
                    tbot.send_photo(config.user_id, open('/home/ph/livechan-js/public/images/stickers/%s.png' % st))

                # will only send images if they exist and nsfw is off
                if out_image != '' and not nsfw and extension != '':
                    #if extension not in ['.webm', '.gif', '.ogg', '.mp3', '.mp4']:
                    #    send_image(out_image)
                    #    img = open('out.jpg', 'rb')
                    #    tbot.send_photo(config.user_id, img, caption=msg)
                    #    img.close()
                    if extension == '.ogg':
                        send_file(out_image, extension)
                        ogg = open('out.ogg', 'rb')
                        tbot.send_voice(config.user_id, ogg)
                        ogg.close()
                    if extension == '.gif':
                        send_file(out_image, extension)
                        gif = open('out.gif', 'rb')
                        tbot.send_document(config.user_id, gif)
                        gif.close()
                    if extension == '.mp4':
                        send_file(out_image, extension)
                        video = open('out.mp4', 'rb')
                        tbot.send_video(config.user_id, video)
                        video.close()
                    if extension == '.webm':
                        url = args[0]['image'].replace('/home/ph/livechan-js/public/', 'https://kotchan.org/')
                        msg += '\n' + url
                        tbot.send_message(config.user_id, msg)


            except Exception as e:
                ree = '----------\n' + str(e) + '\n-----------'
                tbot.send_message(config.user_id, ree)
    except Exception as e2:
        print('Exception e2: ' + str(e2))
        print(args[0]) 

# i guess this is better to have than not to?
while True:
    try:
        login(callback=process_chat)
        join_chat(channel)
        print('Joined chat')
        # init msg to make bot work
        # it doesnt smh lel
        tbot.send_message(config.user_id, 'Joined chat.')
        os.system('/home/ph/anna/say')
    except Exception as e:
        print("Connection failed. Error message:")
        print(e)
        pass
    else:
        break


# makes bot work and tbot polls endlessly(at least while no errors occur)
# and they do a lot
while 1:
    try:
        sleep(3)
        tbot.polling(none_stop=True)
    except:
        pass

