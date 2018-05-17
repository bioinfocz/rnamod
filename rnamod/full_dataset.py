import numpy as np
import scipy as sc

class FullDataset:
   def __init__(self, name, sequence_data):
      self.name = name
      self.sequence_data = sequence_data
      self.reads = 0

   def calculate(self):
      coverages = []
      errors = []
      errors_A = []

      for position in self.sequence_data.positions:
         dataset_detail = position.dataset(self.name)
         coverages.append(dataset_detail.coverage)
         errors.append(dataset_detail.errors)
         errors_A.append(dataset_detail.errors_A)

      self.average_coverage = int(np.mean(coverages))
      self.sd_coverage = int(np.std(coverages))
      self.average_errors = int(np.mean(errors))
      self.sd_errors = int(np.std(errors))
      self.relative_errors = 100*errors/coverages
      self.relative_A_errors = 100*errors_A/coverages
