"""
Convex optimization modeling for cvxopt.

"""

# Copyright (C) 2006-2008 Jacob Mattingley and Stephen Boyd.
#
# This file is part of CVXMOD.
#
# CVXMOD is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# CVXMOD is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

from base import *

# user imports
import cvxopt.base

def eval(obj):
    return obj**0.5

class functionalform(function, elementwise, concave, increasing):
    """Understands square(x)."""
    def __init__(self, arg):
        self.arg = arg
        self.rows = rows(arg)
        self.cols = cols(arg)

    # extended-value extension is -inf.
    def _getposfn(self):
        return ispos(obj.arg)
    posfn = property(_getposfn)

class _stdform1(object):
    # inherit from something, later? jem. include NotImplementedError errors and a
    # test() function or so.
    """An F() standard form for -sqrt(x) + t <= 0."""
    def __init__(self, x, t):
        self.rows = rows(x)
        self.cols = cols(x)
        self.optvars = set((x, t))
        self.x = x
        self.t = t

    def indomain(self):
        return value(self.x >= 0)

    def getdomain(self):
        return [self.x >= 0, self.t >= -1, self.t <= 100]

    def setindomain(self):
        self.x.value = ones(size(self.x))
        self.t.value = -ones(size(self.t))

    def value(self):
        return eval(value(self.x)) + value(self.t)

    def jacobian(self, var):
        # not *quite* the jacobian, but nearly.
        if var is self.x:
            return -0.5*diag(value(self.x)**-0.5)
        elif var is self.t:
            return eye(rows(self.t))
        else:
            raise OptimizationError('illegal jacobian')

    def hessianz(self, firstvar, secondvar, z):
        if firstvar is secondvar is self.x:
            return diag(0.25*diag(value(self.x)**-1.5)*z)
        elif firstvar is secondvar is self.t:
            return zeros(rows(self.t))
        elif firstvar is self.x and secondvar is self.t:
            return zeros(rows(self.x), rows(self.t))
        elif firstvar is self.t and secondvar is self.x:
            return zeros(rows(self.t), rows(self.x))
        else:
            raise OptimizationError('illegal hessian')

applystdform = stdconcave(functionalform, _stdform1)
