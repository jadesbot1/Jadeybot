import datetime
import json
import re
import select
import socket
import urllib2
import login

channels = [
    'jadeymew'
]
username = login.username  
oauth = login.oauth


def ping():
    socks[0].send('PONG :pingis\n')
    print('PONG: Client > tmi.twitch.tv')


def sendmsg(chan, msg):
    socks[0].send('PRIVMSG ' + chan + ' :' + msg + '\n')
    print('[BOT] -> ' + chan + ': ' + msg + '\n')


def sendwhis(user, msg):
    socks[1].send('PRIVMSG #jtv :/w ' + user + ' ' + msg + '\n')
    print('[BOT] -> ' + user + ': ' + msg + '\n')


def getmsg(msg):
    if (re.findall('@(.*).tmi.twitch.tv PRIVMSG (.*) :(.*)', msg)):
        msg_edit = msg.split(':', 2)
        if (len(msg_edit) > 2):
            user = msg_edit[1].split('!', 1)[0]  # User
            message = msg_edit[2]  # Message
            channel = re.findall('PRIVMSG (.*)', msg_edit[1])  # Channel
            privmsg = re.findall('@(.*).tmi.twitch.tv PRIVMSG (.*) :(.*)', msg)
            privmsg = [x for xs in privmsg for x in xs]
            datelog = datetime.datetime.now()
            if (len(privmsg) > 0):
                print(
                    '[' + str(datelog.hour) + ':' + str(datelog.minute) + ':' + str(
                        datelog.second) + '] ' + user + ' @ ' +
                    channel[0][:-1] + ': ' + message)

    if (re.findall('@(.*).tmi.twitch.tv WHISPER (.*) :(.*)', msg)):
        whisper = re.findall('@(.*).tmi.twitch.tv WHISPER (.*) :(.*)', msg)
        whisper = [x for xs in whisper for x in xs]

        if (len(whisper) > 0):
            print('*WHISPER* ' + whisper[0] + ': ' + whisper[2])


def getviews():
    channelx = "jadeymew"
    f = urllib2.urlopen("https://tmi.twitch.tv/group/user/%s/chatters" % (channelx,))
    data = json.loads(f.read().decode("utf-8"))
    views = data["chatters"]["viewers"]
    sendmsg(channel, 'Current: ' + ', '.join(views))


def test():
    channelx = "jadeymew"
    f = urllib2.urlopen("https://tmi.twitch.tv/group/user/%s/chatters" % (channelx,))
    data = json.loads(f.read().decode("utf-8"))
    views = data["chatters"]["viewers"]
    sendwhis(user, ', '.join(views))


def joinpatriarchy():
    with open("Viewers", 'a') as f:
        f.writelines(user + "\n")
    f.close()


socks = [socket.socket(), socket.socket()]
socks[0].connect(('irc.twitch.tv', 6667))
socks[0].send('PASS ' + oauth + '\n')
socks[0].send('NICK ' + username + '\n')

for val in channels:
    socks[0].send('JOIN #' + val + '\n')

print('Connected to irc.twitch.tv on port 6667')
print('USER: ' + username)
print('OAUTH: oauth:' + '*' * 30)
print('\n')

temp = 0
while True:
    (sread, swrite, sexc) = select.select(socks, socks, [], 120)
    for sock in sread:
        msg = sock.recv(2048)
        if (msg == ''):
            temp + 1
            if (temp > 5):
                print('Connection might have been terminated')

        msg = msg.strip('\n\r')

        getmsg(msg)

        check = re.findall('@(.*).tmi.twitch.tv PRIVMSG (.*) :(.*)', msg)
        if (len(check) > 0):
            msg_edit = msg.split(':', 2)
            if (len(msg_edit) > 2):
                user = msg_edit[1].split('!', 1)[0]  # User
                message = msg_edit[2]  # Message
                channel = msg_edit[1].split(' ', 2)[2][:-1]  # Channel

                msg_split = str.split(message)

            if (msg_split[0] == '!Viewers'):
                getviews()

            if (msg_split[0] == '!feetforpremium'):
                sendmsg(channel,
                        'Well ' + user + ', Have I got an offer for you... For the price of only 1 spotify premium subscription can you get 1 picture of Jadeymews heels!')

            if user not in open('Viewers').read():
                sendmsg(channel,
                        'Hi ' + user + ', Welcome to the stream!')
                joinpatriarchy()

        check = re.findall('@(.*).tmi.twitch.tv WHISPER (.*) :(.*)', msg)
        if (len(check) > 0):
            msg_edit = msg.split(':', 2)
            if (len(msg) > 2):
                user = msg_edit[1].split('!', 1)[0]  # User
                message = msg_edit[2]  # Message
                channel = msg_edit[1].split(' ', 2)[2][:-1]  # Channel

                whis_split = str.split(message)

        if msg.find('PING :') != -1:
            print('PING: tmi.twitch.tv > Client')
            ping()
