#!/bin/env python
#-*- coding: utf-8 -*-

import datetime
import subprocess
import time
from math import fabs

class Chance:
	def __init__(self):
		self.MatchesIds = []

	def getMatches(self):
		"""
		Get tenis matches from https://live.chance.cz
	
		@rtype:   list
		@return:  List of Matches.
		"""

		self.__parseMatches(self.__grep(self.__getHtml("https://live.chance.cz/"), "<div class=\"subbox on\">"))
	
	def __getHtml(self, url):
		"""
		Get generated html source.

		@type  url: string
		@param url: Url of page witch source code we want download.
		@rtype:   string
		@return:  Source html code. 
		"""

		command = subprocess.Popen(["./phantomjs", "chance.js", url], stdout=subprocess.PIPE)
		return command.communicate()[0]

	def __grep(self, data, grepString):
		"""
		Grep html source.
		
		@type  grepString: string
		@param grepString: Parameter for grep.
		@rtype:   string
		@return:  Greped data.
		"""
		command = subprocess.Popen(["grep", grepString], stdin=data, stdout=subprocess.PIPE)
		return command.communicate()[0]

	def getMatchInfo(self, id):
		"""
		Get match informations (score, names, who serve)

		@type  id: int
		@param id: Id of actual match.
		@rtype:   Match
		@return:  Match.
		"""

		matchUrl = "https://live.chance.cz/chance/ChanceLiveOddsAction.do?matchId="
		data = self.__getHtml(matchUrl + id)
		match = self.__parseMatchInfo(self.__grep(data, "<div class=\"stats_box\">"), id)
		match = self.__parseMatchBets(self.__grep(data, "<div id=\"main-bets\" class=\"mbox\">"), match)
		return match

	def __parseMatches(self, matchesHtml):
		"""
		Take source of page https://live.chance.cz/ and 
		get matches ids (Save them to self.MatchesIds).

		@type  matchesHtml: string
		@param matchesHtml: Html source of page https://live.chance.cz/.
		"""

		tags = matchesHtml.split('>')
		isTenis = False
		for tag in tags:
			if isTenis and "<span class=\"ico_sport" in tag:
				isTenis = False
				break

			if tag == "<span class=\"ico_sport s-5\"":
				isTenis = True
				continue

			if isTenis and "<li data-id=\"" in tag:
				self.MatchesIds.append(tag.replace("<li data-id=", "").replace("\"", ""))

	def __parseMatchBets(self, grepedMatchHtml, match)
		"""
		Take source of page and get bets info.

		@type  grepedMatchHtml: string
		@param grepedMatchHtml: Html source of page with detail.
		@type  match: Match
		@param match: Match.

		@rtype:   Match
		@return:  Match.
		"""
		tags = matchHtml.split('>')
		set = 0
		gem = 0
		nextIsExchange = False
		for tag in tags:
			if tag[15:] == ". setu</h3":
				set = (int)(tag[14])
				match.Player[0].Exchanges.append([])
				match.Player[1].Exchanges.append([])
				continue
			if set is not 0:
				if tag[1:] == ". gamu</strong":
					gem = (int)(tag[0])
					continue
				if gem is not 0:
					if tag == "<span class=\"kurz\"":
						nextIsExchange = True
						continue
					if nextIsExchange:
						match.Player[0].Exchanges[set - 1][gem - 1] = (float)(tag.replace("</span", ""))

	def __parseMatchInfo(self, grepedMatchHtml, id):
		"""
		Take source of page with detail of match and get match info
		(score, who play, ...)

		@type  grepedMatchHtml: string
		@param grepedMatchHtml: Html source of page with detail.
		@type  id: int
		@param id: Id of match.
		@rtype:   Match
		@return:  Match.
		"""

		match = Match()
		match.Id = id
		match.Players.append(Player())
		match.Players.append(Player())
		tags = matchHtml.split('>')
		nextHaveNotServe = False
		nextHaveServe = False
		nextIsScore = False
		num = 0
		for tag in tags:
			if tag == "<th class=\"ico_serv\"":
				nextHaveServe = True
				continue

			if tag == "<th":
				nextHaveNotServe = True
				continue

			if tag == "<td class=\"on\"":
				nextIsScore = True
				continue
			
			if tag == "<td":
				nextIsScore = True
				continue

			if nextIsScore and ".s" in tag:
				if "5" in tag:
					match.NumOfSets = 5
				nextIsScore = False
				continue

			if nextHaveNotServe and tag is not "</th":
				# save name
				tag = tag.replace("</th", "")
				if match.Players[0].Name == "":
					match.Players[0].Name = tag
				else:
					match.Players[1].Name = tag
				nextHaveNotServe = False
				continue

			if nextHaveServe:
				# save name
				tag = tag.replace("</th", "")
				if match.Players[0].Name == "":
					match.Players[0].Name = tag
					match.Players[0].Serve = True
				else:
					match.Players[1].Name = tag
					match.Players[1].Serve = True
				nextHaveServe = False
				continue

			if nextIsScore:
				# save gems
				tag = tag.replace("</td", "")
				num = num + 1

				if match.NumOfSets == 5:
					if num <= 5:
						match.Players[0].Sets.append(tag)
					else:
						match.Players[1].Sets.append(tag)
				elif match.NumOfSets == 3:
					if num <= 3:
						match.Players[0].Sets.append(tag)
					else:
						match.Players[1].Sets.append(tag)
				else:
					print "fatal error"
					exit(2)

				nextIsScore = False
				continue

		# count gems
		for i in [0,1]:
			num = 1
			for set in match.Players[i].Sets:
				if set.isdigit():
					match.Gems = match.Gems + (int)(set)
					match.ActualSet = num
				num = num + 1

		self.__setWhoWinSet(match)

		return match

	def __setWhoWinSet(self, match):
		"""
		Set Players won sets.

		@type  match: Match
                @param match: Match where we want make change.
		"""
		if match.ActualSet == 0:
			return False
		else:
			for i in [0, 1]:
				if (match.Players[i].Sets[match.ActualSet - 1] == "7" or 
					(match.Players[i].Sets[match.ActualSet - 1] == "6" and 
					(fabs((int)(match.Players[0].Sets[match.ActualSet - 1]) - (int)(match.Players[1].Sets[match.ActualSet - 1])) >= 2))):
					match.Players[i].WonSets = match.Players[i].WonSets + 1


	def checkIfMatchEnd(self, match):
		"""
		Check if match end. Look at players won sets.

		@type  match: Match
		@param match: Match which we want resolve.
		
		@rtype:   bool
		@return:  Return true if match end.
		"""
		if (match.NumOfSets == 3):
			if (match.Players[0].WonSets == 2 or match.Players[1].WonSets == 2):
				return True
		else:
			if (match.Players[0].WonSets == 3 or match.Players[1].WonSets == 3):
                                return True

	def CheckIfPlayerWinHisServe(self, match, prevMatch, g):
		"""
		Check if player won when he had serve.

		@type  match: Match
		@param match: Actual match which we want to compare.
		@type  prevMatch: Match
		@param prevMatch: Previous match which we want to compare.
		"""
		setNumber = match.ActualSet - 1

		if str(match.ActualSet) >= "2" and str(match.Players[0].Sets[setNumber]) == "0" and str(match.Players[1].Sets[setNumber]) == "0":
			setNumber = match.ActualSet - 2

		if prevMatch.Players[0].Serve:
			if (match.Players[0].Sets[setNumber]).isdigit() and (prevMatch.Players[0].Sets[setNumber]).isdigit():
				return ((int)(match.Players[0].Sets[setNumber]) - 1 == (int)(prevMatch.Players[0].Sets[setNumber]))
		elif prevMatch.Players[1].Serve:
			if (match.Players[1].Sets[setNumber]).isdigit() and (prevMatch.Players[1].Sets[setNumber]).isdigit():
				return ((int)(match.Players[1].Sets[setNumber]) - 1 == (int)(prevMatch.Players[1].Sets[setNumber]))
		return match

