import re

COLORS = [
  '197,225,165',
  '206,147,216',
  '244,143,177',
  '179,157,219',
  '255,224,130',
  '230,238,156',
  '159,168,218',
  '128,222,234',
  '129,212,250',
  '165,214,167',
  '255,245,157',
  '255,171,145',
  '128,203,196',
  '238,238,238',
  '255,204,128',
  '176,190,197',
]

class Pattern:

   last_color_index = -1

   @classmethod
   def get_next_color(self):
      self.last_color_index = (self.last_color_index + 1) % len(COLORS)
      return COLORS[self.last_color_index]

   def __init__(self, pattern):
      if not re.fullmatch(r'[atcgATCG\.]+', pattern):
         raise AttributeError('Invalid pattern')

      self.pattern = pattern
      self.match_positions = []
      self.color = self.get_next_color()

      for match in re.finditer(r'[ATCG]', pattern):
         self.match_positions.append(match.start(0))

   def finditer(self, sequence):
      for match_sequence in re.finditer(self.pattern, sequence):
         for match_position in self.match_positions:
            yield match_sequence.start(0)+match_position

