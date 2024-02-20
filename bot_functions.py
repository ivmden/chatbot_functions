from datetime import date
import datetime
import subprocess
from subprocess import Popen, PIPE
import shlex
import os
from random import *
import psycopg2
import re
import pycurl
from io import BytesIO

#BOTNAME='devel'    # TODO FIX THIS.  NOT SUSTAINABLE FOR OTHER DEVELOPERS TO NEED TO UPDATE.  ADD A CONFIG FILE?  DATABASE CONFIG 'FILE'??
BOTNAME='torpedobot'

# TODO: ADD SOME DOCUMENTATION AROUND CALLING FUNCTIONS.
# TODO: OVERAUL SCHEMA FILE.
# TODO: UNIT TESTING CODE.
# TODO: REMOVE REFRENCES TO OLD SHELL VERSIONS.
# TODO: MATHBOT.....
# TODO: THERE ARE STILL A HANDFUL OF THINGS THAT RELY ON OLD SHELL FILES.

################################################################################
'''
This is the main code that runs when the .seen command is called.
'''
def lookup_seen(sender, roomid, inmsg, conn, cur):
  target = resolve_username(sender, roomid, inmsg, conn, cur)
  if target[0] == 0 or target[0] > 1:
    exec_user_error(sender, roomid, inmsg, conn, cur)
    return target[1]


  # look up the last recorded entry from the user

  # TODO: BREAK TIMEZONE OUT INTO THE ABOVE MENTIONED CONFIG FILE.
  dbstring="SET timezone = 'America/new_York';select payload, event_time from user_data where username=\'" + target[1] + "\' and room=\'" + roomid + "\' and kind=\'seen\';"
  cur.execute(dbstring)
  out = cur.fetchone()

  # the user might not be in this room, or may not have said anything.
  if str(out) == "None":
    return target[1] + " has not said anything in this room in my memory."
  else:
    return target[1] + " was last seen saying " + out[0] + " at " + str(out[1])

################################################################################

################################################################################
'''
Log most recent message from a user.  For .seen command.
'''
def exec_seen(sender, roomid, inmsg, conn, cur):
  dbstring="delete from user_data where username=\'" + sender + "\' and room=\'" + roomid + "\' and kind=\'seen\';\n"
  dbstring=dbstring + "insert into user_data (username, room, kind, payload) values (\'" + sender + "\', \'" + roomid + "\', \'seen\', \'" + str(inmsg) + "\');"
  cur.execute(dbstring)
  conn.commit()

################################################################################

################################################################################
'''
I know from all the shell scripting work that username might be passed incompletely.
I really dont want to repeat that code a lot.
  There are 3ish possible inputs:
    1) Exact and valid username:  @USER:matrix.org
          return what was given
    2) incomplete valid username: USER
          if it verifies with a match against the DB, return the full name
    3) invalid username:          (Everything else)
          return eol.  This can be checked for and used as an error string.
'''
''' future
      Want to add a nickname entry to the user_data table
      move step 3 from above comments to 4, make
      3) potential nickname.
        results = "select username from user_data where payload=\'" + target + "\';""
        if results.count() = 0:
          unknown
        elif results.count() = 1:
          exact match
        else:
          too many matches
   '''
def resolve_username(sender, roomid, inmsg, conn, cur):
  # need to remove the username that is being looked for.
  return_string = "I could not find that username."
  counted_names = 0
  inmsg_splt = inmsg.split()
  try:
    target = inmsg_splt[1].lower()
    dbstring="select distinct username from user_data where room=\'" + roomid + "\';"
    cur.execute(dbstring)
    room_users=cur.fetchall()
    for i in room_users:
      potential_match=re.search(target,i[0])
      if potential_match:
        counted_names += 1
        if counted_names > 1:
          return_string += "\n" + i[0]
        else:
          return_string = i[0]

  # at this point we have searched the DB for any matching EXACT username.  Now we can add nicknames if counted_names == 0
    if counted_names == 0:
      inmsg_splt.pop(0)
      strang=""
      for word in inmsg_splt:
        strang += word + " "
      # print(strang)
      #handle nicknames
      dbstring="select username from user_data where kind=\'nickname\' and lower(payload)=\'" + strang.lower().rstrip() + "\';"
      # print("resolve username" + dbstring)
      cur.execute(dbstring)
      if cur.rowcount == 0:
        counted_names = 0
        return_string = "I could not find that username or nickname."
      elif cur.rowcount == 1:
        counted_names = 1
        return_string = cur.fetchone()[0]
        dbstring="select distinct username from user_data where room=\'" + roomid + "\' and username=\'" + return_string + "\';"
        # print(dbstring)
        cur.execute(dbstring)
        if cur.rowcount == 0:
          counted_names = 0
          return_string = "I could not find that username or nickname."
      elif cur.rowcount > 1:
        counted_names = 2
        return_string = "I found WAYY too many matches:\n"
    if counted_names > 1:
      tmpstr = "I found too many matches:\n" + return_string
      return [counted_names, tmpstr]

  except IndexError:
    return_string="Need a username goofball."
  return [counted_names, return_string]

