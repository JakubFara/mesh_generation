import numpy as np
from scipy.interpolate import CubicSpline, CubicHermiteSpline
from dolfin import UserExpression


class Shape_New(object):
    def __init__(self, L0, L1, Win, Wout, R, dx, *args, **kwargs):
        self.R = R
        self.Win = Win
        self.Wout = Wout
        self.L0 = L0
        self.L1 = L1

        mx = [-L0, -L1, 0,  L1, L0]
        my = [Win, Win, R, Wout,  Wout]

        cs = CubicSpline(mx[1:-1], my[1:-1])
        self.cs = cs

        p0 = L1 + dx
        p1 = L1 - dx
        self.p0 = p0
        self.p1 = p1

        self.hs0 = CubicHermiteSpline(
            [-p0, -p1], [Win, cs(-p1)], [0, cs.derivative()(-p1)]
        )
        self.hs1 = CubicHermiteSpline(
            [p1, p0], [cs(p1), Wout], [cs.derivative()(p1), 0]
        )

    def shape(self, x):
        if x < -self.p0:
            y = self.Win
        elif x < -self.p1:
            y = self.hs0(x)
        elif x < self.p1:
            y = self.cs(x)
        elif x < self.p0:
            y = self.hs1(x)
        else:
            y = self.Wout
        return y

    def derivative(self, x):
        if x < -self.p0:
            y = 0.0
        elif x < -self.p1:
            y = self.hs0.derivative()(x)
        elif x < self.p1:
            y = self.cs.derivative()(x)
        elif x < self.p0:
            y = self.hs1.derivative()(x)
        else:
            y = 0.0
        return y

    def derivative_as_expression(self):
        return Eval(self.derivative, degree=2)


class Eval(UserExpression):
    def __init__(self, f, **kwargs):
        self.f = f
        super().__init__(**kwargs)

    def eval(self, values, x):
        values[0] = self.f(x[1])
        return

    def value_shape(self):
        return
