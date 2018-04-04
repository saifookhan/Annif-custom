"""Unit tests for hit processing in Annif"""

from annif.hit import AnalysisHit, HitFilter


def generate_hits(n):
    for i in range(n):
        yield AnalysisHit(uri='http://example.org/{}'.format(i),
                          label='hit {}'.format(i),
                          score=1.0 / (i + 1))


def test_hitfilter_limit():
    orighits = generate_hits(10)
    hits = HitFilter(orighits, limit=5)
    assert len(list(hits)) == 5


def test_hitfilter_threshold():
    orighits = generate_hits(10)
    hits = HitFilter(orighits, threshold=0.5)
    assert len(list(hits)) == 2


def test_hitfilter_zero_score():
    orighits = [AnalysisHit(uri='uri', label='label', score=0.0)]
    hits = HitFilter(orighits, limit=5, threshold=0.5)
    assert len(list(hits)) == 0