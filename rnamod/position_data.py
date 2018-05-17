import collections

class PositionData:
   def __init__(self, base, position):
      self.base = base
      self.position = position
      self.datasets = collections.OrderedDict()
      self.pattern_matches = []

   def add_pattern_match(self, pattern):
      self.pattern_matches.append(pattern)

   def dataset(self, name):
      return self.datasets[name]

   def calculate(self):
      for _, dataset in self.datasets.items():
         dataset.calculate()
