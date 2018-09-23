VERSION HISTORY
===============
This file records version-to-version changes in the Vizitka. The most recent versions are at
the top of the file. Vizitka originated as a fork of the VIS-Framework repository,
so if you would like to see the version history of VIS, take a look at their
version history document.

* 0.1.0:
    -Forks from VIS-Framework repo
    -Renames program Vizitka
    -Removes Windexer
    -Removes all experimenters
    -Removes engineering folder and contained files
    -Add to_kern and to_XML methods for file conversion
    -Walks back a lots of fluff documentation commits, though many still remain
        where it was too complicated to resolve git conflicts
    -Sets music21 version to 5.3, and Python version to 3.7
    -Ends support for Python 2
    -Implements measure indexing for midi files
    -Generalizes FermataIndexer, now ExpressionIndexer handles any expression
    -Adds ArticulationIndexer for all articulations
    -Removes indexer templates
    -Reinstates two-character shortcuts in get_data() method
    -Renames get_data() to get()
    -Adds lyric indexer
    -Adds KeySignatureIndexer and ClefIndexer in staff.py
    -Adds TieIndexer to meter.py
    -Adds MensurationIndexer though only commented out version
    -Remove outdated tutorial
    -Update api
