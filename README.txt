Vizitka
=================

The Vizitka is a Python package that uses the music21 and the pandas library to
build a flexible system for writing computational music analysis programs.
Examples of how to use the program can be found in the different indexers in
the indexers folder. If you need any assistance using this program, or if you
think that automating something would make it easier to use the program, please
just ask me about it and I'll see what I can do.

Copyright Information:
* All source code is subject to the GNU AGPL 3.0 Licence. A copy of this licence is included as doc/apg-3.0.txt.
* All other content is subject to the CC-BY-SA Unported 3.0 Licence. A copy of this licence is included as doc/CC-BY-SA.txt
* All content in the test_corpus directory is subject to the licence in the file test_corpus/test_corpus_licence.txt

Software Dependencies
=====================

The Vizitka has three core software dependencies. These are required:

- [Python 3.7](https://www.python.org)
- [music21 5.3](http://web.mit.edu/music21/)
- [pandas 0.23.1](http://pandas.pydata.org)

These are recommended dependencies:

- [numexpr](https://pypi.python.org/pypi/numexpr) (improved performance for pandas)
- [Bottleneck](https://pypi.python.org/pypi/Bottleneck) (improved performance for pandas)
- [tables](https://pypi.python.org/pypi/tables) (HDF5 output for pandas)
- [openpyxl](https://pypi.python.org/pypi/openpyxl) (Excel output for pandas)
- [mock](https://pypi.python.org/pypi/mock) (for testing)
- [coverage](https://pypi.python.org/pypi/coverage) (for testing)
- [python-coveralls](https://pypi.python.org/pypi/python-coveralls) (to for automated coverage with coveralls.io)

Documentation
=============

At the moment there is no guarantee that everything is documented, but most indexers are well documented and the Readme file covers the basics of how to use Vizitka.

Citation
========

If you want to cite Vizitka, please cite the github repository.

If you wish to cite the VIS, which is the program that Vizitka originated from, please use this ISMIR 2014 article:

Antila, Christopher and Julie Cumming. "The VIS-Framework: Analyzing Counterpoint in Large Datasets."
    In Proceedings of the International Society for Music Information Retrieval, 2014.

A BibTeX entry for LaTeX users is

```
@inproceedings{,
    title = {The VIS-Framework: Analyzing Counterpoint in Large Datasets},
    author = {Antila, Christopher and Cumming, Julie},
    booktitle = {Proceedings of the International Society for Music Information Retrieval},
    location = {Taipei, Taiwan},
    year = {2014},
}
```

You may also wish to cite the software of VIS itself:

Antila, Christopher, Alexander Morgan, Jamie Klassen, and Marina Cotrell. The VIS-Framework for Music Analysis. McGill University, Montreal, 2016.

A BibTeX entry for LaTeX users is

```
@Manual{,
    title = {The VIS-Framework for Music Analysis},
    author = {Antila, Christopher and Morgan, Alexander and Klassen, Jamie and Cotrell, Marina},
    organization = {McGill University},
    location = {Montréal, Québec},
    year = {2016},
}
```
