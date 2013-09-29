Chance
======

Get actual sport score from https://live.chance.cz

Actual it can download only live tenis matches.


USING
======

You must have instaled phantomjs (http://phantomjs.org/)

ch = Chance()

ch.getMatches()


for id in ch.MatchesIds:
  ch.getMatchInfo(id)
