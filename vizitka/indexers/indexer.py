#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               controllers/indexer.py
# Purpose:                Help with indexing data from musical scores.
#
# Copyright (C) 2013-15, 2018 Christopher Antila, Jamie Klassen, and Alexander Morgan
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
.. codeauthor:: Christopher Antila <christopher@antila.ca>
.. codeauthor:: Jamie Klassen <michigan.j.frog@gmail.com>
.. codeauthor:: Alexander Morgan

The controllers that deal with indexing data from music21 Score objects.
"""

import pandas
from music21 import stream

class Indexer(object):
    """
    An object that manages creating an index of a piece, or part of a piece, based on one feature.

    Use the :attr:`required_score_type` attribute to know what type of object is required in
    :meth:`__init__`.

    The name of the indexer, as stored in the :class:`DataFrame` it returns, is the module name and
    class name. For example, the name of the :class:`~vis.analyzers.indexers.interval.IntervalIndexer`
    is ``'interval.IntervalIndexer'``.

    .. caution::
        This module underwent significant changes for  release 2.0.0. In particular, the
        constructor's ``score`` argument and the :meth:`run` method's return type have changed.
    """
    # just the standard instance variables
    required_score_type = None
    possible_settings = {}
    default_settings = {}
    # self._score  # this will hold the input data
    # self._indexer_func  # this function will do the indexing
    # self._types  # if the input is a Score, this is a list of types we'll use for the index

    # In subclasses, we might get these values for required_score_type. The superclass here will
    # "convert" them into the actual type.
    _TYPE_CONVERTER = {'stream.Part': stream.Part,
                       'stream.Score': stream.Score,
                       'pandas.Series': pandas.Series,
                       'pandas.DataFrame': pandas.DataFrame}

    # Error messages
    _MAKE_RETURN_INDEX_ERR = 'Indexer.make_return(): arguments must have the same legnth.'
    _INIT_KEY_ERR = '{} has an incorrectly-set "required_score_type"'
    _INIT_INDEX_ERR = 'Indexer: got a DataFrame but expected a Series; problem with the MultiIndex'
    _INIT_TYPE_ERR = '{} requires "{}" objects'

    # Ignore that we don't use the "settings" argument in this method. Subclasses handle it.
    # pylint: disable=W0613
    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index. Each indexer will specify its
            required input type, of which there will be one. Also refer to the note below.
        :type score: :class:`pandas.DataFrame`, :class:`music21.stream.Score`, or list of \
            :class:`pandas.Series` or of :class:`music21.stream.Part`
        :param settings: A dict of all the settings required by this :class:`Indexer`. All required
            settings should be listed in subclasses. Default is ``None``.
        :type settings: dict or None

        :raises: :exc:`TypeError` if the ``score`` argument is the wrong type.
        :raises: :exc:`RuntimeError` if the required settings are not present in the ``settings``
            argument.
        :raises: :exc:`IndexError` if ``required_score_type`` is ``'pandas.Series'`` and the
            ``score`` argument is an improperly-formatted :class:`DataFrame` (e.g., it contains the
            results of more than one indexer, or the columns do not have a :class:`MultiIndex`).

        .. note:: **About the "score" Parameter:**

            A two-dimensional type, :class:`DataFrame` or :class:`Score`, can be provided to an
            indexer that otherwise requires a list of the corresponding single-dimensional type
            (being :class:`Series` or :class:`Part`, respectively).

            When a :class:`Part`-requiring indexer is given a :class:`Score`, the call to the
            :class:`Indexer` superclass constructor (i.e., this method) will use the
            :attr:`~music21.stream.Score.parts` attribute to get a list of :class:`Part` objects.

            When a :class:`Series`-requiring indexer is given a :class:`DataFrame`, the call to the
            :class:`Indexer` superclass constructor (i.e., this method) exepcts a :class:`DataFrame`
            in the style outputted by :meth:`run`. In other words, the columns must have a
            :class:`pandas.MultiIndex` where the first level is the name of the indexer class that
            produced the results and the second level is the name of the part or part combination
            that produced those results. In this case, the :class:`DataFrame` *must* contain the
            results of only one indexer.

            Also in the last case, any ``NaN`` values are "dropped" with :meth:`~pandas.Series.dropna`.
            The ``NaN`` values would have been introduced as the part (or part combination) was
            re-indexed when being added to the :class:`DataFrame`, and they're only relevant when
            considering all the parts at once.
        """
        # check the required_score_type is valid
        try:
            req_s_type = Indexer._TYPE_CONVERTER[self.required_score_type]
        except KeyError:
            raise TypeError(Indexer._INIT_KEY_ERR.format(self.__class__))
        # if "score" is a list, check it's of the right type
        if isinstance(score, list) and (req_s_type in (pandas.DataFrame, pandas.Series, stream.Part)):
            if not all([isinstance(e, req_s_type) for e in score]):
                raise TypeError(Indexer._INIT_TYPE_ERR.format(self.__class__,
                                                             self.required_score_type))
        elif isinstance(score, pandas.DataFrame) and req_s_type is pandas.Series:
            if (not isinstance(score.columns, pandas.MultiIndex)) or 1 != len(score.columns.levels[0]):
                raise IndexError(Indexer._INIT_INDEX_ERR)
            else:
                ind_name = score.columns.levels[0][0]
                score = [score.iloc[:, x].dropna() for x in range(len(score.columns))]
        elif isinstance(score, stream.Score) and req_s_type is stream.Part:
            score = [score.parts[i] for i in range(len(score.parts))]

        # Call our superclass constructor, then set instance variables
        super(Indexer, self).__init__()
        self._score = score
        self._indexer_func = None
        self._types = None
        if hasattr(self, '_settings'):
            if self._settings is None:
                self._settings = {}
        else:
            self._settings = {}

    def run(self):
        """
        Make a new index of the piece.

        :returns: The new indices. Refer to the section below.
        :rtype: :class:`pandas.DataFrame`

        **About Return Values:**

        Every indexer must return a :class:`DataFrame` with a special kind of :class:`MultiIndex`
        that helps organize data across multiple indexers.

        Indexers return a :class:`DataFrame` where the columns are indexed on two levels: the first
        level is a string with the name of the indexer, and the second level is a string with the
        index of the part, the indices of the parts in a combination, or some other value as
        specified by the indexer.

        This allows, for example:

        >>> the_score = music21.converter.parse('sibelius_5-i.mei')
        >>> the_score.parts[5]
        (the first clarinet Part)
        >>> the_notes = NoteRestIndexer(the_score).run()
        >>> the_notes['noterest.NoteRestIndexer']['5']
        (the first clarinet Series)
        >>> the_intervals = IntervalIndexer(the_notes).run()
        >>> the_intervals['interval.IntervalIndexer']['5,6']
        (Series with vertical intervals between first and second clarinet)

        """
        # This if statement is necessary because of a pandas bug, see pandas issue #8222.
        if len(self._score.index) == 0: # If parts have no note, rest, or chord events in them
            result = self._score.copy()
        else: # This is the regular case.
            result = self._score.applymap(self._indexer_func)
        if type(self._score.columns) == pandas.Index:
            labels = self._score.columns
        else:
            labels = self._score.columns.get_level_values(-1)
        return self.make_return(labels, result)


    def make_return(self, labels, indices):
        """
        Prepare a properly-formatted :class:`DataFrame` as should be returned by any :class:`Indexer`
        subclass. We intend for this to be called by :class:`Indexer` subclasses only.

        The index of a label in ``labels`` should be the same as the index of the :class:`Series`
        to which it corresponds in ``indices``. For example, if ``indices[12]`` is the tuba part,
        then ``labels[12]`` might say ``'Tuba'``.

        :param labels: Indices of the parts or the part combinations, or another descriptive label
            as described in the indexer subclass documentation.
        :type labels: list of strings
        :param indices: The results of the indexer.
        :type indices: list of :class:`pandas.Series` or a :class:`pandas.DataFrame`

        :returns: A :class:`DataFrame` with the appropriate :class:`~pandas.MultiIndex` required
            by the :meth:`Indexer.run` method signature.
        :rtype: :class:`pandas.DataFrame`

        :raises: :exc:`IndexError` if the number of labels and indices does not match.
        """
        if isinstance(indices, pandas.DataFrame):
            ret = indices
        else:
            if len(labels) != len(indices):
                raise IndexError(Indexer._MAKE_RETURN_INDEX_ERR)
            # the levels argument is necessary below even though it just gets written over by the
            # multi_index because it ensures that even empty series will be included in the dataframe.
            ret = pandas.concat(indices, levels=labels, axis=1)

        # just use the name of the indexer without the word "Indexer"
        name = str(self.__class__).rsplit('.', 1)[-1][0:-9]

        # Apply the multi_index as the column labels.
        iterables = ((name,), labels)
        multi_index = pandas.MultiIndex.from_product(iterables, names=('Indexer', 'Part'))
        ret.columns = multi_index

        return ret
