import math
import collections
from scipy import stats
import rnamod.config as config

class PositionData:
   def __init__(self, base, position):
      self.base = base
      self.position = position
      self.datasets = collections.OrderedDict()
      self.patterns_matched = []

   def add_pattern_match(self, pattern):
      self.patterns_matched.append(pattern)

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

      if len(experiments_stops) == 1 or len(experiments_errors) == 1:
         experiments_stops = sum(experiments_stops) / len(experiments_stops)
         experiments_errors = sum(experiments_errors) / len(experiments_errors)
         checks_stops = sum(checks_stops) / len(checks_stops)
         checks_errors = sum(checks_errors) / len(checks_errors)

         self.pvalue_stops = abs(experiments_stops-checks_stops) / max(experiments_stops, checks_stops)
         self.pvalue_errors = abs(experiments_errors-checks_errors) / max(experiments_errors, checks_errors)
      else:
         _, self.pvalue_stops = stats.ttest_ind(experiments_stops, checks_stops)
         _, self.pvalue_errors = stats.ttest_ind(experiments_errors, checks_errors)

   def is_stops_significant(self):
      if math.isnan(self.pvalue_stops) or self.pvalue_stops > config.min_pvalue:
         return False

      for _, dataset in self.datasets.items():
         if dataset.stops_coverage > config.min_coverage and dataset.stops_coverage_relative > config.min_stops_relative:
            return True

      return False

   def is_errors_significant(self):
      if math.isnan(self.pvalue_errors) or self.pvalue_errors > config.min_pvalue:
         return False

      for _, dataset in self.datasets.items():
         if dataset.coverage > config.min_coverage and dataset.errors_relative > config.min_errors_relative:
            return True

      return False

   def is_significant(self):
      if len(self.patterns_matched) > 0:
         return True

      if self.is_stops_significant() or self.is_errors_significant():
         return True

      return False