################################################################################

################################################################################
'''
Need a generic 'updata a counter function'
  gonna be more than the copy/pasta'd code from earlier.  but it will reduce the amount of copypasta
  only NEED the target and db stuff.
  from there, rely on being passed room, kind, payload and offset (+/-)
'''
def increment_counter(conn, cur, target, room = "", kind = "", payload = "", offset = 1):
  #-----------------------------------------------------------------------------
  # want to return the ending value
  final_counter = 0
  # Build a query string to see if they have any of this counter yet
  dbwhere=" where username=\'" + target + "\' "
  if room != "":
    dbwhere += "and room=\'" + room + "\' "
  if kind != "":
    dbwhere += "and kind=\'" + kind + "\' "
  if payload != "":
    dbwhere += "and payload=\'" + payload + "\' "
  dbwhere += ";\n"
  dbstring = "select count from user_data" + dbwhere
  # print(dbstring)
  cur.execute(dbstring)
  out = cur.fetchone()
  #-----------------------------------------------------------------------------
  # if they do not, set it to one.
  if str(out) == "None":
    dbstring = "insert into user_data (username, count"
    dbvalues = "(\'" + target + "\', " + str(offset)
    if room != "":
      dbstring += ", room"
      dbvalues +=", \'" + room + "\'"
    if kind != "":
      dbstring += ", kind"
      dbvalues +=", \'" + kind + "\'"
    if payload != "":
      dbstring += ", payload"
      dbvalues +=", \'" + payload + "\'"
    dbstring += ") values " + dbvalues + ");\n"
    final_counter = offset
  #-----------------------------------------------------------------------------
  else: # otherwise update and increment.
    dbstring="update user_data set count = count + " + str(offset) + dbwhere
    final_counter = int(out[0]) + offset
  # print(dbstring)
  cur.execute(dbstring)
  conn.commit()
  return final_counter

################################################################################

################################################################################
'''
For the lols of it, track when users make an error.
'''
def exec_user_error(sender, roomid, inmsg, conn, cur):
  increment_counter(conn, cur, sender, kind = "bad")

################################################################################

################################################################################
'''
Increment the users room specific lolol counter
'''
def track_lol(sender, roomid, inmsg, conn, cur):
  return increment_counter(conn, cur, sender, kind = "jank", payload = "lolol", room = roomid)

################################################################################

################################################################################
'''
return a nicely formatted lolol count summary
'''
def count_lol(sender, roomid, inmsg, conn, cur):
  dbstring="select count, username from user_data where room=\'" + roomid + "\' and kind=\'jank\' and payload=\'lolol\' order by username;\n"
  cur.execute(dbstring)
  all_lolcount=cur.fetchall()
  final=""
  for i in all_lolcount:
    final= final + i[1] + ' ' + str(i[0]) + "\n"
  return final

################################################################################

################################################################################
'''
generate some messages when a user sends a string in all caps.  Sometimes.
'''

# TODO: MIGRATE THIS TO A db FUNCTION?
def exec_yelling(sender, roomid, inmsg, conn, cur):
      randomness = randint(1,100)
      if randomness == 1:
        return "STOP YELLING!"
      elif randomness == 2:
        return "Don't make me pull this car over."
      elif randomness == 3:
        return "Don't talk to your mother that way."
      elif randomness == 4:
        return "Keep it down, people are sleeping."
      elif randomness == 5:
        return "What is with all the yelling?"

################################################################################

################################################################################
'''
Increment silent counters.
'''
def exec_silent(sender, roomid, counted, conn, cur):
  increment_counter(conn, cur, sender, kind = "silent", payload = counted, room = roomid)

################################################################################

################################################################################
'''
return a nicely formatted silent counter summary
'''
def exec_silent_counting(sender, roomid, inmsg, conn, cur):
  dbstring="select username, payload, count from user_data where room=\'" + roomid + "\' and kind=\'silent\' order by username"
  cur.execute(dbstring)
  all_silentcount=cur.fetchall()
  final=""
  for i in all_silentcount:
    final= final + i[0] + ' ' + i[1] + ' ' + str(i[2]) + "\n"
  return final

################################################################################

################################################################################
'''
Return a random organ.  For dicebot
'''
def dnd_lookup_util(cur, category):
  dbstring = "select count(*) from DND where category='" + category + "';"
  cur.execute(dbstring)
  out = cur.fetchone()

  randomness = randint(1,int(out[0]))

  dbstring = "select content from DND where category='" + category + "' and id=" + str(randomness) + ";"
  cur.execute(dbstring)
  out = cur.fetchone()

  return str(out[0])

