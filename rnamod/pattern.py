import re

class Pattern:
   def __init__(self, pattern):
      if not re.fullmatch(r'[atcgATCG\.]+', pattern):
         raise AttributeError('Invalid pattern')

      self.pattern = pattern
      self.match_positions = []

      for match in re.finditer(r'[ATCG]', pattern):
         self.match_positions.append(match.start(0))

   def finditer(self, sequence):
      for match_sequence in re.finditer(self.pattern, sequence):
         for match_position in self.match_positions:
            yield match_sequence.start(0)+match_position

