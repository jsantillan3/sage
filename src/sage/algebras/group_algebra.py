r"""
Group algebras

This functionality has been moved to :mod:`sage.categories.algebra_functor`.

TESTS:

Check that unpicking old group algebra classes works::

    sage: G = loads(b"x\x9cM\xceM\n\xc20\x10\x86a\xac\xff\xf1$n\xb2\xf1\x04\x82"
    ....:           b"\xe8>\xe0:\xc4fL\x83i\xda\x99$K\xc1M\xf5\xdaj\x1a\xc1\xdd<"
    ....:           b"\xf0\xbd0\x8f\xaa\x0e\xca\x00\x0f\x91R\x1d\x13\x01O\xdeb\x02I"
    ....:           b"\xd0\x13\x04\xf0QE\xdby\x96<\x81N50\x9c\x8c\x81r\x06.\xa4\x027"
    ....:           b"\xd4\xa5^\x16\xb2\xd3W\xfb\x02\xac\x9a\xb2\xce\xa3\xc0{\xa0V"
    ....:           b"\x9ar\x8c\xa1W-hv\xb0\rhR.\xe7\x0c\xa7cE\xd6\x9b\xc0\xad\x8f`"
    ....:           b"\x80X\xabn \x7f\xc0\xd9y\xb2\x1b\x04\xce\x87\xfb\x0b\x17\x02"
    ....:           b"\x97\xff\x05\xe5\x9f\x95\x93W\x0bN3Qx\xcc\xc2\xd5V\xe0\xfa\xf9"
    ....:           b"\xc9\x98\xc0\r\x7f\x03\x9d\xd7^'")
    sage: G
    Algebra of Dihedral group of order 6 as a permutation group over Rational Field
    sage: type(G)
    <class 'sage.algebras.group_algebra.GroupAlgebra_class_with_category'>
"""

#*****************************************************************************
#       Copyright (C) 2008 William Stein <wstein@gmail.com>
#                     2008 David Loeffler <d.loeffler.01@cantab.net>
#                     2009 Martin Raum <mraum@mpim-bonn.mpg.de>
#                     2011 John Palmieri <palmieri@math.washington.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.rings.all import IntegerRing
from sage.categories.all import Rings
from sage.categories.magmas import Magmas
from sage.categories.additive_magmas import AdditiveMagmas
from sage.categories.sets_cat import Sets
from sage.categories.morphism import SetMorphism
from sage.combinat.free_module import CombinatorialFreeModule


def GroupAlgebra(G, R=IntegerRing()):
    r"""
    Return the group algebra of `G` over `R`.

    INPUT:

    - `G` -- a group
    - `R` -- (default: `\ZZ`) a ring

    EXAMPLES:

    The *group algebra* `A=RG` is the space of formal linear
    combinations of elements of `G` with coefficients in `R`::

        sage: G = DihedralGroup(3)
        sage: R = QQ
        sage: A = GroupAlgebra(G, R); A
        Algebra of Dihedral group of order 6 as a permutation group over Rational Field
        sage: a = A.an_element(); a
        () + (1,2) + 3*(1,2,3) + 2*(1,3,2)

    This space is endowed with an algebra structure, obtained by extending
    by bilinearity the multiplication of `G` to a multiplication on `RG`::

        sage: A in Algebras
        True
        sage: a * a
        14*() + 5*(2,3) + 2*(1,2) + 10*(1,2,3) + 13*(1,3,2) + 5*(1,3)

    :func:`GroupAlgebra` is just a short hand for a more general
    construction that covers, e.g., monoid algebras, additive group
    algebras and so on::

        sage: G.algebra(QQ)
        Algebra of Dihedral group of order 6 as a permutation group over Rational Field

        sage: GroupAlgebra(G,QQ) is G.algebra(QQ)
        True

        sage: M = Monoids().example(); M
        An example of a monoid:
        the free monoid generated by ('a', 'b', 'c', 'd')
        sage: M.algebra(QQ)
        Algebra of An example of a monoid: the free monoid generated by ('a', 'b', 'c', 'd')
                over Rational Field

    See the documentation of :mod:`sage.categories.algebra_functor`
    for details.

    TESTS::

        sage: GroupAlgebra(1)
        Traceback (most recent call last):
        ...
        ValueError: 1 is not a magma or additive magma

        sage: GroupAlgebra(GL(3, GF(7)))
        Algebra of General Linear Group of degree 3 over Finite Field of size 7
         over Integer Ring
        sage: GroupAlgebra(GL(3, GF(7)), QQ)
        Algebra of General Linear Group of degree 3 over Finite Field of size 7
         over Rational Field
    """
    if not (G in Magmas() or G in AdditiveMagmas()):
        raise ValueError("%s is not a magma or additive magma" % G)
    if R not in Rings():
        raise ValueError("%s is not a ring" % R)
    return G.algebra(R)