################################################################################

################################################################################
'''
Return a random peer among users in the room, not the person rolling the dice.  For dicebot
'''
def dice_peer(sender, roomid, inmsg, conn, cur):
  dbstring="select distinct username from user_data where room=\'" + roomid + "\' and not username=\' " + sender + "\';"
  cur.execute(dbstring)
  all_users=cur.fetchall()
  randomness = randint(0,len(all_users)-1)
  return all_users[randomness][0]

################################################################################

################################################################################
'''
generate critical fail string.
'''
def dice_crit_fail(sender, roomid, inmsg, conn, cur):
  critness = randint(1,15)
  if critness == 1 :
    return "CRITICAL DETECTED\nYou have slipped in the heat of combat"
  elif critness == 2 :
    return "CRITICAL DETECTED\nYour feet are larger than you remember.  You trip over them."
  elif critness == 3 :
    return "CRITICAL DETECTED\nYour feet are larger than you remember.  You use one of your shoes as a canoe and go for a trip"
  elif critness == 4 :
    return "CRITICAL DETECTED\nYou have lost your bearing.  You wander off northsoutherly for a while"
  elif critness == 5 :
    return "CRITICAL DETECTED\nSomeone lubed the handle on your " + dnd_lookup_util(cur, "weapon") + ".  You drop it."
  elif critness == 6 :
    return "CRITICAL DETECTED\nSomeone replaced your " + dnd_lookup_util(cur, "weapon") + " with a stick of butter.  Butterfingers...."
  elif critness == 7 :
    return "CRITICAL DETECTED\nYou are suddenly convinced your " + dnd_lookup_util(cur, "weapon") + " is a " + dnd_lookup_util(cur, "animals") + ".  You drop it."
  elif critness == 8 :
    return "CRITICAL DETECTED\nYou are dumbfounded by your own ineptitude.  Things happen, but you dont understand"
  elif critness == 9 :
    return "CRITICAL DETECTED\nYou hit the " + dnd_lookup_util(cur, "enemies") + " really hard.  Some random fluid gets in your eye.  You are blind"
  elif critness == 10 :
    return "CRITICAL DETECTED\nYour " + dnd_lookup_util(cur, "weapon") + " breaks"
  elif critness == 11 :
    return "CRITICAL DETECTED\nYou miss and hit yourself in the " + dnd_lookup_util(cur, "organ")
  elif critness == 12 :
    return "CRITICAL DETECTED\nYou miss and hit " + dice_peer(sender, roomid, inmsg, conn, cur)
  elif critness == 13 :
    return "CRITICAL DETECTED\nYou criticaly hit yourself"
  elif critness == 14 :
    return "CRITICAL DETECTED\nYou criticaly hit " + dice_peer(sender, roomid, inmsg, conn, cur)
  elif critness == 15 :
    return "CRITICAL DETECTED\nYou strain your " + dnd_lookup_util(cur, "organ")

################################################################################

################################################################################
'''
Dicebot logic.  Handles processing r3d4, etc.  Also handles various modifiers
'''
def dicebot(sender, roomid, inmsg, conn, cur):
 # TODO: ADD MORE COMMENTS HERE
 # TODO: ADD DICEHARDCAP TO CONFIG FILE.
  total_dice=0
  grand_total=0
  critted=""
  results=""
  truncated=0
  DICEHARDCAP=100
  # step one, parse all dice rolls and bonuses out of inmsg
  inmsg_splt = inmsg.split()
  for rollcommand in inmsg_splt[1:]:
    dice_roll = re.search("d|D|inf|infinty|∞", str(rollcommand))
    bonus = re.search("^\+", str(rollcommand))
    negative = re.search("^-", str(rollcommand))
    DND = re.search("DND", str(rollcommand.lower()))  # TODO: MAKE LOWERCASE WORK HERE.
    if DND:
      dice_roll = False
    #-----------------------------------------------------------------------------
    # process normal dice rolls
    if dice_roll:
      splitted = rollcommand.replace("r",'').replace("d",' ').replace("D"," ").split()
      print(splitted)

      results += rollcommand + ": "
      # verify the number of dice is valid
      try:
        rolls=int(splitted[0])
        # verify the number of sides is valid
        try:
          sides=0
          if splitted[1] == "inf" or splitted[1] == "infinity" or splitted[1] == "∞":
