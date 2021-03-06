# RNAmod

Find RNA modifications in sam files.

### Requirements

- python >= 3
- node >= 8

### Install

If you want only TSV (not graphic output) you can skip 2-4 steps.

1. Clone the repository

2. Make sure that your version of nodejs is higher than 8

```bash
sudo apt install nodejs
node --version
```

3. Install npmjs

```bash
sudo apt install npm
npm --version
```

4. Install puppeteer

```bash
npm install puppeteer
```

5. Install python dependencies

```bash
pip3 install -r requirements.txt
```

## Usage

```bash
bin/rnamod OPTIONS
bin/rnamod --help
```

Miminal configurations

```bash
bin/rnamod --experiment exp1.sam exp2.sam \
           --checks chck1.sam chck.sam \
           --fasta seq1.fa seq2.fa seq3.fa \
```

#### Required options

`--sam EXPERIMENT CHECK`
- EXPERIMENT: Your experiment
- CHECK: Files wich will be compared to experiments

`--fasta`
- Sequence files
- Only FASTA format allowed

#### Optional options

`--pattern`
- Find pattern(s) in sequence
- [atcg]: pattern but unimportant bases
- [ATCG]: important bases (marked in outputs)
- [.]: any unimportant bases

`--min-coverage`
- Min coverage for each position

`--max-pvalue`
- Max pvalue when position is still significant

`--min-stops-relative`
- Min reltive stops when position is significant

`--min-errors-relative`
- Min relative erros when position is significant

`--significant-stops-relative`
- When stop is significant

`--significant-errors-relative`
- When error is significant

`--significant-insertion-relative`
- Significant insertion

`--significant-deletion-relative`
- Significant deletion

`--max-pattern-missmatch`
- Maximum missmatch allowed in pattern matching

`--boundary`
- Set boundaries for sequences (SEQUENCE FROM TO)
- For example if you want sequence HIVNL43 stop at position 9711
- _--boundary HIVNL43 0 9711_

`--no-graphic`
- No graphic output
- Useful if you don't have node installed

`--no-tsv`
- If you don't want TSV output

`--outputs`
- Custom directory where results are saved

## Credits

- Ondřej Moravčík ([@ondra-m](https://github.com/ondra-m))
- Jan Pačes ([@hpaces](https://github.com/hpaces))

---

<a href="https://www.img.cas.cz/en">
  <img src="https://github.com/bioinfocz/rnamod/raw/master/assets/img.png" width=100>
</a>

---

<a href="https://www.elixir-czech.cz">
  <img src="https://github.com/bioinfocz/rnamod/raw/master/assets/elixir.png" width=100>
</a>
