import os
import re
import glob
import uuid
import subprocess

import jinja2

from .utils import *
from .pattern import Pattern
from .sequence_data import SequenceData
import rnamod.config as config

try:
   from IPython import embed as repl
except NameError:
   pass

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
      print('Parsing file: {}'.format(file))

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
            insertion_positions = []
            deletion_positions = []

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
                  insertion_positions.append(full_sequence_pointer+1)
               elif op == CIGAR_DELETION:
                  current_read += (DELETED_BASE_MARK * count)
                  correct_read += self.full_sequences[rname][full_sequence_pointer:full_sequence_pointer+count]
                  full_sequence_pointer += count
                  deletion_positions.append(full_sequence_pointer+1)
               else:
                  raise ValueError('Invalid CIGAR op: {}'.format(op))

            if len(current_read) != len(correct_read):
               raise ValueError('Reads has different size (qname: {}, rname: {})'.format(line[SAM_QNAME], rname))

            sequence_data = self.rname_results[rname]
            sequence_data.ensure_dataset(dataset_name, check_dataset)

            full_dataset = sequence_data.full_dataset(dataset_name)
            full_dataset.reads += 1

            for i, (current_base, corrent_base) in enumerate(zip(current_read, correct_read)):
               full_sequence_pointer = position+i

               dataset_detail = sequence_data.position(full_sequence_pointer).dataset(dataset_name)
               dataset_detail.coverage += 1

               if full_sequence_pointer in insertion_positions:
                  dataset_detail.insertions += 1

               if full_sequence_pointer in deletion_positions:
                  dataset_detail.deletions += 1

               if current_base == DELETED_BASE_MARK:
                  continue

               # full_sequence_pointer = 0: cannot happen
               # full_sequence_pointer = 1: first position but prev is last
               # full_sequence_pointer = 2: prev is first
               if full_sequence_pointer > 1:
                  prev_dataset_detail = sequence_data.position(full_sequence_pointer-1).dataset(dataset_name)
                  prev_dataset_detail.stops_coverage += 1

                  if i == 0:
                     prev_dataset_detail.stops += 1

               if current_base != corrent_base:
                  dataset_detail.errors += 1
                  dataset_detail['errors_'+current_base] += 1

   def run(self, sam):
      for (experiment, check) in sam:
         self.parse_file(experiment)
         self.parse_file(check, check_dataset=True)

      for _, sequence_data in self.rname_results.items():
         sequence_data.calculate()

   def export_graphic(self, file, content):
      export_js = os.path.realpath(
         os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../src/export.js'))

      with open(file, 'w') as f:
         f.write(content)

      subprocess.call(['node', export_js, file])

   def positions_with_boundaries(self, rname, sequence_data):
      positions = sequence_data.positions

      for (seq, sfrom, sto) in config.boundaries:
         if seq.lower() != rname.lower():
            continue

         positions = []
         for position in sequence_data.positions:
            if position.position > sfrom and position.position < sto:
               positions.append(position)

         break

      return positions

   def to_graphic(self, directory):
      env = jinja2.Environment(
         loader=jinja2.PackageLoader('rnamod', 'templates'),
         autoescape=jinja2.select_autoescape(['html'])
      )

      layout_template = env.get_template('layout.html')
      summary_template = env.get_template('summary.html')
      chart_template = env.get_template('chart.html')

      mod_dir = os.path.dirname(os.path.realpath(__file__))
      script_js = os.path.join(mod_dir, 'assets', 'script.js')
      style_css = os.path.join(mod_dir, 'assets', 'style.css')

      def render_in_layout(*bodies, chart_included=False):
         return layout_template.render(
            chart_included=chart_included,
            body=''.join(bodies),
            style_css=style_css,
            script_js=script_js,
         )

      for rname, sequence_data in self.rname_results.items():
         if not sequence_data.any_datasets():
            continue

         positions = self.positions_with_boundaries(rname, sequence_data)

         summary_body = summary_template.render(
            heading=rname,
            dataset_names=sequence_data.dataset_names,
            positions=positions,
            full_datasets=sequence_data.full_datasets,
            patterns=self.patterns,
            config=config
         )

         chart_bodies = {}
         for dataset_name in sequence_data.dataset_names:
            chart_data = []
            for position in positions:
               dataset = position.dataset(dataset_name)
               position_data = {
                  'base': position.base,
                  'position': position.position,
                  'coverage': dataset.coverage,
               }

               if position.is_significant():
                  position_data['errors_relative'] = dataset.errors_relative
                  position_data['stops_coverage_relative'] = dataset.stops_coverage_relative
               else:
                  position_data['errors_relative'] = 0
                  position_data['stops_coverage_relative'] = 0

               chart_data.append(position_data)

            chart_bodies[dataset_name] = chart_template.render(
               rname=rname,
               dataset_name=dataset_name,
               uniq_id=str(uuid.uuid4()),
               chart_data=chart_data,
            )

         summary_file = os.path.join(directory, 'summary_{}.html'.format(rname))
         summary_content = render_in_layout(summary_body)
         print('Exporting {} summary'.format(rname))
         self.export_graphic(summary_file, summary_content)

         summary_with_charts_file = os.path.join(directory, 'summary_with_charts_{}.html'.format(rname))
         summary_with_charts_content = render_in_layout(summary_body, *chart_bodies.values(), chart_included=True)
         print('Exporting {} summary with all charts'.format(rname))
         self.export_graphic(summary_with_charts_file, summary_with_charts_content)

         for dataset_name, chart_body in chart_bodies.items():
            chart_file = os.path.join(directory, 'chart_{}__{}.html'.format(rname, dataset_name))
            chart_content = render_in_layout(chart_body, chart_included=True)
            print('Exporting {} chart from {}'.format(rname, dataset_name))
            self.export_graphic(chart_file, chart_content)

   def to_tsv(self, directory):
      for rname, sequence_data in self.rname_results.items():
         if not sequence_data.any_datasets():
            continue

         positions = self.positions_with_boundaries(rname, sequence_data)

         print('Exporting {} table'.format(rname))
         with open(os.path.join(directory, 'table_{}.tsv'.format(rname)), 'w') as f:
            row = []
            row.append('Position')
            row.append('Base')
            row.append('Pattern matched')

            for name in sequence_data.dataset_names:
               row.append(name + ' stops (%)')
               row.append(name + ' errors (%)')

            row.append('Stops p-value')
            row.append('Errors p-value')

            f.write('\t'.join(map(str, row)))
            f.write('\n')

            for position in positions:
               if not position.is_significant():
                  continue

               row = []
               row.append(position.position)
               row.append(position.base)
               row.append(len(position.patterns_matched))

               for name, dataset in position.datasets.items():
                  row.append(dataset.stops_coverage_relative)
                  row.append(dataset.errors_relative)

               row.append(position.pvalue_stops)
               row.append(position.pvalue_errors)

               f.write('\t'.join(map(str, row)))
               f.write('\n')