#            print("Handle infiite dice here "+ str(rolls))
            sides = randint(1,1000000)
          else:
            sides=int(splitted[1])

          # handle some low value weird cases.  rolling 0 dice, rolling 0 sided dice, rolling 1 sided dice
          print("rolling " + str(rolls) + " dice with " + str(sides) + " sides each")
          if int(sides) == 0:
            results += "Goofball.  You rolled a 0\n"
          elif int(rolls) == 0:
            results += "blah blah blah.  You rolled a 0\n"
          elif int(sides) == 1:
            results += "yeah, howd you think that was gonna work.  You rolled a " + str(rolls) + "\n"
            grand_total += int(rolls)
            total_dice += int(rolls)
          # actually rolling dice
          else:
            # enforce limit on number of dice to roll
            if total_dice > DICEHARDCAP:
              results += "Please keep it less than " + str(DICEHARDCAP) + " dice\n"
            else:
              results += "[ "
              local_total = 0
              # iterate over the dice
              for x in range(0,int(rolls)):
                randomness = randint(1,int(sides))
                results += str(randomness) + " "
                grand_total += randomness
                local_total += randomness
                total_dice += 1
                # breaking out if hardcap exceeeded
                if total_dice > DICEHARDCAP:
                  truncated = 1
                  break
                #   generate critical fails on rolling a 1 on a d20
                if int(sides) == 20 and randomness == 1:
                  critted = dice_crit_fail(sender, roomid, inmsg, conn, cur)
              results += "] sums to " + str(local_total) + "\n"
              # final bit of hardcap enforcement
              if truncated == 1:
                results += "Dice rolling aborted.  " + str(DICEHARDCAP) + " dice limit\n"
        #handle invalid dice sides
        except ValueError:
          results+=str(splitted[1]) + " is not a number\n"
          exec_user_error(sender, roomid, inmsg, conn, cur)
        except IndexError:
          results+="You didnt give me enough numbers.\n"
          exec_user_error(sender, roomid, inmsg, conn, cur)
      # handle invalid dice qty
      except ValueError:
        results+=str(splitted[0]) + " is not a number\n"
        exec_user_error(sender, roomid, inmsg, conn, cur)

    #-----------------------------------------------------------------------------
    # process proficiency bonuses
    elif bonus:
      try:
        grand_total += int(rollcommand)
        results+= "Applied a proficiency bonus of " + rollcommand + "\n"
      except ValueError:
        results+= rollcommand + " is not a valid proficiency bonus\n"
        exec_user_error(sender, roomid, inmsg, conn, cur)

    #-----------------------------------------------------------------------------
    # process negative modifiers
    elif negative:
      try:
        grand_total += int(rollcommand)
        results+= "Applied a negative modifier of " + rollcommand + "\n"
      except ValueError:
        results+= rollcommand + " bonus is not a valid negative modifier\n"
        exec_user_error(sender, roomid, inmsg, conn, cur)

    #-----------------------------------------------------------------------------
    # process dnd character generation
    elif DND:
      results = ""
      for x in range(0,5):
        d = [randint(1,6),randint(1,6),randint(1,6),randint(1,6)]
        results += "4d6: [ " + str(d[0]) + " " + str(d[1]) + " "+ str(d[2]) + " "+ str(d[3]) + " ] "
        d = sorted(d)
        results += "drop lowest:" + str(d[0]) + " sums to " + str(d[1]+d[2]+d[3]) +"\n"
      return results
    #-----------------------------------------------------------------------------
    # handle bad input
    else:
      results += "Expecting something like 1d6.  Roll 1 dice with 6 sides\n"
      exec_user_error(sender, roomid, inmsg, conn, cur)

  results+="Your total is: " + str(grand_total) + "\n" + critted
  
  return results

################################################################################

################################################################################
'''
Calculates a users jank.
jank = sum(room.user.jank)  + sum(room.user.silentcounters)/10
ONLY returns the floating point number.
ASSUMES the target passed in has already been verified.
'''
def calculate_jank(sender, roomid, target, conn, cur):
  dbstring="select count from user_data where kind=\'jank\' and room=\'" + roomid + "\' and username=\'" + target + "\';"
  # print(dbstring)
  cur.execute(dbstring)
  jank_fields=cur.fetchall()
  total_cred = 0
  for i in jank_fields:
    total_cred += int(i[0])
  dbstring="select count from user_data where kind=\'silent\' and room=\'" + roomid + "\' and username=\'" + target + "\';"
  # print(dbstring)
  cur.execute(dbstring)
  jank_fields=cur.fetchall()
  silent_jank = 0
  for i in jank_fields:
    silent_jank += int(i[0])

  total_cred = float(total_cred) + float(silent_jank/10)
  return total_cred

################################################################################

