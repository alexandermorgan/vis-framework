from vis.analyzers.indexers import noterest, interval, new_ngram, metre
from vis.models.indexed_piece import IndexedPiece 
from vis.models.aggregated_pieces import AggregatedPieces
import pandas as pd
import pdb
import time

import vis
VIS_PATH = vis.__path__[0]

# piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Jos2308.mei'
piece_path2 = '/home/amor/Code/vis-framework/vis/tests/corpus/bwv2.xml'
piece_path = '/home/amor/Code/vis-framework/vis/tests/corpus/Kyrie.krn'
# piece_path = '/home/amor/Code/vis-framework/vis/scripts/Lassus_Duets/Lassus_1_Beatus_Vir.xml'
ind_piece = IndexedPiece(piece_path)
parts = ind_piece._import_score().parts

v_setts = {'quality': True, 'simple or compound': 'simple', 'directed': True, 'mp': False}
h_setts = {'quality': False, 'horiz_attach_later': False, 'simple or compound': 'simple', 'directed': True, 'mp': False}
n_setts = {'n': 5, 'continuer': 'P1', 'horizontal': 'lowest', 'vertical': [('0,4',)],
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_2 = {'n': 5, 'continuer': 'P1', 'vertical': 'all',
           'terminator': ['Rest'], 'open-ended': False, 'brackets': False}
n_setts_3 = {'n': 2, 'continuer': 'P1', 'vertical': [('0,4',)],
           'terminator': [], 'open-ended': False, 'brackets': False}

# pieces = (IndexedPiece(piece_path2), ind_piece)
# corpus = AggregatedPieces(pieces)
# pdb.set_trace()

nr = noterest.NoteRestIndexer(parts).run()
dr = metre.DurationIndexer(parts).run()
ms = metre.MeasureIndexer(parts).run()
bs = metre.NoteBeatStrengthIndexer(parts).run()
t0 = time.time()
hz = interval.HorizontalIntervalIndexer(nr, h_setts).run()
t1 = time.time()
print(str(t1-t0))
vt = interval.IntervalIndexer(nr, v_setts).run()

ng = new_ngram.NewNGramIndexer((vt, hz), n_setts).run()
ng_2 = new_ngram.NewNGramIndexer((hz,), n_setts_2).run()
# ng_3 = new_ngram.NewNGramIndexer((dr,), n_setts_3).run()


pdb.set_trace()