class Player:
	"""
	Represent tenis player. I implement only 2 player match. 
	If 4 player play, Players[0].Name contain both names
	"""

	def __init__(self):
		self.Name = ""
		self.Serve = False
		self.Sets = []
		self.WonSets = 0
		self.Exchanges = []

	def __str__(self):
		return self.Name + "\t" + str(int(self.Serve)) + "\t" + "_".join(map(str, self.Sets))

class Match:
	"""
	Represent one tenis game.
	"""

	def __init__(self):
		self.Id = ""
		self.Gems = 0
		self.ActualSet = 0
		self.NumOfSets = 3
		self.Players = []

	def __eq__(self, other):
		return (self.Id == other.Id)

	def __str__(self):
		return self.Id + "\t" + str(self.Gems) + "\t" + str(self.Players[0]) + "\t" + str(self.Players[1])

class Game:
	def __init__(self):
		self.Money = 1000.0
		self.Bet = 100.0
		self.Exchange = 1.50

if  __name__ == "__main__":
	ch = Chance()
	g = Game()
	activeMatches = []
	while True:
		#load new match
		if len(ch.MatchesIds) == 0:
			ch.getMatches()

		#foreach matches
		for id in ch.MatchesIds:
			#get match from chance.cz
			match = ch.getMatchInfo(id)

			# ask if match end
			if ch.checkIfMatchEnd(match) or match.Gems is 0:
				# if match is in activeMatches, remove it from active matches
				if match in activeMatches:
					activeMatches.remove(match)
				# delete match id from ch.MatchesIds
				ch.MatchesIds.remove(id)

				if match.Gems is not 0: 
					print match

			#if match not end
			else:
				# find match and ask if score was changed
				if match in activeMatches:
					for activeMatch in activeMatches:
						if activeMatch.Id == match.Id and activeMatch.Gems is not match.Gems:
							# print "1" if player win his serve, print "0" if not
							ifPlayerWin = ch.CheckIfPlayerWinHisServe(match, activeMatch, g)
							# update match info
							activeMatches.remove(activeMatch)
							activeMatches.append(match)

							if ifPlayerWin:
								g.Money = g.Money + (g.Bet * g.Exchange - g.Bet)
							else:
								g.Money = g.Money - g.Bet
							# print match info
							print "%s %s %s CZK" % (match, ifPlayerWin, g.Money)
				# if match not founded, add it to active matches and print
				else:
					activeMatches.append(match)
					print match
		# wait for end of gem
		time.sleep(60)