################################################################################
'''
Processes out username, gets their calculated jank and prints a string.
'''
def userjank(sender, roomid, inmsg, conn, cur):
  target = resolve_username(sender, roomid, inmsg, conn, cur)
  if target[0] == 0 or target[0] > 1:
    exec_user_error(sender, roomid, inmsg, conn, cur)
    return target[1]

  jank = calculate_jank(sender, roomid, target[1], conn, cur)
  ran = randint(1,1000)
  if ran <= 5:
    return target[1] + " has a credit score of " + str(jank)
  elif ran <= 10:
    return target[1] + " to experian, $print_user has a jank score of " + str(jank)
  elif ran <= 20:
    return target[1] + " has " + str(jank) + " bank in the jank"
  elif ran <= 30:
    return target[1] + "'s jank is so janky (" + str(jank) + ")"
  elif ran <= 40:
    return target[1] + " is so janktacular (" + str(jank) + ")"
  elif ran <= 160:
    return target[1] + " has " + str(jank) + " jank in the bank"
  elif ran <= 280:
    return target[1] + " jank is worth " + str(jank)
  elif ran <= 400:
    return target[1] + " posesses " + str(jank) + " jank"
  elif ran <= 700:
    return target[1] + " has a jank of " + str(jank)
  elif ran <= 1000:
    return target[1] + " has " + str(jank) + " jank"

################################################################################

################################################################################
'''
quick helper function to help with sorting the jank list generated by topjank
'''
def jank_calc(data_value):
  return data_value[1]

################################################################################


################################################################################
'''
For all users in a room, calculate their jank.  Then sort high to low.  Then print top 5 (or all if -le 5)
'''
def top_jank(sender, roomid, inmsg, conn, cur):
  janks=[]
  dbstring="select distinct username from user_data where room=\'" + roomid + "\';"
  cur.execute(dbstring)
  room_users=cur.fetchall()
  for user in room_users:
    j=calculate_jank(sender, roomid, user[0], conn, cur)
    janks.append([user[0],j])
  standings=""
  janks.sort(key=jank_calc, reverse=True)
  for i in range(0,min([5,len(janks)])):
    standings += str(janks[i][0]) + " " + str(janks[i][1]) + "\n"
  return standings
################################################################################

################################################################################
'''
Gives 1 jank to target.  If sender has more than 1 jank.  and if target is valid.
'''
def pityjank(sender, roomid, inmsg, conn, cur):
  target = resolve_username(sender, roomid, inmsg, conn, cur)
  if target[0] == 0 or target[0] > 1:
    exec_user_error(sender, roomid, inmsg, conn, cur)
    return target[1]

  senders_jank=calculate_jank(sender, roomid, sender, conn, cur)

  if senders_jank < 1:
    return "you dont have enough jank to give some to "  + target[1]

  target_pity=increment_counter(conn, cur, target[1], kind = "jank", payload = "pity", room = roomid)
  sender_pity=increment_counter(conn, cur, sender, kind = "jank", payload = "pity", room = roomid, offset=-1)

  extrastrings=""
  if target[1] == "@torpedobot:matrix.org" or target[1] == "@development_env:matrix.org":
    extrastrings=reply_to_pityjank(sender, roomid, inmsg, conn, cur)


  return sender + " now has " + str(sender_pity) + " pityjank and\n" + target[1] + " now has " + str(target_pity) + " pityjank" + extrastrings

################################################################################

################################################################################
'''
Generate a list of users in this room who also have bugreporting priviliges
'''
def check_bug_priv(sender, roomid, inmsg, conn, cur):
  dbstring= "select distinct username from user_data where room=\'" + roomid + "\' intersect "
  dbstring+="select distinct username from user_data where kind=\'bugreporting\';"
  cur.execute(dbstring)
  room_users=cur.fetchall()
  final_list="The following users have bugreporting priviliges:\n"
  for user in room_users:
    final_list+=user[0] + "\n"
  return final_list

################################################################################

################################################################################
'''
Python version of the previous bash weatherbot
'''
def weatherbot(sender, roomid, inmsg, conn, cur):
  final_string=""
  weatherurl=""
  b_obj = BytesIO()
  crl = pycurl.Curl()
  try:
    location_split=inmsg.split()
    location=location_split[1]
  except Exception as e:
    location = ""
  if location == "":
    # 1) try looking up home in db.
    dbstring="select payload from user_data where username=\'" + sender + "\' and kind='home';"
    cur.execute(dbstring)
    out = cur.fetchone()
    if str(out) == "None":
      # 2) else random location
      location_tuple = random_weather(sender, roomid, inmsg, conn, cur)
      final_string = "You have not set a default location for weather.\n" + str(location_tuple[0])
      weatherurl='wttr.in/'+ location_tuple[1] + '?format=%l:+%C+%t%20Sunrise:+%D%20Sunset:+%s'
    else:
      # process known home
      weatherurl='wttr.in/'+ str(out[0]) + '?format=%l:+%C+%t%20Sunrise:+%D%20Sunset:+%s'

  elif location == "set":
    location=location_split[2]
    # 1) set the location in the db
    dbstring= "delete from user_data where username=\'" + sender + "\' and kind='home';"
    dbstring+="insert into user_data (username, kind, payload) values (\'" + sender + "\', \'home\', \'" + location + "\');"
    cur.execute(dbstring)
    conn.commit()

    weatherurl='wttr.in/'+ location + '?format=%l:+%C+%t%20Sunrise:+%D%20Sunset:+%s'
    # 2) lookup weather
  else:
    # return lookup for that location
    weatherurl='wttr.in/'+ location + '?format=%l:+%C+%t%20Sunrise:+%D%20Sunset:+%s'
  crl.setopt(crl.URL, weatherurl) #"')
  crl.setopt(crl.WRITEDATA, b_obj)
  crl.perform()
  crl.close()
  get_body = b_obj.getvalue()
  final_string += get_body.decode('utf8')
  return final_string
