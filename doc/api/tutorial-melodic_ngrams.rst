
.. _tutorial-melodic_ngrams:

Tutorial: Use *N*-Grams to Find Melodic Patterns
------------------------------------------------

Once you understand our framework's architecture (explained in :ref:`design_principles`), you can design new queries to answer your own questions.

Develop a Question
------------------

Our research question involves numerically comparing melodic styles of multiple composers.
To help focus our findings on the differences between *composers*, our test sets should consist of pieces that are otherwise as similar as possible.
One of the best ways to compare styles is using patterns, which are represented in the VIS Framework as *n*-grams: a unit of *n* objects in a row.
While the Framework's *n*-gram functionality is fairly complex, in this tutorial we will focus on simple *n*-grams of melodic intervals, which will help us find melodic patterns.
The most frequently occurring melodic patterns will tell us something about the melodic styles of the composers under consideration: we will be pointed to some similarities and some differences that, taken together, will help us refine future queries.

Since *n*-grams are at the centre of the preliminary investigation described in this tutorial, we will use the corresponding :class:`~vis.analyzers.indexers.ngram.NGramIndexer` to guide our development.
We must answer two questions:

    #. What data will the :class:`NGramIndexer` require to find melodic patterns?
    #. What steps are required after the :class:`NGramIndexer` to produce meaningful results?

We investigate these two questions in the following sections.

What Does the NGramIndexer Require?
-----------------------------------

To begin, try reading the documentation for the :class:`~vis.analyzers.indexers.ngram.NGramIndexer`.
At present, this Indexer is the most powerful and most complicated module in the VIS Framework, and as such it may pose difficulties and behave in unexpected ways.
For this tutorial we focus on the basic functionality: the "n" and "vertical" settings.

TODO: continue revising here

For this simple preliminary investigation, we need only provide the melodic intervals of every part in an :class:`IndexedPiece`.
The melodic intervals will be the "vertical" events; there will be no "horizontal" events.
We can change the "mark_singles" and "continuer" settings any time as we please.
We will probably want to try many different pattern lengths by changing the "n" setting.
If we do not wish our melodic patterns to include rests, we can set "terminator" to ``['Rest']``.

Thus the only information :class:`NGramIndexer` requires from another analyzer is the melodic intervals, produced by :class:`~vis.analyzers.indexers.HorizontalIntervalIndexer`, which will confusingly be the "vertical" event.
As specified in its documentation, the :class:`HorizontalIntervalIndexer` requires the output of the :class:`~vis.analyzers.indexers.noterest.NoteRestIndexer`, which operates directly on the music21 :class:`Score`.

The first part of our query looks like this:

.. code-block:: python
    :linenos:

    from vis.indexers import noterest, interval, ngram
    from vis.models.indexed_piece import IndexedPiece

    # prepare inputs and output-collectors
    pathnames = [list_of_pathnames_here]
    ind_ps = [IndexedPiece(x) for x in pathnames]
    interval_settings = {'quality': True}
    ngram_settings = {'vertical': 0, 'n': 3}  # change 'n' as required
    ngram_results = []

    # prepare for and run the NGramIndexer
    for piece in ind_ps:
        intervals = piece.get([noterest.NoteRestIndexer, interval.HorizontalIntervalIndexer], interval_settings)
        for part in intervals:
            ngram_results.append(piece.get([ngram.NGramIndexer], ngram_settings, [part])

After the imports, we start by making a list of all the pathnames to use in this query, then use a Python list comprehension to make a list of :class:`IndexedPiece` objcects for each file.
We make the settings dictionaries to use for the interval then n-gram indexers on lines 7 and 8, but note we have not included all possible settings.
The empty ``ngram_results`` list will store results from the :class:`NGramIndexer`.

The loop started on line 12 is a little confusing: why not use an :class:`AggregatedPieces` object to run the :class:`NGramIndexer` on all pieces with a single call to :meth:`get`?
The reason is the inner loop, started on line 14: if we run the :class:`NGramIndexer` on an :class:`IndexedPiece` once, we can only index a single part, but we want results from all parts.
This is the special burden of using the :class:`NGramIndexer`, which is flexible but not (yet) intelligent.
In order to index the melodic intervals in every part using the :meth:`get` call on line 15, we must add the nested loops.
