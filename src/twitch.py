import re, socket, sys
import messages, config
from imp import reload

HOST = config.HOST
PORT = config.PORT
CHAN = config.CHAN
NICK = config.NICK
PASS = config.PASS


"""
IRC Helper Functions
"""

def send_pong(msg):
  con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))

def send_message(chan, msg):
  con.send(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))

def send_nick(nick):
  con.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))

def send_pass(password):
  con.send(bytes('PASS %s\r\n' % password, 'UTF-8'))

def join_channel(chan):
  con.send(bytes('JOIN %s\r\n' % chan, 'UTF-8'))

def part_channel(chan):
  con.send(bytes('PART %s\r\n' % chan, 'UTF-8'))

def get_sender(msg):
  result = ""
  for char in msg:
    if char == "!":
      break
    if char != ":":
      result += char
  return result

def get_message(msg):
  result = ""
  i = 3
  length = len(msg)
  while i < length:
    result += msg[i] + " "
    i += 1
  result = result.lstrip(':')
  return result


"""
Moderator Commands
"""

def mod_sleep():
  send_message(CHAN, '/me Kuma-chan is going to sleep!')
  sys.exit()

def mod_kuma():
  send_message(CHAN, '/me Kuma~!')

mod_commands = {
  '!sleep':   mod_sleep,
  '!kuma':    mod_kuma
}


"""
User Commands
"""

def command_run():
  reload(messages)
  send_message(CHAN, '/me ' + messages.RUN)

def command_naka():
  send_message(CHAN, '/me Clank! Clank! Clank!')

commands = {
  '!run':     command_run,
  '!naka':    command_naka
}


"""
Message parsers
"""

def parse_message_mod(msg):
  if len(msg) >= 1:
    msg = msg.split(' ')
    del(msg[-1])
    if len(msg) == 1:
      try:
        if msg[0] in mod_commands:
          mod_commands[msg[0]]()
      except:
        pass
    elif len(msg) >= 2:
      try:
        do = msg[0]
        if len(msg) == 2:
          things = msg[1]
        else:
          del(msg[0])
          things = msg
        if msg[0] in mod_commands:
          mod_commands[do](things)
      except:
        pass

def parse_message(msg):
  if len(msg) >= 1:
    msg = msg.split(' ')
    del(msg[-1])
    if len(msg) == 1:
      try:
        if msg[0] in commands:
          commands[msg[0]]()
      except:
        pass
    elif len(msg) >= 2:
      try:
        do = msg[0]
        if len(msg) == 2:
          things = msg[1]
        else:
          del(msg[0])
          things = msg
        if msg[0] in commands:
          commands[do](things)
      except:
        pass


"""
IRC Server Connection
"""

con = socket.socket()

print("Connecting...")
con.connect((HOST, PORT))
print("Connected!")

send_pass(PASS)
send_nick(NICK)
print("User authenticated!")
join_channel(CHAN)
print("Joined channel!")

data = ""

while True:
  try:
    data = data+con.recv(1024).decode('UTF-8')
    data_split = re.split(r"[~\r\n]+", data)
    data = data_split.pop()

    for line in data_split:
      line = str.rstrip(line)
      line = str.split(line)

      if len(line) >= 1:
        if line[0] == 'PING':
          send_pong(line[1])

        if line[1] == 'PRIVMSG':
          sender = get_sender(line[0])
          message = get_message(line)

          if sender in config.MODS:
            parse_message_mod(message)
            parse_message(message)
          else:
            parse_message(message)

  except socket.error:
    print("Socket died")

  except socket.timeout:
    print("Socket timeout")