################################################################################

################################################################################
'''
Return a tuple of location name and zip code for a random city
'''
def random_weather(sender, roomid, inmsg, conn, cur):
  randomness = randint(1,9)
  if randomness == 1 :
     return ["Using Intercourse, PA ", "17529"]
  elif randomness == 2 :
     return ["Using Hazardville, CT ", "06082"]
  elif randomness == 3 :
     return ["Using Volcano, HI ", "96785"]
  elif randomness == 4 :
     return ["Using Friendship, ME ", "04547"]
  elif randomness == 5 :
     return ["Using Accident, MD ", "21520"]
  elif randomness == 6 :
     return ["Using Licking, MO ", "65542"]
  elif randomness == 7 :
     return ["Using Truth or Consequences, NM ", "87901"]
  elif randomness == 8 :
     return ["Using Flasher, ND ", "58535"]
  elif randomness == 9 :
     return ["Using American Fork, UT ", "84003"]

################################################################################

################################################################################
'''
Return a sum of usererror from the db.
might be able to expose users from other rooms.
'''
def bad_input(sender, roomid, inmsg, conn, cur):
  target = resolve_username(sender, roomid, inmsg, conn, cur)
  if target[0] == 0 or target[0] > 1:
    exec_user_error(sender, roomid, inmsg, conn, cur)
    return target[1]

  dbstring="select count from user_data where username=\'" + target + "\' and kind='bad';"
  cur.execute(dbstring)
  out = cur.fetchone()
  if str(out) == "None":
    return "user " + target[1] + " has a record of 0 bad commands sent"
  else:
    return "user " + target[1] + " has a record of " + str(out[0]) + " bad commands sent"

################################################################################

################################################################################
'''
a wrapper for incrementing jank.img counter.
'''
def increment_img(sender, roomid, inmsg, conn, cur):
  return increment_counter(conn, cur, sender, kind = "jank", payload = "img", room = roomid)

################################################################################

################################################################################
'''
a wrapper for incrementing jank.video counter.
'''
def increment_video(sender, roomid, inmsg, conn, cur):
  return increment_counter(conn, cur, sender, kind = "jank", payload = "video", room = roomid)

################################################################################

################################################################################
'''
a wrapper for incrementing jank.file counter.
'''
def increment_file(sender, roomid, inmsg, conn, cur):
  return increment_counter(conn, cur, sender, kind = "jank", payload = "file", room = roomid)

################################################################################

################################################################################
'''
a wrapper for incrementing jank.audio counter.
'''
def increment_audio(sender, roomid, inmsg, conn, cur):
  return increment_counter(conn, cur, sender, kind = "jank", payload = "audio", room = roomid)

################################################################################

################################################################################
'''
Help message as a function instead of a text file.
'''
def help_method():
  outstring = "1) You can ask me questions.\n"
  outstring += "2) I count the number of times people say certain words and upload files\n"
  outstring += "2.a) I have active counters for certain words\n"
  outstring += "2.b) I have silent counters for other words.\n"
  outstring += "3) Some hidden features\n"
  outstring += "4) Snarky user-specific comments on a semi-random basis\n"
  outstring += "5) dot_keyword actions: use .commands for more info\n"
  outstring += "6) upvote/downvote using .addpoint or .removepoint\n"
  return outstring

################################################################################

