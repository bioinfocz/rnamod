import glob
import os
import re

try:
   from IPython import embed as repl
except NameError:
   pass

import jinja2

from .utils import *
from .pattern import Pattern
from .sequence_data import SequenceData

SAM_QNAME = 0  # Query template NAME (String)
SAM_FLAG  = 1  # bitwise FLAG (Int)
SAM_RNAME = 2  # References sequence NAME (String)
SAM_POS   = 3  # 1- based leftmost mapping POSition (Int)
SAM_MAPQ  = 4  # MAPping Quality (Int)
SAM_CIGAR = 5  # CIGAR String (String)
SAM_RNEXT = 6  # Ref. name of the mate/next read (String)
SAM_PNEXT = 7  # Position of the mate/next read (Int)
SAM_TLEN  = 8  # observed Template LENgth (Int)
SAM_SEQ   = 9  # segment SEQuence (String)
SAM_QUAL  = 10 # ASCII of Phred-scaled base QUALity+33 (String)

FLAG_MAPPED                             = 0    # Mapped
FLAG_READ_PAIRED                        = 1    # Read paired
FLAG_READ_MAPPED_IN_PROPER_PAIR         = 2    # Read mapped in proper pair
FLAG_READ_UNMAPPED                      = 4    # Read unmapped
FLAG_MATE_UNMAPPED                      = 8    # Mate unmapped
FLAG_READ_REVERSE_STRAND                = 16   # Read reverse strand
FLAG_MATE_REVERSE_STRAND                = 32   # Mate reverse strand
FLAG_FIRST_IN_PAIR                      = 64   # First in pair
FLAG_SECOND_IN_PAIR                     = 128  # Second in pair
FLAG_NOT_PRIMARY_ALIGNMENT              = 256  # Not primary alignment
FLAG_READ_FAILS_PLATFORM_QUALITY_CHECKS = 512  # Read fails platform/vendor quality checks
FLAG_READ_IS_PCR_OR_OPTICAL_DUPLICATE   = 1024 # Read is PCR or optical duplicate
FLAG_SUPPLEMENTARY_ALIGNMENT            = 2048 # Supplementary alignment

CIGAR_MATCH             = 'M' # Alignment match (can be a sequence match or mismatch)
CIGAR_INSERTION         = 'I' # Insertion to the reference
CIGAR_DELETION          = 'D' # Deletion from the reference
CIGAR_SKIPPED           = 'N' # Skipped region from the reference
CIGAR_SOFT_CLIPPING     = 'S' # Soft clipping (clipped sequences present in SEQ)
CIGAR_HARD_CLIPPING     = 'H' # Hard clipping (clipped sequences NOT present in SEQ)
CIGAR_PADDING           = 'P' # Padding (silent deletion from padded reference)
CIGAR_SEQUENCE_MATCH    = '=' # Sequence match
CIGAR_SEQUENCE_MISMATCH = 'X' # Sequence mismatch

DELETED_BASE_MARK = '-'

