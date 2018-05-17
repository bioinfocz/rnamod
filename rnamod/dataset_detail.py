from .utils import *
import rnamod.config as config

class DatasetDetail:
   def __init__(self, check_dataset=False):
      self.check_dataset = check_dataset

      self.coverage = 0
      self.errors = 0
      self.errors_A = 0
      self.errors_T = 0
      self.errors_C = 0
      self.errors_G = 0

      self.stops = 0
      self.stops_coverage = 0

   def __getitem__(self, key):
      return self.__dict__[key]

   def __setitem__(self, key, value):
      self.__dict__[key] = value

   def calculate(self):
      self.errors_relative = relative_of(self.errors, self.coverage)
      self.errors_A_relative = relative_of(self.errors_A, self.coverage)
      self.errors_T_relative = relative_of(self.errors_T, self.coverage)
      self.errors_C_relative = relative_of(self.errors_C, self.coverage)
      self.errors_G_relative = relative_of(self.errors_G, self.coverage)
      self.stops_coverage_relative = relative_of(self.stops, self.stops_coverage)

   def rgba_stops_coverage_relative(self):
      return 'rgba({},{})'.format(config.colors.stops, self.stops_coverage_relative/100)

   def rgba_errors_relative(self):
      return 'rgba({},{})'.format(config.colors.errors, self.errors_relative/100)