################################################################################
'''
commands method as a function instead of text file
'''
def commands_method():
  outstring = ".addpoint <STRING> upvotes an item\n"
  outstring += ".bugexample (Gives more indepth information on filing a bug)\n"
  outstring += ".bugpriv (Lists the users with bug reporting priviliges)\n"
  outstring += ".bugreport <STRING> (Logs the string to the bug queue, only if the user has bug reporting priviliges)\n"
  outstring += ".bugsummary (Lists the count of bugs in various states)\n"
  outstring += ".commands (print this help)\n"
  outstring += ".cred <USERNAME> (Displays user file upload credits)\n"
  outstring += ".dicebot <DICE> (Rolls dice.  Expects a '3d6' style format)\n"
  outstring += ".help (print a different help)\n"
  outstring += ".jankreport <USER> (gives a summary of the users jank)\n"
  outstring += ".lolcount (print all user counts for lolol)\n"
  outstring += ".lookup <NUMBER> (looks up the content of the given ticket)\n"
  outstring += ".mathbot <INT> <SYMBOL> <INT>  (Does the symbol operation on the two integers)\n"
  outstring += ".pityjank <USER> (Give the specified user one of your jank)\n"
  outstring += ".removepoint <STRING> downvotes an item\n"
  outstring += ".seen <USERNAME> (Displays the last message sent by the user in this room)\n"
  outstring += ".silent_counters (print all silent counters)\n"
  outstring += ".topjank (lists the 5 top jankiest users)\n"
  outstring += ".uptime (Displays how long the bot has been running)\n"
  outstring += ".version (Display version information)\n"
  outstring += ".weatherbot <ZIP CODE> (Displays weather for that zip)\n"
  outstring += ".weatherbot set <ZIP CODE> (sets your default zip)\n"
  return outstring

################################################################################

################################################################################
'''
Version as a function instead of a text file
'''
# TODO: MIGRATE TO DB LOOKUPS?
def version_method():
  outstring = "BotVersion: 3.1\n"
  outstring += "HelpVersion: 1.2.3\n"
  outstring += "QnAVersion: 2.0\n"
  outstring += "SnarkVersion: 1.2\n"
  return outstring

################################################################################

################################################################################
'''
Bug example as a function instead of a text file.
'''
def bug_example_method():
  outstring ="To send a bug report type\n"
  outstring+=".bugreport\n"
  outstring+="and follow it up with any string.  For example:\n"
  outstring+=".bugreport Does this question have an answer?\n"
  outstring+="It will get assigned a bug id and get logged in the bug queue.\n"
  outstring+="If you do not have bug reporting priviliges you will be told so.\n"
  outstring+="If you abuse your bug reporting priviliges, they will be removed.\n"
  return outstring

################################################################################

################################################################################
'''
For the moment, mathbot is gonna remain as a shell script.  Still would rather rebuild as a CPP executable.
'''
def mathbot_method(sender, roomid, inmsg, conn, cur):
  math = subprocess.check_output(shlex.split('./bin/math.sh ' + sender[1:] + ' ' + inmsg))
  math=str(math)[2:][:-1].rstrip()
  return math

################################################################################

################################################################################
'''
For the moment, bug tracking will remain in an csv, and tracked via shell script.
'''
def bugreport_method(sender, roomid, inmsg, conn, cur):
  bug = subprocess.check_output(shlex.split('./bin/bugreport.sh "' + inmsg + '" ' + sender[1:]))
  bug=str(bug)[2:][:-1].rstrip()
  return bug

################################################################################
'''
for the moment, bug summary reporting will remain a shell function
'''
def bug_summary_method():
  summary = subprocess.check_output(shlex.split('./bin/bug_summary.sh'))
  f = open('outfile.tmp')
  out = f.read()
  f.close()
  os.remove('outfile.tmp')
  return out

################################################################################

################################################################################
'''
for the moment, bug lookup reporting will remain a shell function
'''
def bug_lookup_method(sender, roomid, inmsg, conn, cur):
  summary = subprocess.check_output(shlex.split('./bin/lookup_bug.sh ' + sender[1:] + " " + str(inmsg)))
  f = open('outfile.tmp')
  out = f.read()
  f.close()
  os.remove('outfile.tmp')
  return out

################################################################################

################################################################################
'''
a wrapper for incrementing points.provided string counter.
'''
def upvote_method(sender, roomid, inmsg, conn, cur):
  target = inmsg.split(' ', 1)[1]
  final_counter = increment_counter(conn, cur, sender, kind = "points", payload = target, room = roomid)
  return target + " is now worth " + str(final_counter) + " in the eyes of " + sender

################################################################################

################################################################################
'''
a wrapper for decrementing points.provided string counter.
'''
def downvote_method(sender, roomid, inmsg, conn, cur):
  target = inmsg.split(' ', 1)[1]
  final_counter = increment_counter(conn, cur, sender, kind = "points", payload = target, room = roomid, offset = -1)
  return target + " is now worth " + str(final_counter) + " in the eyes of " + sender

################################################################################

################################################################################
'''
return a string nicely formatted for a users cred.  (file, img, video, audio uploads and pity.)
'''
def calculate_cred(sender, roomid, inmsg, conn, cur):
  target = resolve_username(sender, roomid, inmsg, conn, cur)
  if target[0] == 0 or target[0] > 1:
    exec_user_error(sender, roomid, inmsg, conn, cur)
    return target[1]

  dbstring="select payload, count from user_data where kind=\'jank\' and room=\'" + roomid + "\' and username=\'" + target[1] + "\' and not payload=\'lolol\' order by payload;"
  print(dbstring)
  cur.execute(dbstring)
  jank_fields=cur.fetchall()
  total_cred = "User " + target[1] + " has posted the following cred:\n"
  for i in jank_fields:
    if i[1] != 0:
      total_cred += i[0] + ": " + str(i[1]) + "\n"

  return total_cred