class GroupAlgebra_class(CombinatorialFreeModule):
    def _coerce_map_from_(self, S):
        r"""
        Return a coercion from `S` or ``None``.

        INPUT:

        - ``S`` -- a parent

        Let us write ``self`` as `R[G]`. This method handles
        the case where `S` is another group/monoid/...-algebra
        `R'[H]`, with R coercing into `R'` and `H` coercing
        into `G`. In that case it returns the naturally
        induced coercion between `R'[H]` and `R[G]`. Otherwise
        it returns ``None``.

        EXAMPLES::

            sage: A = GroupAlgebra(SymmetricGroup(4), QQ)
            sage: B = GroupAlgebra(SymmetricGroup(3), ZZ)
            sage: A.has_coerce_map_from(B)
            True
            sage: B.has_coerce_map_from(A)
            False
            sage: A.has_coerce_map_from(ZZ)
            True
            sage: A.has_coerce_map_from(CC)
            False
            sage: A.has_coerce_map_from(SymmetricGroup(5))
            False
            sage: A.has_coerce_map_from(SymmetricGroup(2))
            True


            sage: H = CyclicPermutationGroup(3)
            sage: G = DihedralGroup(3)

            sage: QH = H.algebra(QQ)
            sage: ZH = H.algebra(ZZ)
            sage: QG = G.algebra(QQ)
            sage: ZG = G.algebra(ZZ)
            sage: ZG.coerce_map_from(H)
            Coercion map:
              From: Cyclic group of order 3 as a permutation group
              To:   Algebra of Dihedral group of order 6 as a permutation group over Integer Ring
            sage: QG.coerce_map_from(ZG)
            Generic morphism:
              From: Algebra of Dihedral group of order 6 as a permutation group over Integer Ring
              To:   Algebra of Dihedral group of order 6 as a permutation group over Rational Field
            sage: QG.coerce_map_from(QH)
            Generic morphism:
              From: Algebra of Cyclic group of order 3 as a permutation group over Rational Field
              To:   Algebra of Dihedral group of order 6 as a permutation group over Rational Field
            sage: QG.coerce_map_from(ZH)
            Generic morphism:
              From: Algebra of Cyclic group of order 3 as a permutation group over Integer Ring
              To:   Algebra of Dihedral group of order 6 as a permutation group over Rational Field

        As expected, there is no coercion when restricting the
        field::

            sage: ZG.coerce_map_from(QG)

        There is no coercion for additive groups since ``+`` could mean
        both the action (i.e., the group operation) or adding a term::

            sage: G = groups.misc.AdditiveCyclic(3)
            sage: ZG = G.algebra(ZZ, category=AdditiveMagmas())
            sage: ZG.has_coerce_map_from(G)
            False
        """
        G = self.basis().keys()
        K = self.base_ring()

        if G.has_coerce_map_from(S):
            from sage.categories.groups import Groups
            # No coercion for additive groups because of ambiguity of +
            #   being the group action or addition of a new term.
            return self.category().is_subcategory(Groups().Algebras(K))

        if S in Sets.Algebras:
            S_K = S.base_ring()
            S_G = S.basis().keys()
            hom_K = K.coerce_map_from(S_K)
            hom_G = G.coerce_map_from(S_G)
            if hom_K is not None and hom_G is not None:
                return SetMorphism(S.Hom(self, category=self.category() | S.category()),
                                   lambda x: self.sum_of_terms( (hom_G(g), hom_K(c)) for g,c in x ))

from sage.misc.persist import register_unpickle_override
register_unpickle_override('sage.algebras.group_algebras', 'GroupAlgebra',  GroupAlgebra_class)

