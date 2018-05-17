import collections
from scipy import stats

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
      experiments_stops = []
      experiments_errors = []
      checks_stops = []
      checks_errors = []

      for _, dataset in self.datasets.items():
         dataset.calculate()

         if dataset.check_dataset:
            checks_stops.append(dataset.stops_coverage_relative)
            checks_errors.append(dataset.errors_relative)
         else:
            experiments_stops.append(dataset.stops_coverage_relative)
            experiments_errors.append(dataset.errors_relative)

      _, self.pvalue_stops = stats.ttest_ind(experiments_stops, checks_stops)
      _, self.pvalue_errors = stats.ttest_ind(experiments_errors, checks_errors)
