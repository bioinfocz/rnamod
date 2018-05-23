import os
import re

class OpenDict(dict):
   __getattr__ = dict.get
   __setattr__ = dict.__setitem__
   __delattr__ = dict.__delitem__

def flatten(items):
   for item in items:
      if isinstance(item, list):
         yield from flatten(item)
      else:
         yield item

def relative_of(value, total):
   if total == 0:
      return 0
   else:
      return round((100.0 * value) / total, 2)

def relative_diff(values1, values2):
   values1_average = sum(values1) / len(values1)
   values2_average = sum(values2) / len(values2)

   values_max = max(values1_average, values2_average)
   if values_max == 0:
      return 0
   else:
      return abs(values1_average-values2_average) / values_max

def ensure_directory(name):
   while os.path.exists(name):
      name, count = re.subn(r'_(\d+)$', lambda m: '_'+str(int(m.group(1))+1), name)
      if count == 0:
         name += '_1'

   os.makedirs(name)
   return name
