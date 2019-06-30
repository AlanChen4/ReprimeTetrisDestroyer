import json
import requests
import time
import uuid

from datetime import datetime
from random import randint


class regDestroyer():
  '''bot made for winning every game on regprime tetris 2 play'''


  def __init__(self):
    self.session = requests.Session()

    # lets user choose configuration options
    print("[welcome] @Alan for http://regprime.com/Games/Tetris2Play")
    print("1) start a 2 player game \n2) join a 2 player game")
    self.game_mode = input("[choice]:")
    self.number_of_lines = input("[number of lines]:")
    if self.game_mode == "1":
      self.setupGame()
    else: self.joinGame()


  # used to join game
  def joinGame(self):
    game_code = input("game code:")
    join_url = "http://regprime.com/api/Tetris2PlayApi/{0}/JoinGame".format(game_code)
    join_payload = {}
    join_status = self.session.post(join_url, data=join_payload)
    if join_status.status_code > 200:
      self.game_key = json.loads(join_status.text)['Data']
      print("[success] game key:" + self.game_key)
      self.syncGames()
    else:
      print("unable to join game")


  # used to host game
  def setupGame(self):
    # sets up a new server for others to join
    setup_url = "http://regprime.com/api/Tetris2PlayApi/SetupGame"
    setup_payload = {}
    setup_status = self.session.post(setup_url, data=setup_payload)
    if setup_status.status_code > 200:
      self.setup_key = json.loads(setup_status.text)['Data']
      print("[success] setup properly with code: " + str(self.setup_key))
      self.waitForOpponent()
    else:
      print("could not generate setup code")


  def waitForOpponent(self):
    wait_url = "http://regprime.com/api/Tetris2PlayApi/{0}/WaitForOpponent".format(self.setup_key)
    wait_payload = {}
    wait_status = self.session.post(wait_url, data=wait_payload)
    wait_status = json.loads(wait_status.text)['IsSuccessful']
    while wait_status:
      print("waiting for opponent...")
      time.sleep(1)
      wait_status = self.session.post(wait_url, data=wait_payload)
      self.game_key = json.loads(wait_status.text)['Data']
      if self.game_key != None:
        print("[successful connection] game key:" + self.game_key)
        self.syncGames()
        break
      wait_status = json.loads(wait_status.text)['IsSuccessful']


  def syncGames(self):
    sync_url = "http://regprime.com/api/Tetris2PlayApi/{0}/sync".format(self.game_key)
    sync_payload = {}
    sync_status = self.session.post(sync_url, data=sync_payload)
    if sync_status.status_code > 200:
      print("[success] games have been synced")
      self.gameUpdate()
    else:
      print("error while syncing games")


  def gameUpdate(self):
    update_url = "http://regprime.com/api/Tetris2PlayApi/{0}/gameUpdate".format(self.game_key)
    while True:
      time.sleep(5)
      current_height = randint(1,7)
      syncId = str(uuid.uuid4())
      update_payload = {
        "PlayerId":         self.game_mode,
        "CurrentHeight":    current_height,
        "Total Lines":      "100",
        "AddonLines":       self.number_of_lines,
        "ClientSyncGuid":   syncId
      }
      update_status = self.session.post(update_url, data=update_payload)
      # updates user when post request has been made
      timestamp = str(datetime.now().strftime("%H:%M:%S.%f")[:-3])
      print("[{0}]{1}".format(timestamp, update_status.text))
      if json.loads(update_status.text)['Data']['WinningPlayer'] != 0:
        break
    print("[success] game has completed")


main = regDestroyer()
