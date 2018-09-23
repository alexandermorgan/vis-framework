.. Vizitka documentation master file, created by
   sphinx-quickstart on Wed Sep 18 00:06:56 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


This is the API documentation for Vizitka.

About This Documentation
------------------------

The API is written for programmers interested in symbolic music information retrieval.

One-Paragraph Introduction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Vizitka uses two data models (:class:`~vis.models.indexed_piece.IndexedPiece` and :class:`~vis.models.aggregated_pieces.AggregatedPieces`) to fetch results for one or multiple pieces, respectively.
Call their :meth:`~vis.models.indexed_piece.IndexedPiece.get` method with a list of analyzer classes to run, and a dictionary with their settings.

Table of Contents
-----------------

Learn about and Install the Vizitka
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. toctree::
    :maxdepth: 2

    about
    install_and_test

Programming Tutorials for VIS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. toctree::
    :maxdepth: 1

    tutorial-melodic_ngrams


API Specification
^^^^^^^^^^^^^^^^^
.. toctree::
   :maxdepth: 5

   modules


Indices and Tables
^^^^^^^^^^^^^^^^^^
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
