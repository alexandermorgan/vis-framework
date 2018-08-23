.. _design_principles:

Design Principles
=================

Three Simple Components
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In essence, the VIS Framework is built on three simple components: *analyzers* make music analysis decisions; *models* run analyzers on a score.
In other words, the three components are about analysis decisions, making the decisions happen, and ordering the decision-happening.

Consider this example.
A common task for VIS is to count the number of vertical intervals in a piece of music.
An *analyzer* makes a single type of music analysis decision, for a single moment.
For example, the analyzer called *IntervalIndexer* takes two note names and determines the interval between them.

For a relatively simple music analysis task like counting the number of vertical intervals, these three components may seem anything *but* simple.
For more complicated music analysis tasks, the Framework's architecture begins to pay off.
Whether finding contrapuntal modules, analyzing harmonic function, or anything else, these components will be enough to get the job done.
Complicated analysis tasks will always be complicated, but VIS provides a solid, predictable Framework for any task, allowing you to focus on what's special about your query, rather than on making sure you remember how to load pieces properly.

Three Levels of Interaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because of its flexibility, you may choose to interact with the VIS Framework on one of three levels, depending on the flexibility required for your task.

If you simply want to use VIS for one of its built-in queries, like finding vertical intervals or contrapuntal modules, you can use VIS **as a program**.
You may do this through a graphical interface like the `Counterpoint Web App <https://counterpoint.elvisproject.ca>`_ or through the Python shell directly, as described in :ref:`use_as_a_program`.

You can use VIS **as a library**.
For example, you may wish to analyze melodic patterns with *n*-grams, as described in :ref:`tutorial-melodic_ngrams`.

Finally, if your query cannot be implemented using the built-in analyzers, you can use VIS **as a framework**, adding analyzer modules as necessary.

A More Detailed Look
=========================

Indexers
^^^^^^^^^^^^^^^^^^^^^^^^^

The VIS Framework consists of a wide variety of indexers.

**Indexers** use a :class:`music21.stream.Score`, or a :class:`pandas.DataFrame` from another indexer, to perform a music analytic calculation.
The output of any indexer can be sensibly attached to a specific moment of a piece.
That is, indexers are for events that "happen" at an identifiable time.
Indexers may be relatively simple, like the :class:`~vis.analyzers.indexers.interval.IntervalIndexer`, which accepts an index of the notes and rests in a piece, transforming it into an index of the vertical intervals between all the pairs of parts.
Indexers may also be complicated, like the :class:`~vis.analyzers.indexers.ngram.NGramIndexer`, which accepts at least one index of anything, and outputs an index of successions found therein.
An indexer might tell you scale degrees, the harmonic function of a chord, the figured bass signature of a simultaneity, or the moment of a modulation.

Two Types of Models
^^^^^^^^^^^^^^^^^^^^^^^^^

VIS uses two types of models: :class:`~vis.models.indexed_piece.IndexedPiece` and :class:`~vis.models.aggregated_pieces.AggregatedPieces`.
These models represent a single piece (or movement), and a group of pieces (and movements), respectively.
In a typical application, you will write analyzers but never call their methods directly.
On the other hand, you will almost never modify the models, but call their methods very often.
Models know how to run analyzers on the piece or pieces they represent, how to import music21 :class:`Score` objects safely and efficiently, and how to find and access metadata.
The models also perform some level of automated error-handling and data-coordination.
In the future, the models may also help coordinate multiprocessing or results-caching, and they should be able to do this without a change in the API.