class Mod:
   def __init__(self, fasta_files, patterns):
      self.load_full_sequences(fasta_files)
      self.load_patterns(patterns)
      self.load_rname_results()

   def load_full_sequences(self, fasta_files):
      self.full_sequences = {}

      for files in flatten(fasta_files):
         for file in glob.glob(files):
            if not os.path.exists(file):
               raise IOError('File {} does not exist'.format(file))

            current_name = None
            with open(file) as f:
               for line in f:
                  line = line.rstrip()

                  if line.startswith('>'):
                     current_name = line.split(maxsplit=1)[0][1:]
                     self.full_sequences[current_name] = ''
                  else:
                     self.full_sequences[current_name] += line

   def load_patterns(self, patterns):
      self.patterns = []
      if patterns:
         for pattern in flatten(patterns):
            self.patterns.append(Pattern(pattern))

   def load_rname_results(self):
      self.rname_results = {}
      for rname, sequence in self.full_sequences.items():
         self.rname_results[rname] = SequenceData(sequence, self.patterns)

   def parse_file(self, file, check_dataset=False):
      print('File: {}'.format(file))

      line_index = 0
      dataset_name = os.path.basename(file)

      with open(file) as f:
         for line in f:
            line_index += 1

            if line_index % 10000 == 0:
               print('line_index = {}'.format(line_index), end="\r")

            if line.startswith('@'):
               continue

            line = line.rstrip().split("\t")

            flag = int(line[SAM_FLAG])
            if flag != FLAG_MAPPED and flag != FLAG_READ_REVERSE_STRAND:
               continue

            rname = line[SAM_RNAME]

            if rname not in self.rname_results:
               raise ValueError('{} in not part of any fasta files'.format(rname))
               # continue

            seq = line[SAM_SEQ]
            position = int(line[SAM_POS])
            cigar = re.findall(r'(\d+)([^\d])', line[SAM_CIGAR])

            current_read = ''
            correct_read = ''
            seq_pointer = 0
            full_sequence_pointer = position-1

            for (count, op) in cigar:
               count = int(count)

               if op == CIGAR_SOFT_CLIPPING:
                  seq_pointer += count
               elif op == CIGAR_HARD_CLIPPING:
                  # Nothing todo
                  pass
               elif op == CIGAR_MATCH:
                  current_read += seq[seq_pointer:seq_pointer+count]
                  correct_read += self.full_sequences[rname][full_sequence_pointer:full_sequence_pointer+count]

                  seq_pointer += count
                  full_sequence_pointer += count
               elif op == CIGAR_INSERTION:
                  seq_pointer += count
               elif op == CIGAR_DELETION:
                  current_read += (DELETED_BASE_MARK * count)
                  correct_read += self.full_sequences[rname][full_sequence_pointer:full_sequence_pointer+count]
                  full_sequence_pointer += count
               else:
                  raise ValueError('Invalid CIGAR op: {}'.format(op))

            if len(current_read) != len(correct_read):
               raise ValueError('Reads has different size (qname: {}, rname: {})'.format(line[SAM_QNAME], rname))

            sequence_data = self.rname_results[rname]
            sequence_data.ensure_dataset(dataset_name, check_dataset)

            for i, (current_base, corrent_base) in enumerate(zip(current_read, correct_read)):
               full_sequence_pointer = position+i

               dataset_detail = sequence_data.position(full_sequence_pointer).dataset(dataset_name)
               dataset_detail.coverage += 1

               if current_base == DELETED_BASE_MARK:
                  continue

               # full_sequence_pointer = 0: cannot happen
               # full_sequence_pointer = 1: first position but prev is last
               # full_sequence_pointer = 2: prev is first
               if full_sequence_pointer > 1:
                  prev_dataset_detail = sequence_data.position(full_sequence_pointer-1).dataset(dataset_name)
                  prev_dataset_detail.coverage_for_stops += 1

                  if i == 0:
                     prev_dataset_detail.stops += 1

               if current_base != corrent_base:
                  dataset_detail.errors += 1
                  dataset_detail['errors_'+current_base] += 1


   def run(self, experiment_files, check_files):
      for files in flatten(experiment_files):
         for file in glob.glob(files):
            self.parse_file(file)

      for files in flatten(check_files):
         for file in glob.glob(files):
            self.parse_file(file, check_dataset=True)

      for _, sequence_data in self.rname_results.items():
         sequence_data.calculate()

   def to_html(self, directory):
      env = jinja2.Environment(
         loader=jinja2.PackageLoader('rnamod', 'templates'),
         autoescape=jinja2.select_autoescape(['html'])
      )

      for rname, sequence_data in self.rname_results.items():
         repl()

         template = env.get_template('summary.html')
         with open("outputs/summary.html", "w") as f:
            f.write(template.render(
               heading=rname,
               dataset_names=sequence_data.dataset_names,
               positions=sequence_data.positions,
            ))

