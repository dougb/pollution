
from mixing_height import computeTime, computeRelTime

from time import localtime, strftime


def test_computeTime():
    assert 1590838740 == computeTime('7:39 am EDT May 30, 2020')

def test_computeRelTime():
    assert 1591056000 == computeRelTime(1590838740,"June",1,8,"pm")

def test_dec_computeRelTime():
    assert 1609556400 == computeRelTime(1609056000,"January",1,10,"pm")
