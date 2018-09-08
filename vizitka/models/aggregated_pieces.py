#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/aggregated_pieces.py
# Purpose:                Hold the model representing data from multiple IndexedPieces.
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Alexander Morgan
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
.. codeauthor:: Alexander Morgan
The model representing data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
"""

import sys
import os
import pandas


class AggregatedPieces(object):
    """
    Hold data from multiple :class:`~vis.models.indexed_piece.IndexedPiece` instances.
    """

    # When get() is called but _pieces is still an empty list.
    _NO_PIECES = 'This aggregated_pieces object has no pieces assigned to it. This probably means \
that this aggregated_pieces object was instantiated incorrectly. Please refer to the documentation \
on the Importer() method in vis.models.indexed_piece.'

    # When a directory has no files in it.
    _NO_FILES = 'There are no files in the directory provided.'

    # When get() is missing the "settings" and/or data" argument but needed them, or was supplied .
    _SUPERFLUOUS_OR_INSUFFICIENT_ARGUMENTS = 'You made improper use of the settings and/or data \
arguments. Please refer to the {} documentation to see what it requires.'


    # When metadata() gets a 'field' argument that isn't a string
    _FIELD_STRING = "parameter 'field' must be of type 'string'"

    _UNKNOWN_INPUT = "The input type is not one of the supported options"

    class Metadata(object):
        """
        Used internally by :class:`AggregatedPieces` ... at least for now.
        Hold aggregated metadata about the IndexedPieces in an AggregatedPiece. Every list has no
        duplicate entries.
        - composers: list of all the composers in the IndexedPieces
        - dates: list of all the dates in the IndexedPieces
        - date_range: 2-tuple with the earliest and latest dates in the IndexedPieces
        - titles: list of all the titles in the IndexedPieces
        - locales: list of all the locales in the IndexedPieces
        - pathnames: list of all the pathnames in the IndexedPieces
        """
        __slots__ = ('composers', 'dates', 'date_range', 'titles', 'locales', 'pathnames')

    def __init__(self, pieces=None, metafile=None):
        """
        :param pieces: The IndexedPieces to collect.
        :type pieces: list of :class:`~vis.models.indexed_piece.IndexedPiece`
        """
        def init_metadata():
            """
            Initialize valid metadata fields with a zero-length string.
            """
            field_list = ['composers', 'dates', 'date_range', 'titles', 'locales',
                          'pathnames']
            for field in field_list:
                self._metadata[field] = None

        super(AggregatedPieces, self).__init__()
        self._pieces = pieces if pieces is not None else []
        self._metafile = metafile if metafile is not None else []
        self._metadata = {}
        init_metadata()


    @staticmethod
    def _make_date_range(dates):
        """
        Find the earliest and latest years in a list of music21 date strings.
        Each string should use one of the following two formats:
        - "----/--/--"
        - "----/--/-- to ----/--/--"
        where each - is an integer.
        :param dates: The date strings to use.
        :type dates: list of basesetring
        :returns: The earliest and latest years in the list of dates.
        :rtype: 2-tuple of string
        **Examples**
        >>> ranges = ['1987/09/09', '1865/12/08', '1993/08/08']
        >>> AggregatedPieces._make_date_range(ranges)
        ('1865', '1993')
        """
        post = []
        for poss_date in dates:
            if len(poss_date) > len('----/--/--'):
                # it's a date range, so we have "----/--/-- to ----/--/--"
                try:
                    post.append(int(poss_date[:4]))
                    post.append(int(poss_date[14:18]))
                except ValueError:
                    pass
            elif isinstance(poss_date, str):
                try:
                    post.append(int(poss_date[:4]))
                except ValueError:
                    pass
        if [] != post:
            return str(min(post)), str(max(post))
        else:
            return None

    def _fetch_metadata(self, field):
        """
        Collect metadata from the IndexedPieces and store it in our own Metadata object.
        :param field: The metadata field to return
        :type field: str
        :returns: The requested metadata field.
        :rtype: list of str or tuple of str
        """
        post = None
        # composers: list of all the composers in the IndexedPieces
        if 'composers' == field:
            post = [p.metadata('composer') for p in self._pieces]
        # dates: list of all the dates in the IndexedPieces
        elif 'dates' == field:
            post = [p.metadata('date') for p in self._pieces]
        # date_range: 2-tuple with the earliest and latest dates in the IndexedPieces
        elif 'date_range' == field:
            post = AggregatedPieces._make_date_range([p.metadata('date') for p in self._pieces])
        # titles: list of all the titles in the IndexedPieces
        elif 'titles' == field:
            post = [p.metadata('title') for p in self._pieces]
        # locales: list of all the locales in the IndexedPieces
        elif 'locales' == field:
            post = [p.metadata('locale_of_composition') for p in self._pieces]
        elif 'pathnames' == field:
            post = [p._pathname for p in self._pieces]
        if post is not None:
            self._metadata[field] = post
        return post

    def metadata(self, field):
        """
        Get a metadatum about the IndexedPieces stored in this AggregatedPieces.
        If only some of the stored IndexedPieces have had their metadata initialized, this method
        returns incompelete metadata. Missing data will be represented as ``None`` in the list,
        but it will not appear in ``date_range`` unless there are no dates. If you need full
        metadata, we recommend running an Indexer that requires a :class:`Score` object on all the
        IndexedPieces (like :class:`vis.analyzers.indexers.noterest.NoteRestIndexer`).
        Valid fields are:
        * ``'composers``: list of all the composers in the IndexedPieces
        * ``'dates``: list of all the dates in the IndexedPieces
        * ``'date_range``: 2-tuple with the earliest and latest dates in the IndexedPieces
        * ``'titles``: list of all the titles in the IndexedPieces
        * ``'locales``: list of all the locales in the IndexedPieces
        * ``'pathnames``: list of all the pathnames in the IndexedPieces
        :param field: The name of the field to be accessed or modified.
        :type field: str
        :returns: The value of the requested field or None, if accessing a non-existant field or a
            field that has not yet been initialized in the IndexedPieces.
        :rtype: object or None
        :raises: :exc:`TypeError` if ``field`` is not a str.
        """
        if not isinstance(field, str):
            raise TypeError(AggregatedPieces._FIELD_STRING)
        elif field in self._metadata:
            if self._metadata[field] is None:
                return self._fetch_metadata(field)
            else:
                return self._metadata[field]
        else:
            return None

    def get(self, ind_analyzer=None, settings=None, data=None):
        """
        Get the results of an :class:`Indexer` run on all the
        :class:`IndexedPiece` objects either individually, or all together. If
        settings are provided, the same settings dict will be used throughout.

        Indexers  associate observations with a specific moment in a piece.

        **Examples**

        .. note:: The analyzers in the ``analyzer_cls`` argument are run with
            :meth:`~vis.models.indexed_piece.IndexedPiece.get` from the :class:`IndexedPiece`
            objects themselves. Thus any exceptions raised there may also be raised here.
        Get the results of an Indexer run on this :class:`IndexedPiece`.

        :param ind_analyzer: The analyzer to run.
        :type ind_analyzer: str or VizitkaIndexer.
        :param settings: Settings to be used with the analyzer. Only use if necessary.
        :type settings: dict
        :param data: Input data for the analyzer to run. If this is provided for an indexer that
            normally caches its results (such as the NoteRestIndexer, the DurationIndexer, etc.),
            the results will not be cached since it is uncertain if the input passed in the ``data``
            argument was calculated on this indexed_piece.
        :type data: Depends on the requirement of the analyzer designated by the ``analyzer_cls``
            argument. Usually a list of :class:`pandas.DataFrame`.
        :returns: Results of the analyzer.
        :rtype: Depending on the ``analyzer_cls``, either a :class:`pandas.DataFrame` or more often
            a list of :class:`pandas.DataFrame`.
        :return: Either one :class:`pandas.DataFrame` with all experimental results or a list of
            :class:`DataFrame` objects, each with the experimental results for one piece.
        :raises: :exc:`TypeError` if an analyzer is invalid or cannot be found.
        """
        if not self._pieces: # if there are no pieces in this aggregated_pieces object
            raise RuntimeWarning(AggregatedPieces._NO_PIECES)

        args_dict = {} # Only pass the settings argument if it is not ``None``.
        if settings is not None:
            args_dict['settings'] = settings

        if ind_analyzer is not None: # for indexers run individually on each indexed_piece in self._pieces
            if data is None:
                results = [p.get(ind_analyzer, **args_dict) for p in self._pieces]
            else:
                results = [p.get(ind_analyzer, data[i], **args_dict) for i, p in enumerate(self._pieces)]

        return results
