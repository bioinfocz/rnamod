import re
import rnamod.config as config

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

   def pattern_matched(self, sequence, sequence_index):
      pattern_index = 0
      missmatch = 0

      while pattern_index < len(self.pattern):
         if sequence_index >= len(sequence):
            return False

         sequence_base = sequence[sequence_index]
         pattern_base = self.pattern[pattern_index]

         if pattern_base == '.':
            # On sequence can be anything
            pass
         elif (pattern_index in self.match_positions) and sequence_base != pattern_base:
            # Big letter must match
            return False
         elif sequence_base.lower() == pattern_base.lower():
            # Bases are equal
            pass
         else:
            if missmatch >= config.max_pattern_missmatch:
               return False
            else:
               missmatch += 1

         pattern_index += 1
         sequence_index += 1

      return True

   def finditer(self, sequence):
      for sequence_index, _ in enumerate(sequence):
         if self.pattern_matched(sequence, sequence_index):
            for match_position in self.match_positions:
               yield sequence_index+match_position
