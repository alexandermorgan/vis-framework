#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/indexed_piece.py
# Purpose:                Hold the model representing an indexed and analyzed piece of music.
#
# Copyright (C) 2013, 2014, 2016 Christopher Antila, Jamie Klassen, Alexander Morgan
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
.. codeauthor:: Jamie Klassen <michigan.j.frog@gmail.com>
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>
.. codeauthor:: Alexander Morgan
This model represents an indexed and analyzed piece of music.
"""

# Imports
import os
import music21
import music21.chord as chord
import pandas
import numpy
from music21 import converter, stream, analysis
from vizitka.models.aggregated_pieces import AggregatedPieces
from vizitka.indexers.indexer import Indexer
from vizitka.indexers import noterest, output, staff, lyric, approach, articulation, meter, interval, dissonance, expression, offset, repeat, active_voices, offset, over_bass, contour, ngram
from collections import Counter
import pdb

# Error message when importing doesn't work because of unknown file type
_UNKNOWN_INPUT = 'This file type was not recognized. The file is probably not \
a score in symbolic notation.'
# the title given to a piece when we cannot determine its title
_UNKNOWN_PIECE_TITLE = 'Unknown Piece'
# Types for noterest indexing
_noterest_types = ('Note', 'Rest', 'Chord')
_default_interval_setts = {'quality':True, 'directed':True, 'simple or compound':'compound', 'horiz_attach_later':True}

def _find_piece_title(the_score):
    """
    Find the title of a score. If there is none, return the filename without an extension.
    :param the_score: The score of which to find the title.
    :type the_score: :class:`music21.stream.Score`
    :returns: The title of the score.
    :rtype: str
    """
    # First try to get the title from a Metadata object, but if it doesn't
    # exist, use the filename without directory.
    if the_score.metadata is not None:
        post = the_score.metadata.title
    elif hasattr(the_score, 'filePath'):
        post = os.path.basename(the_score.filePath)
    else:  # if the Score was part of an Opus
        post = _UNKNOWN_PIECE_TITLE

    # Now check that there is no file extension. This could happen either if
    # we used the filename or if music21 did a less-than-great job at the
    # Metadata object.
    # TODO: test this "if" stuff
    if not isinstance(post, str):  # uh-oh
        try:
            post = str(post)
        except UnicodeEncodeError:
            _UNKNOWN_PIECE_TITLE
    post = os.path.splitext(post)[0]

    return post


def _find_part_names(list_of_parts):
    """
    Return a list of part names in a score. If the score does not have proper
    part names, return a list of enumerated parts.
    :param list_of_parts: The parts of the score.
    :type list_of_parts: List of :class:`music21.stream.Part`
    :returns: List of part names.
    :rtype: :obj:`list` of str
    """
    # hold the list of part names
    post = []

    # First try to find Instrument objects. If that doesn't work, use the "id"
    for i, each_part in enumerate(list_of_parts):
        name = 'None'
        instr = each_part.getInstrument()
        if instr is not None and instr.partName != '' and instr.partName is not None:
            name = instr.partName
        elif each_part.id is not None:
            if isinstance(each_part.id, str):
                # part ID is a string, so that's what we were hoping for
                name = each_part.id
        # Make sure none of the part names are just 'None'.
        if name == 'None' or name == '':
            name = 'Part {}'.format(i + 1)
        post.append(name)

    # If there are duplicates, add enumerated suffixes.
    counts = {k:v for k,v in Counter(post).items() if v > 1}
    for i in reversed(range(len(post))):
        item = post[i]
        if item in counts and counts[item]:
            post[i] = ''.join((post[i], '_', str(counts[item])))
            counts[item] -= 1

    return post

def _get_offsets(event, part):
    """This method finds the offset of a music21 event. There are other ways to get the offset of a
    music21 object, but this is the fastest and most reliable.

    :param event: music21 object contained in a music21 part stream.
    :param part: music21 part stream.
    """
    for y in event.contextSites():
        if y[0] is part:
            return float(y[1])

def _eliminate_ties(event):
    """Gets rid of the notes and rests that have non-start ties. This is used internally for
    noterest and beatstrength indexing."""
    if hasattr(event, 'tie') and event.tie is not None and event.tie.type != 'start':
        return float('nan')
    return event

def _type_func_noterest(event):
    """Used internally by _get_m21_nrc_objs() to filter for just the 'Note', 'Rest', and 'Chord'
    objects in a piece."""
    if any([typ in event.classes for typ in _noterest_types]):
        return event
    return float('nan')

def _type_func_measure(event):
    """Used internally by _get_m21_measure_objs() to filter for just the 'Measure' objects in a
    piece."""
    if 'Measure' in event.classes:
        return event
    return float('nan')

def _type_func_voice(event):
    """Used internally by _combine_voices() to filter for just the 'Voice' objects in a part."""
    if 'Voice' in event.classes:
        return event
    return float('nan')

def _get_pitches(event):
    """Used internally by _combine_voices() to represent all the note and chord objects of a part as
    music21 pitches. Rests get discarded in this stage, but later re-instated with
    _reinsert_rests()."""
    if isinstance(event, float):
        return event
    elif event.isNote:
        return (music21.pitch.Pitch(event.nameWithOctave),)
    elif event.isRest:
        return float('nan')
    else: # The event is a chord
        return event.pitches

def _reinsert_rests(event):
    """Used internally by _combine_voices() to put rests back into its intermediate representation
    of a piece which had to temporarily remove the rests."""
    if isinstance(event, float):
        return music21.note.Rest()
    return event

def _combine_voices(ser, part):
    """Used internally by _get_m21_nrc_objs() to combine the voices of a single part into one
    pandas.Series of music21 chord objects."""
    temp = []
    indecies = [0]
    voices = part.apply(_type_func_voice).dropna()
    if len(voices.index) < 1:
        return ser
    for voice in voices:
        indecies.append(len(voice) + indecies[-1])
        temp.append(ser.iloc[indecies[-2] : indecies[-1]])
    # Put each voice in separate columns in a dataframe.
    df = pandas.concat(temp, axis=1).applymap(_get_pitches)
    # Condense the voices (df's columns) into chord objects in a series.
    res = df.apply(lambda x: chord.Chord(sorted([pitch for lyst in x.dropna() for pitch in lyst], reverse=True)), axis=1)
    # Note that if a part has two voices, and one voice has a note or a chord, and the other a rest,
    # only the rest will be lost even after calling _reinsert_rests().
    return res.apply(_reinsert_rests)

def _attach_before(df):
    """Used internally by _get_horizontal_interval() to change the index values of the cached
    results of the interval.HorizontalIntervalIndexer so that they start on 0.0 instead of whatever
    value they start on. This shift makes the index values correspond to the first of two notes in
    a horizontal interval in any given voice rather than that of the second."""
    re_indexed = []
    for x in range(len(df.columns)):
        ser = df.iloc[:, x].dropna()
        ser.index = numpy.insert(ser.index, 0, 0.0)[:-1]
        re_indexed.append(ser)
    return pandas.concat(re_indexed, axis=1)

def _find_piece_range(the_score):

    p = analysis.discrete.Ambitus()
    p_range = p.getPitchSpan(the_score)

    if p_range is None:
        return (None, None)
    else:
        return (p_range[0].nameWithOctave, p_range[1].nameWithOctave)


def _find_part_ranges(the_score):

    ranges = []
    for x in range(len(the_score.parts)):
        p = analysis.discrete.Ambitus()
        p_range = p.getPitchSpan(the_score.parts[x])
        if p_range is None:
            ranges.append((None, None))
        else:
            ranges.append((p_range[0].nameWithOctave, p_range[1].nameWithOctave))

    return ranges

def _import_file(pathname, metafile=None):
    """
    Import the score to music21 format.
    :param pathname: Location of the file to import on the local disk.
    :type pathname: str
    :returns: A 1-tuple of :class:`IndexedPiece` if the file imported as a
        :class:`music21.stream.Score` object or a multi-element list if it imported as a
        :class:`music21.stream.Opus` object.
        respectively.
    :rtype: 1-tuple or list of :class:`IndexedPiece`
    """
    score = converter.Converter()
    score.parseFile(pathname, forceSource=True, storePickle=False)
    score = score.stream
    if isinstance(score, stream.Opus):
        # make an AggregatedPieces object containing IndexedPiece objects of each movement of the opus.
        score = [IndexedPiece(pathname, opus_id=i) for i in xrange(len(score))]
    elif isinstance(score, stream.Score):
        score = (IndexedPiece(pathname, score=score),)
    for ip in score:
        for field in ip._metadata:
            if hasattr(ip.metadata, field):
                ip._metadata[field] = getattr(ip.metadata, field)
                if ip._metadata[field] is None:
                    ip._metadata[field] = '???'
        ip._metadata['parts'] = _find_part_names(ip._get_part_streams())
        ip._metadata['title'] = _find_piece_title(ip._score)
        ip._metadata['partRanges'] = _find_part_ranges(ip._score)
        ip._metadata['pieceRange'] = _find_piece_range(ip._score)
        ip._imported = True

    return score

def _import_directory(directory, metafile=None):

    pieces = [] # a list of the pieces being imported
    meta = metafile

    if isinstance(directory, list):
        file_paths = directory

    else: # the `directory` argument is the pathname of a directory
        file_paths = []
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f == '.DS_Store': # exclude ds_stores
                    continue
                if len(f) > 1 and f[:2] == '._': # filter out hidden files if they show up
                    continue
                if f == 'meta': # attach meta files if they exist
                    meta = root + '/meta'
                    continue
                file_paths.append('/'.join((root, f)))

    if not file_paths:
        raise RuntimeError(vis.models.aggregated_piece.AggregatedPieces._NO_FILES)

    for path in file_paths:
        # use extend rather than append because it could import as a multi-movement opus
        pieces.extend(_import_file(pathname=path, metafile=meta))

    return (pieces, meta)

def Importer(location, metafile=None):
    """
    Import the file, website link, or directory of files designated by ``location`` to music21
    format.

    :param location: Location of the file to import on the local disk.
    :type location: str
    :returns: An :class:`IndexedPiece` or an :class:`AggregatedPieces` object if the file passed
        imports as a :class:`music21.stream.Score` or :class:`music21.stream.Opus` object
        respectively.
    :rtype: A new :class:`IndexedPiece` or :class:`AggregatedPieces` object.
    """
    pieces = []

    # load directory of pieces
    if isinstance(location, list) or os.path.isdir(location):
        directory_return = _import_directory(location, metafile)
        pieces.extend(directory_return[0])
        metafile = directory_return[1]

    # index piece if it is a file or a link
    elif os.path.isfile(location):
        pieces.extend(_import_file(location))

    else:
        raise RuntimeError(_UNKNOWN_INPUT)

    if len(pieces) == 1: # there was a single piece that imported as a score (not an opus)
        return(pieces[0]) # this returns an IndexedPiece object
    else: # there were multiple pieces or a single piece that imported as an opus
        return(AggregatedPieces(pieces=pieces, metafile=metafile))


class IndexedPiece(object):
    """
    Hold indexed data from a musical score, and the score itself. IndexedPiece objects are VIS's
    basic representations of a piece of music and also a container for metadata and analyses about
    that piece. An IndexedPiece object should be created by passing the pathname of a symbolic
    notation file to the Importer() method in this file. The Importer() will return an IndexedPiece
    object as long as the piece did not import as an opus. In this case Importer() will return an
    AggregatedPieces object. Information about an IndexedPiece object from an indexer should be
    requested via the get() method. If you want to access the full
    music21 score object of a VizitkaIndexedPiece object, access the _score attribute of the
    IndexedPiece object. See the examples below:

    **Examples**
    # Create an IndexedPiece object
    from vizitka.models.indexed_piece import Importer
    ip = Importer('path_to_file.xml')

    # Get the results of an indexer (noterest and dissonance indexers shown)
    noterest_results = ip.get('noterest')
    dissonance_results = ip.get('dissonance')

    # Access the full music21 score object of the file
    ip._score
    """

    # When get() is missing the "settings" and/or data" argument but needed them, or was
    # supplied this information, but couldn't use it.
    _SUPERFLUOUS_OR_INSUFFICIENT_ARGUMENTS = 'You made improper use of the settings and/or data \
arguments. Please refer to the {} documentation to see what is required by the Indexer or \
requested.'

    # When get() gets an analysis_cls argument that isn't a key in IndexedPiece._indexers.
    _NOT_AN_ANALYZER = 'Could not recognize the requested Indexer (received {}). \
When using IndexedPiece.get(), please use one of the following short- or long-format \
strings to identify the desired Indexer: {}.'

    # When measure_index() is run on a piece with no measure information.
    _NO_MEASURES = 'There are no measures in this piece.'

    # When measure_index() is passed something other than a dataframe.
    _NOT_DATAFRAME = 'The passed argument must be a pandas.DataFrame and cannot be empty.'

    # When metadata() gets an invalid field name
    _INVALID_FIELD = 'metadata(): invalid field ({})'

    # When metadata()'s "field" is not a string
    _META_INVALID_TYPE = "metadata(): parameter 'field' must be of type 'string'"

    _MISSING_USERNAME = ('You must enter a username to access the elvis database')
    _MISSING_PASSWORD = ('You must enter a password to access the elvis database')
    def __init__(self, pathname='', opus_id=None, score=None, metafile=None, username=None, password=None):
        """
        :param str pathname: Pathname to the file music21 will import for this :class:`IndexedPiece`.
        :param opus_id: The index of the :class:`Score` for this :class:`IndexedPiece`, if the file
            imports as a :class:`music21.stream.Opus`.
        :returns: A new :class:`IndexedPiece`.
        :rtype: :class:`IndexedPiece`
        """

        def init_metadata():
            """
            Initialize valid metadata fields with a zero-length string.
            """
            field_list = ['opusNumber', 'movementName', 'composer',
                'movementNumber', 'date', 'composers', 'alternativeTitle', 'title',
                'localeOfComposition', 'parts']
            for field in field_list:
                self._metadata[field] = ''
            self._metadata['pathname'] = pathname

        super(IndexedPiece, self).__init__()
        self._imported = False
        self._analyses = {}
        self._score = score
        self._pathname = pathname
        self._metadata = {}
        self._known_opus = False
        self._opus_id = opus_id  # if the file imports as an Opus, this is the index of the Score
        self._username = username
        self._password = password
        # Dictionary of indexers and their shorts for calls to get()
        self._indexers = { # Indexers :
            'av': self._get_active_voices,
            'active_voices': self._get_active_voices,
            'ap': self._get_approach,
            'approach': self._get_approach,
            'ar': self._get_articulation,
            'articulation': self._get_articulation,
            'cl': self._get_clef,
            'clef': self._get_clef,
            'co': contour.ContourIndexer,
            'contour': contour.ContourIndexer,
            'di': self._get_dissonance,
            'dissonance': self._get_dissonance,
            'ex': self._get_expression,
            'expression': self._get_expression,
            'ly': self._get_lyric,
            'lyric': self._get_lyric,
            'hi': self._get_horizontal_interval,
            'horizontal_interval': self._get_horizontal_interval,
            'ks': self._get_key_signature,
            'key_signature': self._get_key_signature,
            'vi': self._get_vertical_interval,
            'vertical_interval': self._get_vertical_interval,
            'du': self._get_duration,
            'duration': self._get_duration,
            'me': self._get_measure,
            'measure': self._get_measure,
            'bs': self._get_beat_strength,
            'beat_strength': self._get_beat_strength,
            'ti': self._get_tie,
            'tie': self._get_tie,
            'ts': self._get_time_signature,
            'time_signature': self._get_time_signature,
            'ng': self._get_ngram,
            'ngram': self._get_ngram,
            'mu': self._get_multistop,
            'multistop': self._get_multistop,
            'nr': self._get_noterest,
            'noterest': self._get_noterest,
            'of': self._get_offset,
            'offset': self._get_offset,
            'ob': over_bass.OverBassIndexer,
            'over_bass': over_bass.OverBassIndexer,
            're': repeat.FilterByRepeatIndexer,
            'repeat': repeat.FilterByRepeatIndexer,
            'vh': self._get_viz2hum,
            'viz2hum': self._get_viz2hum,
            'xm': self._get_xml,
            'xml': self._get_xml,
            # 'mensuration': self._get_mensuration, # Not currently supported by m21 as of v. 5.3
    		}

        init_metadata()
        if metafile is not None:
            self._metafile = metafile
            self._open_file()
        self._opus_id = opus_id  # if the file imports as an Opus, this is the index of the Score

    def __repr__(self):
        return "vis.models.indexed_piece.IndexedPiece('{}')".format(self.metadata('pathname'))

    def __str__(self):
        post = []
        if self._imported:
            return '<IndexedPiece ({} by {})>'.format(self.metadata('title'), self.metadata('composer'))
        else:
            return '<IndexedPiece ({})>'.format(self.metadata('pathname'))

    def metadata(self, field, value=None):
        """
        Get or set metadata about the piece.
        .. note:: Some metadata fields may not be available for all pieces. The available metadata
            fields depend on the specific file imported. Unavailable fields return ``None``.
            We guarantee real values for ``pathname``, ``title``, and ``parts``.
        :param str field: The name of the field to be accessed or modified.
        :param value: If not ``None``, the value to be assigned to ``field``.
        :type value: object or ``None``
        :returns: The value of the requested field or ``None``, if assigning, or if accessing
            a non-existant field or a field that has not yet been initialized.
        :rtype: object or ``None`` (usually a string)
        :raises: :exc:`TypeError` if ``field`` is not a string.
        :raises: :exc:`AttributeError` if accessing an invalid ``field`` (see valid fields below).
        **Metadata Field Descriptions**
        All fields are taken directly from music21 unless otherwise noted.
        +---------------------+--------------------------------------------------------------------+
        | Metadata Field      | Description                                                        |
        +=====================+====================================================================+
        | alternativeTitle    | A possible alternate title for the piece; e.g. Bruckner's          |
        |                     | Symphony No. 8 in C minor is known as "The German Michael."        |
        +---------------------+--------------------------------------------------------------------+
        | composer            | The author of the piece.                                           |
        +---------------------+--------------------------------------------------------------------+
        | composers           | If the piece has multiple authors.                                 |
        +---------------------+--------------------------------------------------------------------+
        | date                | The date that the piece was composed or published.                 |
        +---------------------+--------------------------------------------------------------------+
        | localeOfComposition | Where the piece was composed.                                      |
        +---------------------+--------------------------------------------------------------------+
        | movementName        | If the piece is part of a larger work, the name of this            |
        |                     | subsection.                                                        |
        +---------------------+--------------------------------------------------------------------+
        | movementNumber      | If the piece is part of a larger work, the number of this          |
        |                     | subsection.                                                        |
        +---------------------+--------------------------------------------------------------------+
        | opusNumber          | Number assigned by the composer to the piece or a group            |
        |                     | containing it, to help with identification or cataloguing.         |
        +---------------------+--------------------------------------------------------------------+
        | parts               | A list of the parts names in a multi-voice work.                   |
        +---------------------+--------------------------------------------------------------------+
        | title               | The title of the piece. This is determined partially by music21.   |
        +---------------------+--------------------------------------------------------------------+
        **Examples**
        >>> piece = IndexedPiece('a_sibelius_symphony.mei')
        >>> piece.metadata('composer')
        'Jean Sibelius'
        >>> piece.metadata('date', 1919)
        >>> piece.metadata('date')
        1919
        >>> piece.metadata('parts')
        ['Flute 1'{'Flute 2'{'Oboe 1'{'Oboe 2'{'Clarinet 1'{'Clarinet 2', ... ]
        """
        if not isinstance(field, str):
            raise TypeError(IndexedPiece._META_INVALID_TYPE)
        elif field not in self._metadata:
            raise AttributeError(IndexedPiece._INVALID_FIELD.format(field))
        if value is None:
            return self._metadata[field]
        else:
            self._metadata[field] = value

    def _get_part_streams(self):
        """Returns a list of the part streams in this indexed_piece."""
        if 'part_streams' not in self._analyses:
            self._analyses['part_streams'] = self._score.parts
        return self._analyses['part_streams']

    def _get_m21_objs(self):
        """
        Return the all the music21 objects found in the piece. This is a list of pandas.Series
        where each series contains the events in one part. It is not concatenated into a
        dataframe at this stage because this step should be done after filtering for a certain
        type of event in order to get the proper index.

        This list of voices with their events can easily be turned into a dataframe of music21
        objects that can be filtered to contain, for example, just the note and rest objects.
        Filtered dataframes of music21 objects like this can then have an indexer_func applied
        to them all at once using df.applymap(indexer_func).

        :returns: All the objects found in the music21 voice streams. These streams are made
            into pandas.Series and collected in a list.
        :rtype: list of :class:`pandas.Series`
        """
        if 'm21_objs' not in self._analyses:
            # save the results as a list of series in the indexed_piece attributes
            sers =[]
            for i, p in enumerate(self._get_part_streams()):
                # NB: since we don't use ActiveSites, not restoring them is a minor speed-up. Also,
                # skipSelf will soon change its default to True in music21.
                ser = pandas.Series(p.recurse(restoreActiveSites=False, skipSelf=True),
                                    name=self.metadata('parts')[i])
                ser.index = ser.apply(_get_offsets, args=(p,))
                sers.append(ser)
            self._analyses['m21_objs'] = sers
        return self._analyses['m21_objs']

    def _get_m21_nrc_objs(self):
        """
        This method takes a list of pandas.Series of music21 objects in each part in a piece and
        filters them to reveal just the 'Note', 'Rest', and 'Chord' objects. It then aligns these
        events with their offsets, and returns a pandas dataframe where each column has the events
        of a single part.

        :returns: The note, rest, and chord music21 objects in each part of a piece, aligned with
            their offsets.
        :rtype: A pandas.DataFrame of music21 note, rest, and chord objects.
        """
        if 'm21_nrc_objs' not in self._analyses:
            # get rid of all m21 objects that aren't notes, rests, or chords in each part series
            sers = [s.apply(_type_func_noterest).dropna() for s in self._get_m21_objs()]
            for i, ser in enumerate(sers): # and index  the offsets
                if not ser.index.is_unique: # the index is often not unique if there is an embedded voice
                    sers[i] = _combine_voices(ser, self._get_m21_objs()[i])
                # if it's still not unique, it's probably because of quantization.
                # This is a somewhat brutal solution in that it wipes all notes
                # that have a zero duration.
                if not ser.index.is_unique:
                    temp = sers[i].apply(lambda x: x.quarterLength)
                    sers[i] = sers[i][temp > 0]
            self._analyses['m21_nrc_objs'] = pandas.concat(sers, axis=1)
        return self._analyses['m21_nrc_objs']

    def _get_m21_nrc_objs_no_tied(self):
        """Used internally by _get_noterest() and _get_multistop(). Returns a pandas dataframe where
        each column corresponds to one part in the score. Each part has the note, rest, and chord
        objects as the elements in its column as long as they don't have a non-start tie, otherwise
        they are omitted."""
        if 'm21_nrc_objs_no_tied' not in self._analyses:
           # This if statement is necessary because of a pandas bug, see pandas issue #8222.
            if len(self._get_m21_nrc_objs()) == 0: # If parts have no note, rest, or chord events in them
                self._analyses['m21_nrc_objs_no_tied'] = self._get_m21_nrc_objs()
            else: # This is the normal case.
                self._analyses['m21_nrc_objs_no_tied'] = self._get_m21_nrc_objs().applymap(_eliminate_ties).dropna(how='all')
        return self._analyses['m21_nrc_objs_no_tied']

    def _get_noterest(self):
        """Used internally by get() to cache and retrieve results from the
        noterest.NoteRestIndexer."""
        if 'noterest' not in self._analyses:
            self._analyses['noterest'] = noterest.NoteRestIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['noterest']

    def _get_multistop(self):
        """Used internally by get() to cache and retrieve results from the
        noterest.MultiStopIndexer."""
        if 'multistop' not in self._analyses:
            self._analyses['multistop'] = noterest.MultiStopIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['multistop']

    def _get_duration(self, data=None):
        """Used internally by get() to cache and retrieve results from the
        meter.DurationIndexer. The `data` argument should be a 2-tuple where the first element is
        a dataframe of results with one column per voice (like the noterest indexer) and the second
        element is a list of the part streams, one per part."""
        if data is not None:
            return meter.DurationIndexer(data[0], data[1]).run()
        elif 'duration' not in self._analyses:
            self._analyses['duration'] = meter.DurationIndexer(self._get_noterest(), self._get_part_streams()).run()
        return self._analyses['duration']

    def _get_tie(self, data=None):
        """Used internally by get() to cache and retrieve results from the
        meter.TieIndexer. The `data` argument should be a dataframe of music21
        note, rest, and chord objects. If nothing is passed to data, it
        gets the correct dataframe of music21 objects for this indexed piece
        automatically. Only pass something to data if you don't want the
        results to be cached or if you have some strange special-use case."""
        if data is not None:
            return meter.TieIndexer(data).run()
        elif 'tie' not in self._analyses:
            self._analyses['tie'] = meter.TieIndexer(self._get_m21_nrc_objs()).run()
        return self._analyses['tie']

    def _get_active_voices(self, data=None, settings=None):
        """Used internally by get() to cache and retrieve results from the
        active_voices.ActiveVoicesIndexer."""
        if data is not None:
            return active_voices.ActiveVoicesIndexer(data, settings).run()
        elif 'active_voices' not in self._analyses and (settings is None or settings ==
                active_voices.ActiveVoicesIndexer.default_settings):
            self._analyses['active_voices'] = active_voices.ActiveVoicesIndexer(self._get_noterest()).run()
            return self._analyses['active_voices']
        return active_voices.ActiveVoicesIndexer(self._get_noterest(), settings).run()

    def _get_beat_strength(self):
        """Used internally by get() to cache and retrieve results from the
        meter.NoteBeatStrengthIndexer."""
        if 'beat_strength' not in self._analyses:
            self._analyses['beat_strength'] = meter.NoteBeatStrengthIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['beat_strength']

    def _get_articulation(self):
        """Used internally by get() to cache and retrieve results from the
        expression.ExpressionIndexer."""
        if 'articulation' not in self._analyses:
            self._analyses['articulation'] = articulation.ArticulationIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['articulation']

    def _get_expression(self):
        """Used internally by get() to cache and retrieve results from the
        expression.ExpressionIndexer."""
        if 'expression' not in self._analyses:
            self._analyses['expression'] = expression.ExpressionIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['expression']

    def _get_vertical_interval(self, settings=None):
        """Used internally by get() to cache and retrieve results from the
        interval.IntervalIndexer. Since there are many possible settings for intervals, no matter
        what the user asks for intervals are calculated as compound, directed, and diatonic with
        quality. The results with these settings are stored and if the user asked for different
        settings, they are recalculated from these 'complete' cached results. This reindexing is
        done with the interval.IntervalReindexer."""
        if 'vertical_interval' not in self._analyses:
            self._analyses['vertical_interval'] = interval.IntervalIndexer(self._get_noterest(), settings=_default_interval_setts.copy()).run()
        if settings is not None and not ('directed' in settings and settings['directed'] == True and
                'quality' in settings and settings['quality'] in (True, 'diatonic with quality') and
                'simple or compound' in settings and settings['simple or compound'] == 'compound'):
            return interval.IntervalReindexer(self._analyses['vertical_interval'], settings).run()
        return self._analyses['vertical_interval']

    def _get_horizontal_interval(self, settings=None):
        """Used internally by get() to cache and retrieve results from the
        interval.IntervalIndexer. Since there are many possible settings for intervals, no matter
        what the user asks for intervals are calculated as compound, directed, and diatonic with
        quality. The results with these settings are stored and if the user asked for different
        settings, they are recalculated from these 'complete' cached results. This reindexing is
        done with the interval.IntervalReindexer. Those details are the same as for the
        _get_vertical_interval() method, but this method has an added check to see if the user asked
        for horiz_attach_later == False. In this case the index of each part's horizontal intervals
        is shifted forward one element and 0.0 is assigned as the first element."""
        # No matter what settings the user specifies, calculate the intervals in the most complete way.
        if 'horizontal_interval' not in self._analyses:
            self._analyses['horizontal_interval'] = interval.HorizontalIntervalIndexer(self._get_noterest(), _default_interval_setts.copy()).run()
        # If the user's settings were different, reindex the stored intervals.
        if settings is not None and not ('directed' in settings and settings['directed'] == True and
                'quality' in settings and settings['quality'] in (True, 'diatonic with quality') and
                'simple or compound' in settings and settings['simple or compound'] == 'compound'):
            post = interval.IntervalReindexer(self._analyses['horizontal_interval'], settings).run()
            # Switch to 'attach before' if necessary.
            if 'horiz_attach_later' not in settings or not settings['horiz_attach_later']:
                post = _attach_before(post)
            return post
        return self._analyses['horizontal_interval']

    def _get_dissonance(self):
        """Used internally by get() to cache and retrieve results from the
        dissonance.DissonanceIndexer. This method automatically supplies the input dataframes from
        the indexed_piece that is the self argument. If you want to call this with indexer results
        other than those associated with self, you can call the indexer directly."""
        if 'dissonance' not in self._analyses:
            h_setts = {'quality': False, 'simple or compound': 'compound', 'horiz_attach_later': False}
            v_setts = setts = {'quality': True, 'simple or compound': 'simple', 'directed': True}
            in_dfs = [self._get_beat_strength(), self._get_duration(),
                      self._get_horizontal_interval(h_setts), self._get_vertical_interval(v_setts)]
            self._analyses['dissonance'] = dissonance.DissonanceIndexer(in_dfs).run()
        return self._analyses['dissonance']

    def _get_lyric(self):
        """Used internally by get() as a convenience method to simplify
        getting results from the LyricIndexer.
        """
        if 'lyric' not in self._analyses:
            self._analyses['lyric'] = lyric.LyricIndexer(self._get_m21_nrc_objs()).run()
        return self._analyses['lyric']

    def _get_approach(self, data=[], settings=None):
        """Used internally by get() as a convenience method to simplify getting results from
        the ApproachIndexer. Since the results of the ExpressionIndexer are required for this and do not
        take any settings, they are automatically provided for the user, so only the results of the
        OverBassIndexer must necessarily be provided in the 'data' argument."""
        if len(data) == 1: # If data has more than two dfs, or the wrong dfs, this will be caught later
            temp = [self._get_expression()]
            temp.extend(data)
            data = temp
        return approach.ApproachIndexer(data, settings).run()

    def _get_m21_measure_objs(self):
        """Makes a dataframe of the music21 measure objects in the indexed_piece."""
        if 'm21_measure_objs' not in self._analyses:
            # filter for just the measure objects in each part of this indexed piece
            sers = [s.apply(_type_func_measure).dropna() for s in self._get_m21_objs()]
            self._analyses['m21_measure_objs'] = pandas.concat(sers, axis=1)
        return self._analyses['m21_measure_objs']

    def _get_measure(self, settings=None):
        """Fetches and caches a dataframe of the measure numbers in a piece.
        Can also return Humdrum-style measure numbers if {'style': 'Humdrum'}
        is passed as the settings. In this case, the results are not cached."""
        if (settings is not None and 'style' in settings and
            settings['style'] == 'Humdrum'): # this case is not cached.
            return meter.MeasureIndexer([self._get_m21_measure_objs(),
                                         self._get_time_signature()],
                                        self._get_part_streams(),
                                        settings).run()
        elif 'measure' not in self._analyses:
            self._analyses['measure'] = meter.MeasureIndexer([self._get_m21_measure_objs(),
                                                              self._get_time_signature()],
                                                             self._get_part_streams(),
                                                             ).run()
        return self._analyses['measure']

    def _get_ngram(self, data, settings=None):
        """Convenience method for fethcing ngram indexer results. These results never get cached
        though, because there are too many unpredictable variables in ngram queries."""
        return ngram.NGramIndexer(data, settings).run()

    def _get_offset(self, data, settings=None):
        if (settings is not None and settings['quarterLength'] == 'dynamic' and
            ('dom_data' not in settings or type(settings['dom_data']) != list)):
            settings['dom_data'] = [self._get_dissonance(), self._get_duration(),
                                     self._get_beat_strength(), self._get_noterest(),
                                     self._get_time_signature(),
                                     self._get_part_streams()[0].highestTime]
        return offset.FilterByOffsetIndexer(data, settings).run()

    def _get_clef(self, data=None):
        """Fetches and caches a dataframe of the clefs."""
        if data is not None:
            return staff.ClefIndexer(data).run()
        elif 'clef' not in self._analyses:
            self._analyses['clef'] = staff.ClefIndexer(self._get_m21_objs()).run()
        return self._analyses['clef']

    def _get_key_signature(self, data=None):
        """Fetches and caches a dataframe of the key signatures."""
        if data is not None:
            return staff.KeySignatureIndexer(data).run()
        elif 'key_signature' not in self._analyses:
            self._analyses['key_signature'] = staff.KeySignatureIndexer(self._get_m21_objs()).run()
        return self._analyses['key_signature']

    def _get_time_signature(self, data=None):
        """Fetches and caches a dataframe of the time signatures."""
        if data is not None:
            return meter.TimeSignatureIndexer(data).run()
        elif 'time_signature' not in self._analyses:
            self._analyses['time_signature'] = meter.TimeSignatureIndexer(self._get_m21_objs()).run()
        return self._analyses['time_signature']

    def _get_viz2hum(self):
        """Fetches and caches a dataframe of a kern representation of a piece.
        Don't even try to use this indexer without this convenience method. It's
        relatively complicated and poorly documented, but that's where this
        method comes in handy. """
        if 'viz2hum' not in self._analyses:
            score_arg = [self._get_clef(),
                         self._get_key_signature(),
                         self._get_time_signature(),
                         self._get_measure(settings={'style': 'Humdrum'}),
                         self._get_m21_nrc_objs(),
                         self._get_lyric()]
            setts = {'vizmd': self._metadata, 'm21md': self._score.metadata}
            self._analyses['viz2hum'] = output.Viz2HumIndexer(score_arg, setts).run()

        return self._analyses['viz2hum']

    def _get_xml(self):
        """Fetches and caches a string of an XML representation of a piece, as
        generated by music21."""
        if 'xml' not in self._analyses:
            self._analyses['xml'] = output.XMLIndexer(self._score).run()

        return self._analyses['xml']


    def get(self, analyzer_cls, data=None, settings=None):
        """
        Get the results of an Indexer run on this :class:`IndexedPiece`.

        :param analyzer_cls: The analyzer to run.
        :type analyzer_cls: str or VizitkaIndexer.
        :param settings: Settings to be used with the analyzer. Only use if necessary.
        :type settings: dict
        :param data: Input data for the analyzer to run. If this is provided for an indexer that
            normally caches its results (such as the NoteRestIndexer, the DurationIndexer, etc.),
            the results will not be cached since it is uncertain if the input passed in the ``data``
            argument was calculated on this indexed_piece.
        :type data: Depends on the requirement of the analyzer designated by the ``analyzer_cls``
            argument. Usually a :class:`pandas.DataFrame` or a list of :class:`pandas.Series`.
        :returns: Results of the analyzer.
        :rtype: Usually :class:`pandas.DataFrame` or list of :class:`pandas.Series`.
        :raises: :exc:`RuntimeWarning` if the ``analyzer_cls`` is invalid or cannot be found.
        :raises: :exc:`RuntimeError` if the first analyzer class in ``analyzer_cls`` does not use
            :class:`~music21.stream.Score` objects, and ``data`` is ``None``.
        """
        if analyzer_cls not in self._indexers: # Make sure the indexer requested exists.
            raise KeyError(IndexedPiece._NOT_AN_ANALYZER.format(analyzer_cls, sorted(self._indexers.keys())))

        args_dict = {} # Only pass the settings argument if it is not ``None``.
        if settings is not None:
            args_dict['settings'] = settings

        try: # Fetch or calculate the actual results requested.
            if data is None:
                results = self._indexers[analyzer_cls](**args_dict)
            else:
                results = self._indexers[analyzer_cls](data, **args_dict)
            if hasattr(results, 'run'): # execute analyzer if there is no caching method for this one
                results = results.run()
        except TypeError: # There is some issue with the 'settings' and/or 'data' arguments.
            raise RuntimeWarning(IndexedPiece._SUPERFLUOUS_OR_INSUFFICIENT_ARGUMENTS.format(analyzer_cls))

        return results

    def to_kern(self, path=None):
        """Exports score to a kern file in the humdrum format at the location
        specified in the `path` argument. If no path is provided, the
        default is to use the title of the piece in the metadata (not a very
        reliable naming convention) or the current indexed_piece's current
        path if there is no title. If there are lyrics in the piece, they
        will be included in the new kern file.

        **Example**
        from vizitka.models.indexed_piece import Importer()
        # Make an IndexedPiece object out of a symbolic notation file:
        ip = Importer('path_to_file.xml')
        ip.to_kern() # exports the piece to a kern file at 'path_to_file.krn'
        """
        # check if no valid path string was provided
        if not (isinstance(path, str) and path):
            if self._metadata['title']: # if there's a title in the metadata, use that
                path = self._metadata['title']
            else: # otherwise use the current file's path
                path = self._pathname.rsplit('.', 1)[0]

        # Add .krn to the end if it's not already there.
        if not path.endswith('.krn'):
            path += '.krn'

        return self._get_viz2hum().to_csv(path, sep='\t', index=False, header=False,
                                          index_label=False, quotechar='`')

    def to_xml(self, path=None):
        """Exports score to an xml file at the location specified in the `path`
        argument. If no path is provided, the default is to use the title of
        the piece in the metadata (not a very reliable naming convention) or
        the current indexed_piece's current path if there is no title. The
        conversion is done entirely by music21.

        **Example**
        from vizitka.models.indexed_piece import Importer()
        # Make an IndexedPiece object out of a symbolic notation file:
        ip = Importer('path_to_file.krn')
        ip.to_xml() # exports the piece to a kern file at 'path_to_file.xml'
        """
        # check if no valid path string was provided
        if not (isinstance(path, str) and path):
            if self._metadata['title']: # if there's a title in the metadata, use that
                path = self._metadata['title']
            else: # otherwise use the current file's path
                path = self._pathname.rsplit('.', 1)[0]

        # Add .xml to the end if the user didn't.
        if not path.endswith('.xml'):
            path += '.xml'

        pdb.set_trace()

        with open(path, 'w') as f:
            # writes the file and returns the number of characters written. The
            # number of characters is simply discarded
            chars = f.write(self._get_xml())

        return None

    def measure_index(self, dataframe):
        """Multi-indexes the index of the passed dataframe by adding the measures to the offsets.
        The passed dataframe should be of an indexer's results. Also adds
        index labels. Note that this method should ideally only be used at the end of a set of
        analysis steps, because there is no guarantee that the resultant multi-indexed dataframe
        will not cause problems if passed to a subsequent indexer.

        **Example**
        from vizitka.models.indexed_piece import Importer()
        # Make an IndexedPiece object out of a symbolic notation file:
        ip = Importer('path_to_file.xml')
        # Get some results from an indexer:
        df = ip.get('horizontal_interval')
        # Multi-index the dataframe index by adding the measure informaiton:
        ip.measure_index(df)
        """
        if not isinstance(dataframe, pandas.DataFrame):
            raise RuntimeWarning(IndexedPiece._NOT_DATAFRAME)
        # Make a copy of the dataframe to avoid altering it inplace
        df = dataframe.copy()
        # Get a series of the measures from the first part of this IndexedPiece
        measures = self.get('measure').iloc[:, 0]
        # Make sure it actually has measure events in it.
        if measures.empty:
            raise RuntimeWarning(IndexedPiece._NO_MEASURES)
        # Add measures as a column of the dataframe which merges the indecies
        df['Measure'] = measures
        # Forward-fill measure observations so that there's one label per event
        df['Measure'] = df['Measure'].ffill().apply(int)
        # Provide label for existing index
        df.index.name = 'Offset'
        # Reassign new column as an extra index
        df.set_index('Measure', append=True, inplace=True)
        # Rearrange indecies and return result. NB: rearranging cannot be done in place
        return df.reorder_levels(('Measure', 'Offset'))
