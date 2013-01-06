#! /usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: analyzing.py
# Purpose: The model classes for the Analyzer controller.
#
# Copyright (C) 2012 Jamie Klassen, Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
'''
The model classes for the Analyzer controller.
'''


# Imports from...
# PyQt4
from PyQt4.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
# music21
from music21.metadata import Metadata



class ListOfPieces(QAbstractTableModel):
   '''
   This model holds a filename, a music21 Score object, and various pieces of
   information about the Score, to ease preparation for processing by the
   Analyzer and Experiment controllers.

   You cannot currently change the number of columns, or their name as returned
   by headerData(), at run-time.
   '''

   # Here's the data model:
   # self._pieces : a list of lists. For each sub-list...
   #    sublist[0] : filename
   #    sublist[1] : a music21 score object OR piece title (depending on "role" when data() is called)
   #    sublist[2] : list of names of parts in the score
   #    sublist[3] : offset intervals to analyze
   #    sublist[4] : list of pairs of indices for part combinations to prepare

   # Public class variables to track which column has which data
   # NOTE: Update _number_of_columns whenever you change the number of columns,
   #       since this variable is used by columnCount().
   # NOTE: Update _header_names whenever you change the number or definition of
   #       columns, since this variale is used by headerData().
   _number_of_columns = 5
   _header_names = ['Path', 'Title', 'List of Part Names', 'Offset',
                    'Part Combinations']
   filename = 0
   score = 1
   parts_list = 2
   offset_intervals = 3
   parts_combinations = 4

   # A role for data() that means to return the Score object rather than title
   ScoreRole = 'This is an object for the ScoreRole'



   def __init__(self, parent=QModelIndex()):
      '''
      Create a new ListOfPieces instance. Best to use no arguments.
      '''
      super.__init__(self, parent)
      self._pieces = []



   def rowCount(self, parent=QModelIndex()):
      '''
      Return the number of pieces in this list.
      '''
      return len(self._pieces)



   def columnCount( self, parent=QModelIndex() ):
      '''
      Return the number of columns in this ListOfPieces.
      '''
      # Every time we change the number of columns, we change this class
      # variable... so it should be correct.
      return ListOfPieces._number_of_columns



   def data(self, index, role):
      '''
      Returns the data for the table cell corresponding to the index. The role
      should always be Qt.DisplayRole except in the "score" column, in which
      case Qt.DisplayRole returns a string representing the title, and the
      ListOfPieces.ScoreRole returns the Score object.

      data() should return the following formats, but only if this specification
      was followed when calling setData(). If the index is...
      - ListOfPieces.filename : string
      - ListOfPieces.score : either...
         - music21.stream.Score (for ListOfPieces.ScoreRole)
         - string (for Qt.DisplayRole)
      - ListOfPieces.parts_list : list of string
      - ListOfPieces.offset_intervals : list of float
      - ListOfPieces.parts_combinations : either...
         - [[int, int], [int, int], ...]
         - [[int, 'bs'], [int, int], ...]
         - ['all']
         - ['all', 'bs']
         where 'all' means "all combinations" and 'bs' means "basso seguente."
      '''
      #if index.isValid():
         #if Qt.DisplayRole == role:
            #if self.model_score == index.column():
               #score = self._pieces[index.row()][index.column()]
               #if score.metadata is not None:
                  #return QVariant( score.metadata.title )
               #else:
                  #return QVariant('')
            #elif self.model_parts_list == index.column():
               ## this is for the part names
               #return QVariant( str(self._pieces[index.row()][index.column()])[1:-1] )
            #elif self.model_n == index.column():
               #return QVariant(",".join(str(n) for n in self._pieces[index.row()][index.column()]))
            #else:
               #return QVariant( self._pieces[index.row()][index.column()] )
         #elif 'raw_list' == role:
            #return QVariant( self._pieces[index.row()][index.column()] )
         #else:
            #return QVariant()
      pass



   def headerData(self, section, orientation, role):
      '''
      Return the column names for a ListOfPieces instance.

      Arguments:
      - section: the index of the column you want the name of
      - orientation: should be Qt.Horizontal; Qt.Vertical is ignored
      - role: should be Qt.DisplayRole; others are ignored

      If the section index is out of range, or the orientation or role is
      different than expected, an empty QVariant is returned.
      '''
      # All of the column titles are stored as class variables. I decided to
      # use the class name here, rather than "self," just in case they were
      # accidentally changed in this instance. We do not want to allow that.
      if Qt.Horizontal == orientation and Qt.DisplayRole == role and \
      section < ListOfPieces._number_of_columns:
         return ListOfPieces._header_names[section]
      else:
         return QVariant()



   def setData(self, index, value, role):
      '''
      Set the data in a particular cell. The index must be a QModelIndex as
      returned by, for example, ListOfPieces.createIndex. The value should be
      the appropriate type for the cell you are setting. The role must be
      Qt.EditRole, or no change is made.

      Returns True on setting the data in the cell, othwerise False.

      >>> a = ListOfPieces()
      >>> a.insertRows(0, 1)
      >>> index = a.createIndex(0, ListOfPieces.filename)
      >>> a.setData(index, 'kyrie.krn', Qt.EditRole)

      Use the following data formats:
      - ListOfPieces.filename : string
      - ListOfPieces.score : tuple, being (music21.stream.Score, string)
      - ListOfPieces.parts_list : list of string
      - ListOfPieces.offset_intervals : list of float
      - ListOfPieces.parts_combinations : either...
         - [[int, int], [int, int], ...]
         - [[int, 'bs'], [int, int], ...]
         - ['all']
         - ['all', 'bs']
         where 'all' means "all combinations" and 'bs' means "basso seguente."

      This method does not check your argument is the right type.
      '''
      pass
      #if Qt.EditRole == role:
         #self._pieces[index.row()][index.column()] = value
         #self.dataChanged.emit( index, index )
         #return True
      #else:
         #return False



   def insertRows(self, row, count, parent=QModelIndex()):
      '''
      Insert a certain number of rows at a certain point in the ListOfPieces.

      The first argument is the index you want for the first row to be inserted.
      The second argument is the number of rows to insert.

      The elements already in the list, with an index lower than "row" will
      retain their index values. The elements at indices "row" and higher will
      have an index value that is their original value plus "count".

      Each row is initialized with the following data:
      ['', None, [], [0.5], [2], '(no selection)']
      '''
      pass
      #self.beginInsertRows( parent, row, row+count-1 )
      #for zed in xrange(count):
         #self._pieces.insert( row, ['', None, [], 0.5, [2], '(no selection)'] )
      #self.endInsertRows()



   def removeRows( self, row, count, parent=QModelIndex() ):
      '''
      This is the opposite of insertRows(), and the arguments work in the same
      way.
      '''
      pass
      #self.beginRemoveRows( parent, row, row+count-1 )
      #self._pieces = self._pieces[:row] + self._pieces[row+count:]
      #self.endRemoveRows()



   def iterateRows( self ):
      '''
      Create an iterator that returns each of the filenames in this ListOfFiles.
      '''
      for piece_data in self._pieces:
         yield piece_data
