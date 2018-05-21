import math
import collections
from scipy import stats
import rnamod.config as config
import rnamod.utils as utils

class PositionData:
   def __init__(self, base, position):
      self.base = base
      self.position = position
      self.datasets = collections.OrderedDict()
      self.patterns_matched = []
      self._is_significant = None

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
         self.pvalue_stops = 1 - utils.relative_diff(experiments_stops, checks_stops)
         self.pvalue_errors = 1 - utils.relative_diff(experiments_errors, checks_errors)
      else:
         _, self.pvalue_stops = stats.ttest_ind(experiments_stops, checks_stops)
         _, self.pvalue_errors = stats.ttest_ind(experiments_errors, checks_errors)

   def is_stops_significant(self):
      if math.isnan(self.pvalue_stops) or self.pvalue_stops > config.max_pvalue:
         return False

      for _, dataset in self.datasets.items():
         if dataset.stops_coverage > config.min_coverage and dataset.stops_coverage_relative > config.min_stops_relative:
            return True

      return False

   def is_errors_significant(self):
      if math.isnan(self.pvalue_errors) or self.pvalue_errors > config.max_pvalue:
         return False

      for _, dataset in self.datasets.items():
         if dataset.coverage > config.min_coverage and dataset.errors_relative > config.min_errors_relative:
            return True

      return False

   def is_significant(self):
      if self._is_significant != None:
         return self._is_significant

      if len(self.patterns_matched) > 0:
         self._is_significant = True
         return True

      if self.is_stops_significant() or self.is_errors_significant():
         self._is_significant = True
         return True

      self._is_significant = False
      return False

