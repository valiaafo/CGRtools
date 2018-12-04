# -*- coding: utf-8 -*-
#
#  Copyright 2017, 2018 Ramil Nugmanov <stsouko@live.ru>
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
from .common import BaseContainer
from .molecule import MoleculeContainer
from ..algorithms import StringCGR, CGRCompose
from ..attributes import DynAtom, DynBond


class CGRContainer(StringCGR, CGRCompose, BaseContainer):
    """
    storage for CGRs. has similar to molecules behavior
    """

    node_attr_dict_factory = DynAtom
    edge_attr_dict_factory = DynBond

    def get_center_atoms(self, stereo=False):
        """ get list of atoms of reaction center (atoms with dynamic: bonds, stereo, charges, radicals).
        """
        nodes = set()
        for n, atom in self._node.items():
            if stereo:
                if atom._reagent != atom._product:
                    nodes.add(n)
            elif atom.stereo == atom.p_stereo:
                nodes.add(n)

        seen = set()
        for n, m_bond in self._adj.items():
            seen.add(n)
            for m, bond in m_bond.items():
                if m not in seen:
                    if stereo:
                        if bond._reagent != bond._product:
                            nodes.add(n)
                            nodes.add(m)
                    elif bond._reagent == bond._product:
                        nodes.add(n)
                        nodes.add(m)
        return list(nodes)

    def decompose(self):
        """
        decompose CGR to pair of Molecules, which represents reagents and products state of reaction

        :return: tuple of two molecules
        """
        reagents = MoleculeContainer()
        products = MoleculeContainer()

        for n, atom in self._node.items():
            reagents.add_atom(atom._reagent, n)
            products.add_atom(atom._product, n)

        seen = set()
        for n, m_bond in self._adj.items():
            seen.add(n)
            for m, bond in m_bond.items():
                if m not in seen:
                    if bond.order:
                        reagents.add_bond(n, m, bond._reagent)
                    if bond.p_order:
                        products.add_bond(n, m, bond._product)
        return reagents, products

    def __invert__(self):
        """
        decompose CGR
        """
        return self.decompose()

    def reset_query_marks(self, copy=False):
        """
        set or reset hyb and neighbors marks to atoms.

        :param copy: if True return copy of graph and keep existing as is
        :return: graph if copy True else None
        """
        g = self.copy() if copy else self
        for i, atom in g._node.items():
            neighbors = 0
            hybridization = 1
            p_neighbors = 0
            p_hybridization = 1
            # hyb 1- sp3; 2- sp2; 3- sp1; 4- aromatic
            for j, bond in g._adj[i].items():
                isnth = g._node[j] != 'H'

                order = bond.order
                if order:
                    if isnth:
                        neighbors += 1
                    if hybridization not in (3, 4):
                        if order == 4:
                            hybridization = 4
                        elif order == 3:
                            hybridization = 3
                        elif order == 2:
                            if hybridization == 2:
                                hybridization = 3
                            else:
                                hybridization = 2
                order = bond.p_order
                if order:
                    if isnth:
                        p_neighbors += 1
                    if p_hybridization not in (3, 4):
                        if order == 4:
                            p_hybridization = 4
                        elif order == 3:
                            p_hybridization = 3
                        elif order == 2:
                            if p_hybridization == 2:
                                p_hybridization = 3
                            else:
                                p_hybridization = 2

            atom.neighbors = neighbors
            atom.hybridization = hybridization
            atom.p_neighbors = p_neighbors
            atom.p_hybridization = p_hybridization
        if copy:
            return g
        self.flush_cache()

    _visible = ()


__all__ = ['CGRContainer']