# End Class ListOfPieces ------------------------------------------------------



class AnalysisRecord(object):
   '''
   Stores an intermediate record of an analysis. This class does not hold
   statistics or other results, but rather represents a mid-point, where the
   information being analyzed is stored separately from the piece.

   Each AnalysisRecord contains the following information:
   - a music21 Metadata object, with information about the work and movement
   - the names of the parts being analyzed
   - the minimum quarterLength offset value between subsequent elements
   - the events in the parts being analyzed, and the offset at which they happen
   - whether the score was "salami sliced" (maintaining the same offset
     between events) or not (which does not include an event if it is equal to
     the previous offset)

   This class is iterable. Each iteration returns a 2-tuple, where index 0 is
   the offset at which the event occurs in the Score, and index 1 is the event
   itself.

   You can access the Metadata object directly, through the "metadata" property.
   '''



   # Instance Data:
   # ==============
   # metadata : a music21 Metadata object
   # _part_names : list of string objects that are the part names
   # _offset : the (minimum) offset value between events
   # _is_salami : whether the score was "salami sliced"
   # _record : a list representing a record of an analysis, such that:
   #    _record[x][0] : holds the offset at which the event happened
   #    _record[x][1] : holds the event itself



   def __init__(self, metadata=None, part_names=None, offset=None, salami=None):
      '''
      Create a new AnalysisRecord. You should set the following keyword
      arguments when you make the AnalysisRecord:
      - metadata (with a music21 Metadata object)
      - _part_names (with a list of strings containing part names)
      - _offset (with a floating point number)
      - _salami (boolean)

      If you do not provide this information, sensible defaults will be used:
      - empty Metadata
      - _part_names : ['']
      - _offset : 0.0
      - _salami : False
      '''
      self._record = []

      if metadata is None:
         self.metadata = Metadata()
      else:
         self.metadata = metadata

      if part_names is None:
         self._part_names = ['']
      else:
         self._part_names = part_names

      if offset is None:
         self._offset = 0.0
      else:
         self._offset = offset

      if salami is None:
         self._salami = False
      else:
         self._salami = salami



   def __iter__(self):
      '''
      Iterate through the events in this AnalysisRecord.
      '''
      for event in self._record:
         yield event



   def part_names(self):
      '''
      Return a list of strings that represent the part names involved in this
      AnalysisRecord.

      >>> a = AnalysisRecord(part_names=['Clarinet', 'Tuba'])
      >>> a.part_names()
      ['Clarinet', 'Tuba']
      >>> a = AnalysisRecord(part_names=['Piano'])
      >>> a.part_names()
      ['Piano']
      >>> a = AnalysisRecord()
      >>> a.part_names()
      ['']
      '''
      return self._part_names



   def offset(self):
      '''
      Return the minimum offset between events in this AnalysisRecord. If
      salami_sliced() reutrns True, then all events are this offset from each
      other.

      >>> a = AnalysisRecord(offset=1)
      >>> a.offset()
      1
      >>> a = AnalysisRecord(offset=0.5)
      >>> a.offset()
      0.5
      >>> a = AnalysisRecord()
      >>> a.offset()
      0.0
      '''
      return self._offset



   def salami_sliced(self):
      '''
      Return whether or not the score was "salami sliced" to produce this
      AnalysisRecord.

      >>> a = AnalysisRecord(salami=True)
      >>> a.salami_sliced()
      True
      >>> a = AnalysisRecord(salami=False)
      >>> a.salami_sliced()
      False
      >>> a = AnalysisRecord()
      >>> a.salami_sliced()
      False
      '''
      return self._is_salami



   def append_event(self, offset, event):
      '''
      Add an event to the end of this AnalysisRecord.

      There are two arguments, both mandatory:
      - offset : (an int or float) the offset in the Score at which event happens
      - event : the object being analyzed
      '''
      self._record.append((offset, event))
# End class AnalysisRecord -----------------------------------------------------
