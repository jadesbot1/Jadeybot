import datetime
import json
import re
import select
import socket
import urllib2
import login

CHANNEL_NAME = "jadeymew"
BLOCKED_NAMES = ['jadeymewbot', 'faegwent']

channels = [
    'jadeymew'
]
username = login.username
oauth = login.oauth

class PrivMsg:
    def __init__(self, msg):
        msg_edit = msg.split(':', 2)
        if (len(msg_edit) > 2):
            self.user = msg_edit[1].split('!', 1)[0]
            self.message = msg_edit[2]
            self.channel = msg_edit[1].split(' ', 2)[2][:-1]

    def command(self):
        return str.split(self.message)[0]

    def subject(self):
        return str.split(self.message)[1].lower()

    def channel_name(self):
        return self.channel[1:]

    def handle(self):
        if (self.command() == '!viewers' and authorise(self.user, self.channel)):
            self.getviews()
        elif(self.command() == '!auth' and authorise(self.user, self.channel)):
            promote(self.subject(), self.channel)
        elif(self.command() == '!deauth' and authorise(self.user, self.channel)):
            demote(self.subject(), self.channel)
        elif(self.command() == '!tiddies' and authorise(self.user, self.channel)):
            sendmsg(self.channel, "( . Y . )")
        elif(self.command() == '!tacos'):
            sendmsg(self.channel, "Taco time!")
        elif(self.command() == '!feetforpremium'):
            sendmsg(self.channel,
                    'Well ' + self.user + ', Have I got an offer for you... For the price of only 1 spotify premium subscription can you get 1 picture of Jadeymews heels!')
        if self.user not in open('Viewers').read():
            sendmsg(self.channel,
                    'Hi ' + self.user + ', Welcome to the stream!')
            joinpatriarchy()

    def getviews(self):
        url = "https://tmi.twitch.tv/group/user/%s/chatters" % (self.channel_name(),)
        f = urllib2.urlopen(url)
        data = json.loads(f.read().decode("utf-8"))
        views = self.parse_views(data)
        sendmsg(self.channel, 'Current: ' + ', '.join(views))

    def parse_views(self, data):
        views_with_bot = data["chatters"]["viewers"]
        views = list(filter(lambda name: name not in BLOCKED_NAMES, views_with_bot))
        return views
        

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
    channelx = CHANNEL_NAME
    f = urllib2.urlopen("https://tmi.twitch.tv/group/user/%s/chatters" % (channelx,))
    data = json.loads(f.read().decode("utf-8"))
    views = parse_views(data)
    sendmsg(channel, 'Current: ' + ', '.join(views))


def parse_views(data):
    views_with_bot = data["chatters"]["viewers"]
    views = list(filter(lambda name: name not in BLOCKED_NAMES, views_with_bot))
    return views

def joinpatriarchy():
    with open("Viewers", 'a') as f:
        f.writelines(user + "\n")
    f.close()

def authorise(user, channel):
    if user in open('AUTHORISED_USERS').read():
        return True
    else:
        sendmsg(channel, 'Unauthorised command by ' + user)
        return False

def promote(user, channel):
    if user not in open('AUTHORISED_USERS').read():
        with open("AUTHORISED_USERS", 'a') as f:
            f.writelines(user + "\n")
        sendmsg(channel, 'Promoted user ' + user)
    else:
        sendmsg(channel, 'User ' + user + ' is already promoted')

def demote(user, channel):
    if user == 'jadeymew':
        sendmsg(channel, "Hey hey, not Mira Jay!")
        return
    
    authorised_users = open('AUTHORISED_USERS').read()
    if user in authorised_users:
        new_users = re.sub(user + '\n', '', authorised_users)
        with open("AUTHORISED_USERS", 'r+') as f:
            f.seek(0)
            f.write(new_users)
            f.truncate()
        sendmsg(channel, 'Demoted user ' + user)
    else:
        sendmsg(channel, 'User ' + user + ' is not promoted')


def handle_privmsg(msg):
    privmsg = PrivMsg(msg)
    privmsg.handle()

socks = [socket.socket(), socket.socket()]
socks[0].connect(('irc.twitch.tv', 6667))
socks[0].send('PASS ' + oauth + '\n')
socks[0].send('NICK ' + username + '\n')

for val in channels:
    socks[0].send('JOIN #' + val + '\n')
    socks[0].send('CAP REQ :twitch.tv/membership\n')

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
            handle_privmsg(msg)

            

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
