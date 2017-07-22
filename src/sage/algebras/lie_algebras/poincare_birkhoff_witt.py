"""
The Poincare-Birkhoff-Witt Basis For A Universal Enveloping Algebra

AUTHORS:

- Travis Scrimshaw (2013-11-03): Initial version

.. TODO::

    Implement a :class:`sage.categories.pushout.ConstructionFunctor`
    and return as the ``construction()``.
"""

#*****************************************************************************
#       Copyright (C) 2013-2017 Travis Scrimshaw <tcscrims at gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.cachefunc import cached_method
from sage.misc.misc_c import prod
from sage.categories.algebras import Algebras
from sage.monoids.indexed_free_monoid import IndexedFreeAbelianMonoid
from sage.combinat.free_module import CombinatorialFreeModule
from sage.sets.family import Family
from sage.rings.all import ZZ

class PoincareBirkhoffWittBasis(CombinatorialFreeModule):
    r"""
    The Poincare-Birkhoff-Witt (PBW) basis of the universal enveloping
    algebra of a Lie algebra.

    Consider a Lie algebra `\mathfrak{g}` with ordered basis
    `(b_1,\dots,b_n)`. Then the universal enveloping algebra `U(\mathfrak{g})`
    is generated by `b_1,\dots,b_n` and subject to the relations

    .. MATH::

        [b_i, b_j] = \sum_{k = 1}^n c_{ij}^k b_k

    where `c_{ij}^k` are the structure coefficients of `\mathfrak{g}`. The
    Poincare-Birkhoff-Witt (PBW) basis is given by the monomials
    `b_1^{e_1} b_2^{e_2} \cdots b_n^{e_n}`. Specifically, we can rewrite
    `b_j b_i = b_i b_j + [b_j, b_i]` where `j > i`, and we can repeat
    this to sort any monomial into

    .. MATH::

        b_{i_1} \cdots b_{i_k} = b_1^{e_1} \cdots b_n^{e_n} + LOT

    where `LOT` are lower order terms. Thus the PBW basis is a filtered basis
    for `U(\mathfrak{g})`.

    EXAMPLES:

    We construct the PBW basis of `\mathfrak{sl}_2`::

        sage: L = lie_algebras.three_dimensional_by_rank(QQ, 3, names=['E','F','H'])
        sage: PBW = L.pbw_basis()

    We then do some computations; in particular, we check that `[E, F] = H`::

        sage: E,F,H = PBW.algebra_generators()
        sage: E*F
        PBW['E']*PBW['F']
        sage: F*E
        PBW['E']*PBW['F'] - PBW['H']
        sage: E*F - F*E
        PBW['H']

    Next we construct another instance of the PBW basis, but sorted in the
    reverse order::

        sage: def neg_key(x):
        ....:     return -L.basis().keys().index(x)
        sage: PBW2 = L.pbw_basis(prefix='PBW2', basis_key=neg_key)

    We then check the multiplication is preserved::

        sage: PBW2(E) * PBW2(F)
        PBW2['F']*PBW2['E'] + PBW2['H']
        sage: PBW2(E*F)
        PBW2['F']*PBW2['E'] + PBW2['H']
        sage: F * E + H
        PBW['E']*PBW['F']

    We now construct the PBW basis for Lie algebra of regular
    vector fields on `\CC^{\times}`::

        sage: L = lie_algebras.regular_vector_fields(QQ)
        sage: PBW = L.pbw_basis()
        sage: G = PBW.algebra_generators()
        sage: G[2] * G[3]
        PBW[2]*PBW[3]
        sage: G[3] * G[2]
        PBW[2]*PBW[3] - PBW[5]
        sage: G[-2] * G[3] * G[2]
        PBW[-2]*PBW[2]*PBW[3] - PBW[-2]*PBW[5]
    """
    @staticmethod
    def __classcall_private__(cls, g, basis_key=None, prefix='PBW', **kwds):
        """
        Normalize input to ensure a unique representation.

        TESTS::

            sage: from sage.algebras.lie_algebras.poincare_birkhoff_witt import PoincareBirkhoffWittBasis
            sage: L = lie_algebras.sl(QQ, 2)
            sage: P1 = PoincareBirkhoffWittBasis(L)
            sage: P2 = PoincareBirkhoffWittBasis(L, prefix='PBW')
            sage: P1 is P2
            True
        """
        return super(PoincareBirkhoffWittBasis, cls).__classcall__(cls,
                            g, basis_key, prefix, **kwds)

    def __init__(self, g, basis_key, prefix, **kwds):
        """
        Initialize ``self``.

        TESTS::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: PBW = L.pbw_basis()
            sage: E,F,H = PBW.algebra_generators()
            sage: TestSuite(PBW).run(elements=[E, F, H])
            sage: TestSuite(PBW).run(elements=[E, F, H, E*F + H]) # long time
        """
        if basis_key is not None:
            self._basis_key = basis_key
        else:
            self._basis_key = g._basis_key

        R = g.base_ring()
        self._g = g
        monomials = IndexedFreeAbelianMonoid(g.basis().keys(), prefix,
                                             sorting_key=self._monoid_key, **kwds)
        CombinatorialFreeModule.__init__(self, R, monomials,
                                         prefix='', bracket=False, latex_bracket=False,
                                         sorting_key=self._monomial_key,
                                         category=Algebras(R).WithBasis().Filtered())

    def _monoid_key(self, x):
        """
        Return a key for comparison in the underlying monoid of ``self``.

        EXAMPLES::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: def neg_key(x):
            ....:     return -L.basis().keys().index(x)
            sage: PBW = L.pbw_basis(basis_key=neg_key)
            sage: M = PBW.basis().keys()
            sage: prod(M.gens())  # indirect doctest
            PBW[-alpha[1]]*PBW[alphacheck[1]]*PBW[alpha[1]]
        """
        return self._basis_key(x[0])

    def _monomial_key(self, x):
        """
        Compute the key for ``x`` so that the comparison is done by
        reverse degree lexicographic order.

        EXAMPLES::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: PBW = L.pbw_basis()
            sage: E,H,F = PBW.algebra_generators()
            sage: F*H*H*E  # indirect doctest
            PBW[alpha[1]]*PBW[alphacheck[1]]^2*PBW[-alpha[1]]
             + 8*PBW[alpha[1]]*PBW[alphacheck[1]]*PBW[-alpha[1]]
             - PBW[alphacheck[1]]^3 + 16*PBW[alpha[1]]*PBW[-alpha[1]]
             - 4*PBW[alphacheck[1]]^2 - 4*PBW[alphacheck[1]]

            sage: def neg_key(x):
            ....:     return -L.basis().keys().index(x)
            sage: PBW = L.pbw_basis(basis_key=neg_key)
            sage: E,H,F = PBW.algebra_generators()
            sage: E*H*H*F  # indirect doctest
            PBW[-alpha[1]]*PBW[alphacheck[1]]^2*PBW[alpha[1]]
             - 8*PBW[-alpha[1]]*PBW[alphacheck[1]]*PBW[alpha[1]]
             + PBW[alphacheck[1]]^3 + 16*PBW[-alpha[1]]*PBW[alpha[1]]
             - 4*PBW[alphacheck[1]]^2 + 4*PBW[alphacheck[1]]
        """
        return (-len(x), [self._basis_key(l) for l in x.to_word_list()])

    def _repr_(self):
        """
        Return a string representation of ``self``.

        EXAMPLES::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: L.pbw_basis()
            Universal enveloping algebra of
             Lie algebra of ['A', 1] in the Chevalley basis
             in the Poincare-Birkhoff-Witt basis
        """
        return "Universal enveloping algebra of {} in the Poincare-Birkhoff-Witt basis".format(self._g)

    def _coerce_map_from_(self, R):
        """
        Return ``True`` if there is a coercion map from ``R`` to ``self``.

        EXAMPLES:

        We lift from the Lie algebra::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: PBW = L.pbw_basis()
            sage: PBW.has_coerce_map_from(L)
            True
            sage: [PBW(g) for g in L.basis()]
            [PBW[alpha[1]], PBW[alphacheck[1]], PBW[-alpha[1]]]

        We can go between PBW bases under different sorting orders::

            sage: def neg_key(x):
            ....:     return -L.basis().keys().index(x)
            sage: PBW2 = L.pbw_basis(basis_key=neg_key)
            sage: E,H,F = PBW.algebra_generators()
            sage: PBW2(E*H*F)
            PBW[-alpha[1]]*PBW[alphacheck[1]]*PBW[alpha[1]]
             - 4*PBW[-alpha[1]]*PBW[alpha[1]]
             + PBW[alphacheck[1]]^2
             - 2*PBW[alphacheck[1]]

        TESTS:

        Check that we can take the preimage (:trac:`23375`)::

            sage: L = lie_algebras.cross_product(QQ)
            sage: pbw = L.pbw_basis()
            sage: L(pbw(L.an_element()))
            X + Y + Z
            sage: L(pbw(L.an_element())) == L.an_element()
            True
            sage: L(prod(pbw.gens()))
            Traceback (most recent call last):
            ValueError: PBW['X']*PBW['Y']*PBW['Z'] is not in the image
            sage: L(pbw.one())
            Traceback (most recent call last):
            ...
            ValueError: 1 is not in the image
        """
        if R == self._g:
            # Make this into the lift map
            I = self._indices
            def basis_function(x): return self.monomial(I.gen(x))
            def inv_supp(m): return None if m.length() != 1 else m.leading_support()
            # TODO: this diagonal, but with a smaller indexing set...
            return self._g.module_morphism(basis_function, codomain=self,
                                           triangular='upper', unitriangular=True,
                                           inverse_on_support=inv_supp)

        if isinstance(R, PoincareBirkhoffWittBasis) and self._g == R._g:
            I = self._indices
            def basis_function(x):
                return self.prod(self.monomial(I.gen(g)**e) for g,e in x._sorted_items())
            # TODO: this diagonal, but with a smaller indexing set...
            return R.module_morphism(basis_function, codomain=self)

        return super(PoincareBirkhoffWittBasis, self)._coerce_map_from_(R)

    def lie_algebra(self):
        """
        Return the underlying Lie algebra of ``self``.

        EXAMPLES::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: PBW = L.pbw_basis()
            sage: PBW.lie_algebra() is L
            True
        """
        return self._g

    def algebra_generators(self):
        """
        Return the algebra generators of ``self``.

        EXAMPLES::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: PBW = L.pbw_basis()
            sage: PBW.algebra_generators()
            Finite family {-alpha[1]: PBW[-alpha[1]],
                           alpha[1]: PBW[alpha[1]],
                           alphacheck[1]: PBW[alphacheck[1]]}
        """
        G = self._indices.gens()
        return Family(self._indices._indices, lambda x: self.monomial(G[x]),
                      name="generator map")

    gens = algebra_generators

    @cached_method
    def one_basis(self):
        """
        Return the basis element indexing `1`.

        EXAMPLES::

            sage: L = lie_algebras.three_dimensional_by_rank(QQ, 3, names=['E','F','H'])
            sage: PBW = L.pbw_basis()
            sage: ob = PBW.one_basis(); ob
            1
            sage: ob.parent()
            Free abelian monoid indexed by {'E', 'F', 'H'}
        """
        return self._indices.one()

    def product_on_basis(self, lhs, rhs):
        """
        Return the product of the two basis elements ``lhs`` and ``rhs``.

        EXAMPLES::

            sage: L = lie_algebras.three_dimensional_by_rank(QQ, 3, names=['E','F','H'])
            sage: PBW = L.pbw_basis()
            sage: I = PBW.indices()
            sage: PBW.product_on_basis(I.gen('E'), I.gen('F'))
            PBW['E']*PBW['F']
            sage: PBW.product_on_basis(I.gen('E'), I.gen('H'))
            PBW['E']*PBW['H']
            sage: PBW.product_on_basis(I.gen('H'), I.gen('E'))
            PBW['E']*PBW['H'] + 2*PBW['E']
            sage: PBW.product_on_basis(I.gen('F'), I.gen('E'))
            PBW['E']*PBW['F'] - PBW['H']
            sage: PBW.product_on_basis(I.gen('F'), I.gen('H'))
            PBW['F']*PBW['H']
            sage: PBW.product_on_basis(I.gen('H'), I.gen('F'))
            PBW['F']*PBW['H'] - 2*PBW['F']
            sage: PBW.product_on_basis(I.gen('H')**2, I.gen('F')**2)
            PBW['F']^2*PBW['H']^2 - 8*PBW['F']^2*PBW['H'] + 16*PBW['F']^2

            sage: E,F,H = PBW.algebra_generators()
            sage: E*F - F*E
            PBW['H']
            sage: H * F * E
            PBW['E']*PBW['F']*PBW['H'] - PBW['H']^2
            sage: E * F * H * E
            PBW['E']^2*PBW['F']*PBW['H'] + 2*PBW['E']^2*PBW['F']
             - PBW['E']*PBW['H']^2 - 2*PBW['E']*PBW['H']

        TESTS:

        Check that :trac:`23268` is fixed::

            sage: MS = MatrixSpace(QQ, 2,2)
            sage: gl = LieAlgebra(associative=MS)
            sage: Ugl = gl.pbw_basis()
            sage: prod(Ugl.gens())
            PBW[(0, 0)]*PBW[(0, 1)]*PBW[(1, 0)]*PBW[(1, 1)]
            sage: prod(reversed(list(Ugl.gens())))
            PBW[(0, 0)]*PBW[(0, 1)]*PBW[(1, 0)]*PBW[(1, 1)]
             - PBW[(0, 0)]^2*PBW[(1, 1)] + PBW[(0, 0)]*PBW[(1, 1)]^2
        """
        # Some trivial base cases
        if lhs == self.one_basis():
            return self.monomial(rhs)
        if rhs == self.one_basis():
            return self.monomial(lhs)

        I = self._indices
        trail = lhs.trailing_support()
        lead = rhs.leading_support()
        if self._basis_key(trail) <= self._basis_key(lead):
            return self.monomial(lhs * rhs)

        # Create the commutator
        # We have xy - yx = [x, y] -> xy = yx + [x, y] and we have x > y
        terms = self._g.monomial(trail).bracket(self._g.monomial(lead))
        lead = I.gen(lead)
        trail = I.gen(trail)
        mc = terms.monomial_coefficients(copy=False)
        terms = self.sum_of_terms((I.gen(t), c) for t,c in mc.items())
        terms += self.monomial(lead * trail)
        return self.monomial(lhs // trail) * terms * self.monomial(rhs // lead)

    def degree_on_basis(self, m):
        """
        Return the degree of the basis element indexed by ``m``.

        EXAMPLES::

            sage: L = lie_algebras.sl(QQ, 2)
            sage: PBW = L.pbw_basis()
            sage: E,H,F = PBW.algebra_generators()
            sage: PBW.degree_on_basis(E.leading_support())
            1
            sage: m = ((H*F)^10).trailing_support(key=PBW._monomial_key)  # long time
            sage: PBW.degree_on_basis(m)  # long time
            20
            sage: ((H*F*E)^4).maximal_degree()  # long time
            12
        """
        return m.length()

