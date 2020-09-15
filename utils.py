import itertools as it
from collections import Counter

def powerset(iterable, min_len=1, max_len=None):
    """
    Return the powerset of an iterable as a generator
    
    Args:
    iterable -- a list or other iterable
    min_len -- the shortest combination to return
    max_len -- the longest combination to return
    
    >>> list(powerset([1,2,3]))
    [(1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)]
    
    >>> list(powerset([1,2,3], min_len=0))
    [(), (1,), (2,), (3,), (1,2), (1,3), (2,3), (1,2,3)]
    
    >>> list(powerset([1,2,3], max_len=2))
    [(1,), (2,), (3,), (1,2), (1,3), (2,3)]
    """
    if max_len is None:
        max_len = len(iterable)
        
    s = list(iterable)
    
    return it.chain.from_iterable(it.combinations(s, r) for r in range(min_len, max_len + 1))

def merge_tuple(tuples):
    """
    Accept a tuple of tuples. Merge the innermost into one
    
    >>> list(merge_tuple( ((1,),) ))
    [(1,)]
    
    >>> list(merge_tuple(((1,), (1, 2))))
    [(1, 1, 2)]
    
    >>> list(merge_tuple( ((1, 2), (3, 4), (5, 5)) ))
    [(1, 2, 3, 4, 5, 5)]
        
    >>> list(merge_tuple( ((1,), (5, 5, 5, 5)) ))
    [(1, 5, 5, 5, 5)]
    
    >>> list(merge_tuple( ((5, 5),) ))
    [(5, 5)]
    """
    if all(type(inner) is tuple for inner in tuples):
        # merge the inner tuple into one, pack it inside a tuple
        yield tuple(it.chain.from_iterable(tuples))
    else:
        yield tuples

def merge_subtuples(iterable):
    """
    Accept an iterator of nested tuples. Merge the innermost tuples into one
    
    >>> list(merge_subtuples( [((1,),), ((1,), (1, 2)), ((1, 2), (3, 4), (5, 5))] ))
    [(1,), (1, 1, 2), (1, 2, 3, 4, 5, 5)]
    
    >>> list(merge_subtuples( [(1,), ((1,), (5, 5, 5, 5)), ((5, 5),)] ))
    [(1,), (1, 5, 5, 5, 5), (5, 5)]
    """
    for inner_tuple in iterable:
        yield merge_tuple(inner_tuple)
            
            
def intersection(a, b):
    """
    Find the intersection of two iterables
    
    >>> intersection((1,2,3), (2,3,4))
    (2, 3)
    
    >>> intersection((1,2,3,3), (2,3,3,4))
    (2, 3, 3)
    
    >>> intersection((1,2,3,3), (2,3,4,4))
    (2, 3)
    
    >>> intersection((1,2,3,3), (2,3,4,4))
    (2, 3)
    """
    return tuple(n for n, count in (Counter(a) & Counter(b)).items() for _ in range(count))

def difference(a, b):
    """
    Find the difference between two iterables
    
    "Which of a are not in b?"
    
    >>> difference((1,2,3), (2,3,4))
    (1,)
    
    >>> difference((1,2,3,3), (2,3,4))
    (1, 3)
    
    >>> difference((1,2,3,3), (2,3,4,4))
    (1, 3)
    """
    return tuple(n for n, count in (Counter(a) - Counter(b)).items() for _ in range(count))

def difference_symmetric(a, b):
    """
    Find the symmetric difference between two iterables
    
    >>> difference_symmetric((1,2,3), (2,3,4))
    (1, 4)
    
    >>> difference_symmetric((1,2,3,3), (2,3,4))
    (1, 3, 4)
    
    >>> difference_symmetric((1,2,3,3), (2,3,4,4))
    (1, 3, 4, 4)
    """
    return difference(a, b) + difference(b, a)
