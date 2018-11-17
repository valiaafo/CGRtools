# -*- coding: utf-8 -*-
#
#  Copyright 2017, 2018 Ramil Nugmanov <stsouko@live.ru>
#  Copyright 2017 Timur Madzhidov <tmadzhidov@gmail.com>
#  This file is part of CGRtools.
#
#  CGRtools is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
from collections import Counter
from functools import reduce
from itertools import count
from operator import mul, itemgetter
from warnings import warn


class Morgan:
    def _morgan(self, atom=True, isotope=False, stereo=False, hybridization=False, neighbors=False):
        """
        Morgan like algorithm for graph nodes ordering

        :param atom: differentiate elements and charges
        :param isotope: differentiate isotopes
        :param stereo: differentiate stereo atoms and bonds
        :param hybridization: differentiate hybridization of atoms
        :param neighbors: differentiate neighbors of atoms. useful for queries structures
        :return: dict of atom-weight pairs
        """
        if not len(self):  # for empty containers
            return {}

        params = {n: (node.weight(atom, isotope, stereo, hybridization, neighbors),
                      tuple(sorted(edge.weight(stereo) for edge in self._adj[n].values())))
                  for n, node in self._node.items()}
        scaf = {n: tuple(m) for n, m in self._adj.items()}
        newlevels = {}
        countprime = iter(primes)
        weights = {x: newlevels.get(y) or newlevels.setdefault(y, next(countprime))
                   for x, y in sorted(params.items(), key=itemgetter(1))}

        numb = len(set(weights.values()))
        stab = 0

        tries = len(self) * 4  # limit for searching
        while tries:
            oldnumb = numb
            neweights = {}
            countprime = iter(primes)

            # weights[n] ** 2 NEED for differentiation of molecules like A-B or any other complete graphs.
            tmp = {n: reduce(mul, (weights[x] for x in m), weights[n] ** 2) for n, m in scaf.items()}

            weights = {x: (neweights.get(y) or neweights.setdefault(y, next(countprime)))
                       for x, y in sorted(tmp.items(), key=itemgetter(1))}

            numb = len(set(weights.values()))
            if numb == oldnumb:
                x = Counter(weights.values())
                if x[max(x)] > 1:
                    if stab == 3:
                        break
                elif stab >= 2:
                    break

                stab += 1
            elif stab:
                stab = 0

            tries -= 1
            if not tries and numb < oldnumb:
                warn('morgan. number of attempts exceeded. uniqueness has decreased. last attempt will be made')
                tries = 1
        else:
            warn('morgan. number of attempts exceeded')

        return weights


def _eratosthenes():
    """Yields the sequence of prime numbers via the Sieve of Eratosthenes."""
    d = {}  # map each composite integer to its first-found prime factor
    for q in count(2):  # q gets 2, 3, 4, 5, ... ad infinitum
        p = d.pop(q, None)
        if p is None:
            # q not a key in D, so q is prime, therefore, yield it
            yield q
            # mark q squared as not-prime (with q as first-found prime factor)
            d[q * q] = q
        else:
            # let x <- smallest (N*p)+q which wasn't yet known to be composite
            # we just learned x is composite, with p first-found prime factor,
            # since p is the first-found prime factor of q -- find and mark it
            x = p + q
            while x in d:
                x += p
            d[x] = p


primes = tuple(x for _, x in zip(range(1000), _eratosthenes()))