################################################################################

################################################################################
'''
This uptime function is a little messy.  It's not gonna be 100% because i'll forget to change the bot name at some point.
'''
def lookup_uptime(sender, roomid, inmsg, conn, cur):
  dbstring="select started from uptime where username=\'" + BOTNAME + "\' order by started desc;"
  cur.execute(dbstring)
  started=cur.fetchone()
  delta=datetime.datetime.now() - started[0]
  return "The bot has been up since " + str(started[0]) + " (" + str(delta) + ")"

################################################################################

################################################################################
'''
Here is our function to handle snarky comments.
'''
def generate_snark(sender, roomid, inmsg, conn, cur):
  dbstring="select content, rate from snark where kind = \'normal\' and username=\'" + sender + "\' or username=\'__all\';"
  cur.execute(dbstring)
  returning_snark = ""
  snark_options=cur.fetchall()
  for snark in snark_options:
    randomness = randint(1,snark[1])
    if randomness == 1:
      returning_snark += snark[0] + "\n"

  #calendar 'snark'
  today = date.today()
  dated = today.strftime("%m%d")

  dbstring="select content, rate from snark where kind = \'" + dated + "\' and username=\'holiday__\';"
  cur.execute(dbstring)
  snark_options=cur.fetchall()
  for snark in snark_options:
    randomness = randint(1,snark[1])
    if randomness == 1:
      returning_snark += snark[0] + "\n"

  return returning_snark
  #still need to implement supersnakrk

################################################################################


################################################################################
'''
A function to say funny things when the bot it pityjanked
  I want a BUNCH of replies
    I should probably store them in the database.
      this would let me have user specific replies
      i can also have some 'low credit' replies
      can also have SUPRE Rare replies
'''
def reply_to_pityjank(sender, roomid, inmsg, conn, cur):
  #ANYTHING I RETURN NEEDS TO START WITH A NEWLINE CHAR:
  result = "\n"
  do_a_generic="false"
  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # super rare encounter.
  randomness = randint(1,10000)
  if randomness == 1:
    increment_counter(conn, cur, sender, kind = "jank", payload = "pity", room = roomid)
    increment_counter(conn, cur, sender, kind = "jank", payload = "pity", room = roomid)
    increment_counter(conn, cur, sender, kind = "jank", payload = "pity", room = roomid)
    increment_counter(conn, cur, sender, kind = "jank", payload = "pity", room = roomid)
    increment_counter(conn, cur, sender, kind = "jank", payload = "pity", room = roomid)
    return "\nYour generosity does not go unseen.  You find 5 jank lying on the ground"


  # need to decide if i want to do a user specific:
  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  randomness = randint(1,100)
  if randomness == 1:
    # i'm gonna assume there is only one user specific string per user.
      # And by assume I mean take the first hit only.
    dbstring="select content from snark where username=\'" + sender + "\' and kind='pityjankd' limit 1;"
    cur.execute(dbstring)
    out = cur.fetchone()
    #need to handle the case where there is no user specific.
    if str(out) == "None":
      do_a_generic="true"
    else:
      result = "\n" + str(out[0])
      return result
  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  if randomness != 1 or do_a_generic == "true":
    dbstring="select rate from snark where kind='pityjankd' order by rate desc limit 1;"
    cur.execute(dbstring)
    out = cur.fetchone()
    randomness = randint(1,int(out[0]))
    dbstring="select content from snark where kind='pityjankd' and rate>=" + str(randomness) + " order by rate limit 1;"
    cur.execute(dbstring)
    out = cur.fetchone()
    outstring = str(out[0]).replace("@user", sender)
    return "\n" + outstring
  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

################################################################################


################################################################################
'''
given that we've been logging some .addpoint and .rmpoint for a while now, lets start looking for the strings.
'''
def upvote_searching_method(sender, roomid, inmsg, conn, cur):
  outstring = ""
  dbstring="select (username, payload, count) from user_data where kind='points' and room='" + roomid +"';"
  cur.execute(dbstring)
  upvotes = cur.fetchall() # technically also downvotes.
  for i in upvotes:
    results_splitted=i[0].split(",")
    found = re.search(results_splitted[1],inmsg)
    if found:
      outstring += results_splitted[1] + " is worth " + results_splitted[2].replace(")","") + " to " + results_splitted[0].replace("(","") + "\n"
  return outstring

################################################################################
