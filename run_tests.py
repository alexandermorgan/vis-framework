#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: run_tests.py
# Purpose: Run automated tests for the Vizitka.
#
# Copyright (C) 2012, 2013, 2014 Jamie Klassen, Christopher Antila, Ryan Bannon, Alexander Morgan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
Run automated tests for the Vizitka.
"""

VERBOSITY = 0

from unittest import TextTestRunner

from vizitka.tests import test_indexer
from vizitka.tests import test_duration_indexer
from vizitka.tests import test_note_beat_strength_indexer
from vizitka.tests import test_measure_indexer
from vizitka.tests import test_note_rest_indexer
from vizitka.tests import test_ngram
from vizitka.tests import test_dissonance_indexer
from vizitka.tests import test_repeat
from vizitka.tests import test_interval_indexer
from vizitka.tests import test_offset
from vizitka.tests import test_indexed_piece
from vizitka.tests import test_aggregated_pieces
from vizitka.tests import bwv2_integration_tests as bwv2
from vizitka.tests import bwv603_integration_tests as bwv603
from vizitka.tests import test_fermata_indexer
from vizitka.tests import test_over_bass
from vizitka.tests import test_approach
from vizitka.tests import test_contour
from vizitka.tests import test_active_voices


THE_TESTS = (  # Indexer and Subclasses
             test_indexer.INDEXER_INIT_SUITE,
             test_indexer.INDEXER_1_PART_SUITE,
             test_fermata_indexer.FERMATA_INDEXER_SUITE,
             test_note_rest_indexer.NOTE_REST_INDEXER_SUITE,
             test_note_rest_indexer.MULTI_STOP_INDEXER_SUITE,
             test_duration_indexer.DURATION_INDEXER_SUITE,
             test_note_beat_strength_indexer.NOTE_BEAT_STRENGTH_INDEXER_SUITE,
             test_measure_indexer.MEASURE_INDEXER_SUITE,
             test_interval_indexer.INTERVAL_INDEXER_SHORT_SUITE,
             test_interval_indexer.INTERVAL_INDEXER_LONG_SUITE,
             test_interval_indexer.INT_IND_INDEXER_SUITE,
             test_interval_indexer.HORIZ_INT_IND_LONG_SUITE,
             test_repeat.REPEAT_INDEXER_SUITE,
             test_ngram.NGRAM_INDEXER_SUITE,
             test_dissonance_indexer.DISSONANCE_INDEXER_SUITE,
             test_offset.OFFSET_INDEXER_SINGLE_SUITE,
             test_offset.OFFSET_INDEXER_MULTI_SUITE,
             test_over_bass.OVER_BASS_INDEXER_SUITE,
             test_approach.APPROACH_INDEXER_SUITE,
             test_contour.CONTOUR_INDEXER_SUITE,
             test_active_voices.ACTIVE_VOICES_INDEXER_SUITE,
             # Importer, IndexedPiece, and AggregatedPieces
             test_aggregated_pieces.IMPORTER_SUITE,
             test_indexed_piece.INDEXED_PIECE_SUITE_A,
             test_indexed_piece.INDEXED_PIECE_PARTS_TITLES,
             test_indexed_piece.INDEXED_PIECE_SUITE_C,
             test_aggregated_pieces.AGGREGATED_PIECES_SUITE,
             # Integration Tests
             bwv2.ALL_VOICE_INTERVAL_NGRAMS,
             bwv603.ALL_VOICE_INTERVAL_NGRAMS,
             )


if __name__ == '__main__':
    for each_test in THE_TESTS:
        result = TextTestRunner(verbosity=VERBOSITY, descriptions=False).run(each_test)
        if not result.wasSuccessful():
            raise RuntimeError('Test failure')
