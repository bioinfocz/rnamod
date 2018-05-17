import collections
from .position_data import PositionData
from .dataset_detail import DatasetDetail
from .full_dataset import FullDataset

class SequenceData:
   def __init__(self, sequence, patterns):
      self.positions = []
      self.dataset_names = []
      self.full_datasets = collections.OrderedDict()

      for i, base in enumerate(sequence):
         self.positions.append(PositionData(base, i))

      for pattern in patterns:
         for pos in pattern.finditer(sequence):
            self.position(pos).add_pattern_match(pattern)

   # Position on sequence starts from 1
   def position(self, pos):
      return self.positions[pos-1]

   def full_dataset(self, name):
      return self.full_datasets[name]

   def ensure_dataset(self, name, check_dataset=False):
      if name in self.dataset_names:
         return

      for positions in self.positions:
         positions.datasets[name] = DatasetDetail(check_dataset)

      self.full_datasets[name] = FullDataset(name, self)
      self.dataset_names.append(name)

   def calculate(self):
      for position in self.positions:
         position.calculate()

      for _, dataset in self.full_datasets.items():
         dataset.calculate()
