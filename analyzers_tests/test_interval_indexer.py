#! /usr/bin/python
# -*- coding: utf-8 -*-

#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
#
# Copyright (C) 2013 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------

# allow "no docstring" for everything
# pylint: disable=C0111
# allow "too many public methods" for TestCase
# pylint: disable=R0904


import unittest
import pandas
from music21 import interval, note
from vis.analyzers.indexers.interval import IntervalIndexer, real_indexer
from vis.analyzers_tests.test_note_rest_indexer import TestNoteRestIndexer
from vis.controllers import mpcontroller


class TestIntervalIndexerShort(unittest.TestCase):
    "These 'short' tests were brought over from the vis9 tests for _event_finder()."
    @staticmethod
    def pandas_maker(wrap_this):
        """
        Transform tuple-formatted tests into appropriate pandas.Series.

        Input:
        ======
        --> [[tuples_for_part_1], [tuples_for_part_2], ...]
        --> [[(offset, obj), ...], ...]

        Output:
        =======
        lists of Series, ready for IntervalIndexer.__init__()
        """
        post = []
        for part in wrap_this:
            offsets = []
            objs = []
            for obj in part:
                offsets.append(obj[0])
                objs.append(obj[1])
            post.append(pandas.Series(objs, index=offsets))
        return post

    def test_int_indexer_short_1(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4')], [(0.0, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_2(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        not_processed = [[(0.0, u'G4'), (0.25, u'Rest')],
                         [(0.0, u'G3'), (0.25, u'Rest')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_3(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        not_processed = [[(0.0, u'G4')], [(0.0, u'G3'), (0.25, u'Rest')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_4(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest')]
        not_processed = [[(0.0, u'G4'), (0.25, u'Rest')], [(0.0, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_5(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('F4')).name)]
        not_processed = [[(0.0, u'G4'), (0.5, u'F4')],
                         [(0.0, u'G3'), (0.5, u'A3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_6(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3'), (0.5, u'A3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_7(self):
        expected = [(0.0, interval.Interval(note.Note('B3'), note.Note('A4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (1.0, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (1.5, interval.Interval(note.Note('B3'), note.Note('F4')).name)]
        not_processed = [[(0.0, u'A4'), (0.5, u'G4', 1.0), (1.5, u'F4')],
                         [(0.0, u'B3'), (0.5, u'G3'),
                          (1.0, u'A3'), (1.5, u'B3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_8(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        not_processed =  [[(0.0, u'G4', 1.0)],
                  [(0.0, u'G3'), (0.25, u'Rest'), (0.5, u'A3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_9(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (1.0, interval.Interval(note.Note('B3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0), (1.0, u'G4')],
                [(0.0, u'G3'), (0.25, u'Rest'), (0.5, u'A3'), (1.0, u'B3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_10(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3'), (0.25, u'A3', 0.75)]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_11(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)], [(0.0, u'G3'), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_12(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.25, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)],
                   [(0.0, u'G3'), (0.25, u'Rest'), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_13(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.125, u'Rest'),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (0.375, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 1.0)],
                   [(0.0, u'G3', 0.125), (0.125, u'Rest', 0.125),
                    (0.25, u'A3', 0.125), (0.375, u'Rest', 0.125), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_14(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.0625, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.125, u'Rest'),
                    (0.1875, u'Rest'),
                    (0.25, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (0.3125, interval.Interval(note.Note('A3'), note.Note('G4')).name),
                    (0.375, u'Rest'),
                    (0.4375, u'Rest'),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4', 0.0625), (0.0625, u'G4', 0.0625),
                    (0.125, u'G4', 0.0625), (0.1875, u'G4', 0.0625),
                    (0.25, u'G4', 0.0625), (0.3125, u'G4', 0.0625),
                    (0.375, u'G4', 0.0625), (0.4375, u'G4', 0.0625),
                    (0.5, u'G4')],
                   [(0.0, u'G3', 0.125), (0.125, u'Rest', 0.125), (0.25, u'A3', 0.125),
                    (0.375, u'Rest', 0.0625), (0.4375, u'Rest', 0.0625), (0.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_15(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.75, u'Rest'),
                    (1.0, u'Rest'),
                    (1.5, interval.Interval(note.Note('G3'), note.Note('G4')).name)]
        not_processed = [[(0.0, u'G4'), (0.5, u'G4'), (0.75, u'Rest'),
                    (1.0, u'G4'), (1.5, u'G4')],
                   [(0.0, u'G3'), (0.5, u'G3'), (0.75, u'Rest'),
                    (1.0, u'Rest'), (1.5, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_16(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, u'Rest'),
                    (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
                    (1.25, interval.Interval(note.Note('F3'), note.Note('G4')).name),
                    (1.5, interval.Interval(note.Note('E3'), note.Note('B4')).name)]
        not_processed = [[(0.0, u'G4'), (0.5, u'A4', 0.75),
                          (1.25, u'G4'), (1.5, u'B4')],
                         [(0.0, u'G3'), (0.5, u'Rest'),
                          (0.75, u'F3', 0.75), (1.5, u'E3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_int_indexer_short_17(self):
        expected = [(0.0, interval.Interval(note.Note('G3'), note.Note('G4')).name),
                    (0.5, interval.Interval(note.Note('A3'), note.Note('A4')).name),
                    (0.75, interval.Interval(note.Note('F3'), note.Note('A4')).name),
                    (1.125, u'Rest'),
                    (1.25, u'Rest'),
                    (1.375, interval.Interval(note.Note('G3'), note.Note('F4')).name),
                    (2.0, interval.Interval(note.Note('G3'), note.Note('E4')).name)]
        not_processed = [[(0.0, u'G4'), (0.5, u'A4', 0.75), (1.25, u'F4', 0.75),
                          (2.0, u'E4')],
                         [(0.0, u'G3'), (0.5, u'A3'), (0.75, u'F3', 0.375),
                          (1.125, u'Rest'), (1.375, u'G3', 0.625), (2.0, u'G3')]]
        test_in = TestIntervalIndexerShort.pandas_maker(not_processed)
        int_indexer = IntervalIndexer(test_in,
                                      {u'quality': True, u'simple or compound': u'compound'})
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])


class TestIntervalIndexerLong(unittest.TestCase):
    bwv77_S_B_basis = [
        (0.0, "P8"),
        (0.5, "M9"),
        (1.0, "m10"),
        (2.0, "P12"),
        (3.0, "M10"),
        (4.0, "P12"),
        (4.5, "m13"),
        (5.0, "m17"),
        (5.5, "P12"),
        (6.0, "M13"),
        (6.5, "P12"),
        (7.0, "P8"),
        (8.0, "m10"),
        (9.0, "m10"),
        (10.0, "M10"),
        (11.0, "M10"),
        (12.0, "m10"),
        (13.0, "m10"),
        (14.0, "P12"),
        (15.0, "P8"),
        (16.0, "P8"),
        (16.5, "M9"),
        (17.0, "m10"),
        (18.0, "P12"),
        (19.0, "M10"),
        (20.0, "P12"),
        (20.5, "m13"),
        (21.0, "m17"),
        (21.5, "P12"),
        (22.0, "M13"),
        (22.5, "P12"),
        (23.0, "P8"),
        (24.0, "m10"),
        (25.0, "m10"),
        (26.0, "M10"),
        (27.0, "M10"),
        (28.0, "m10"),
        (29.0, "m10"),
        (30.0, "P12"),
        (31.0, "P8"),
        (32.0, "P8"),
        (32.5, "M9"),
        (33.0, "m13"),
        (33.5, "m14"),
        (34.0, "m13"),
        (34.5, "m14"),
        (35.0, "M10"),
        (36.0, "M10"),
        (36.5, "P11"),
        (37.0, "P12"),
        (38.0, "M10"),
        (39.0, "P15"),
        (40.0, "P12"),
        (40.5, "P11"),
        (41.0, "M13"),
        (42.0, "P12"),
        (43.0, "M17"),
        (43.5, "M16"),
        (44.0, "P12"),
        (44.5, "m13"),
        (45.0, "P15"),
        (45.5, "m14"),
        (46.0, "P12"),
        (47.0, "P15"),
        (48.0, "P12"),
        (49.0, "m10"),
        (50.0, "M13"),
        (50.5, "P12"),
        (51.0, "M10"),
        (52.0, "m10"),
        (52.5, "P11"),
        (53.0, "m13"),
        (53.5, "d12"),
        (54.0, "m10"),
        (55.0, "P12"),
        (56.0, "P8"),
        (56.5, "M10"),
        (57.0, "P12"),
        (57.5, "m13"),
        (58.0, "P15"),
        (59.0, "M17"),
        (60.0, "P15"),
        (60.5, "m13"),
        (61.0, "M13"),
        (61.5, "m14"),
        (62.0, "P12"),
        (63.0, "P8"),
        (64.0, "P15"),
        (65.0, "P12"),
        (65.5, "M13"),
        (66.0, "m14"),
        (66.5, "P15"),
        (67.0, "M17"),
        (68.0, "P15"),
        (68.5, "m14"),
        (69.0, "P12"),
        (69.5, "m14"),
        (70.0, "P12"),
        (71.0, "P15")]

    def setUp(self):
        self.bwv77_soprano = TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_soprano)
        self.bwv77_bass = TestIntervalIndexerLong.do_wrapping(TestNoteRestIndexer.bwv77_bass)
        #self.bwv77_S_B = TestIntervalIndexerLong.do_wrapping(TestIntervalIndexerLong.bwv77_S_B_basis)

    @staticmethod
    def do_wrapping(of_this):
        "Convert a list of tuples (offset, obj) into the expected Series version."
        post_data = []
        post_offsets = []
        for each_obj in of_this:
            post_data.append(unicode(each_obj[1]))
            post_offsets.append(each_obj[0])
        return pandas.Series(post_data, index=post_offsets)

    def test_interval_indexer_1(self):
        # BWV7.7: soprano and bass parts
        test_parts = [self.bwv77_soprano, self.bwv77_bass]
        expected = TestIntervalIndexerLong.bwv77_S_B_basis
        setts = {u'simple or compound': u'compound', u'quality': True}
        int_indexer = IntervalIndexer(test_parts, setts)
        actual = int_indexer.run()[u'[0, 1]']
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])

    def test_interval_indexer_1_mpc(self):
        # BWV7.7: soprano and bass parts with MPController
        test_parts = [self.bwv77_soprano, self.bwv77_bass]
        expected = TestIntervalIndexerLong.bwv77_S_B_basis
        setts = {u'simple or compound': u'compound', u'quality': True}
        mpc = mpcontroller.MPController()
        mpc.start()
        int_indexer = IntervalIndexer(test_parts, setts, mpc)
        actual = int_indexer.run()[u'[0, 1]']
        del int_indexer
        mpc.shutdown()
        self.assertEqual(len(expected), len(actual))
        for i, ind in enumerate(list(actual.index)):
            self.assertEqual(expected[i][0], ind)
            self.assertEqual(expected[i][1], actual[ind])


class TestIntervalIndexerIndexer(unittest.TestCase):
    def test_int_ind_indexer_1(self):
        # ascending simple: quality, simple
        notes = [u'E4', u'C4']
        expected = u'M3'
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_2(self):
        # ascending simple: quality, compound
        notes = [u'E4', u'C4']
        expected = u'M3'
        actual = real_indexer(notes, qual=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_3(self):
        # ascending simple: noQuality, simple
        notes = [u'E4', u'C4']
        expected = u'3'
        actual = real_indexer(notes, qual=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_4(self):
        # ascending simple: noQuality, compound
        notes = [u'E4', u'C4']
        expected = u'3'
        actual = real_indexer(notes, qual=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_5(self):
        # ascending compound: quality, simple
        notes = [u'E5', u'C4']
        expected = u'M3'
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_6(self):
        # ascending compound: quality, compound
        notes = [u'E5', u'C4']
        expected = u'M10'
        actual = real_indexer(notes, qual=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_7(self):
        # ascending compound: noQuality, simple
        notes = [u'E5', u'C4']
        expected = u'3'
        actual = real_indexer(notes, qual=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_8(self):
        # ascending compound: noQuality, compound
        notes = [u'E5', u'C4']
        expected = u'10'
        actual = real_indexer(notes, qual=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_9(self):
        # descending simple: quality, simple
        notes = [u'C4', u'E4']
        expected = u'-M3'
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_10(self):
        # descending simple: quality, compound
        notes = [u'C4', u'E4']
        expected = u'-M3'
        actual = real_indexer(notes, qual=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_11(self):
        # descending simple: noQuality, simple
        notes = [u'C4', u'E4']
        expected = u'-3'
        actual = real_indexer(notes, qual=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_12(self):
        # descending simple: noQuality, compound
        notes = [u'C4', u'E4']
        expected = u'-3'
        actual = real_indexer(notes, qual=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_13(self):
        # descending compound: quality, simple
        notes = [u'C4', u'E5']
        expected = u'-M3'
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_14(self):
        # descending compound: quality, compound
        notes = [u'C4', u'E5']
        expected = u'-M10'
        actual = real_indexer(notes, qual=True, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_15(self):
        # descending compound: noQuality, simple
        notes = [u'C4', u'E5']
        expected = u'-3'
        actual = real_indexer(notes, qual=False, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_16(self):
        # descending compound: noQuality, compound
        notes = [u'C4', u'E5']
        expected = u'-10'
        actual = real_indexer(notes, qual=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_17(self):
        # rest in upper part
        notes = [u'C4', u'Rest']
        expected = u'Rest'
        actual = real_indexer(notes, qual=False, simple=False)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_18(self):
        # rest in lower part
        notes = [u'Rest', u'C4']
        expected = u'Rest'
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_19(self):
        # triple augmented ascending
        notes = [u'G###4', u'C4']
        expected = u'AAA5'
        actual = real_indexer(notes, qual=True, simple=False)
        self.assertEqual(expected, actual)
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_20(self):
        # triple diminished descending
        notes = [u'C###4', u'G4']
        expected = u'-ddd5'
        actual = real_indexer(notes, qual=True, simple=False)
        self.assertEqual(expected, actual)
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_21(self):
        # too few inputs
        notes = [u'C4']
        expected = None
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)

    def test_int_ind_indexer_22(self):
        # too many inputs
        notes = [u'C4', u'D4', u'E4']
        expected = None
        actual = real_indexer(notes, qual=True, simple=True)
        self.assertEqual(expected, actual)


#--------------------------------------------------------------------------------------------------#
# Definitions                                                                                      #
#--------------------------------------------------------------------------------------------------#
interval_indexer_short_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerShort)
interval_indexer_long_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerLong)
int_ind_indexer_suite = unittest.TestLoader().loadTestsFromTestCase(TestIntervalIndexerIndexer)
