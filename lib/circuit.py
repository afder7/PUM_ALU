from lib.core import C, Input, Output
from lib.utils import CircuitError


class Circuit:
    ELEMENTS = {}

    def __init__(self, **kwargs):
        self._init = kwargs
        self._elements = []
        for elem, names in self.ELEMENTS.items():
            for n in names:
                e = elem()
                self._elements.append(e)
                setattr(self, n, e)
        self._input_names = []
        for name, contact in self.inout().items():
            if not (name.startswith('in') or name.startswith('out')):
                raise CircuitError("Bad contacts name")
            if contact:
                setattr(self, name, contact)
            elif name.startswith("in"):
                setattr(self, name, Input())
                self._input_names.append(name)
            else:
                setattr(self, name, Output())
        self._conductors = []
        for c in self.connect():
            self._conductors.append(C(*c))

    def inout(self):
        return {}

    def connect(self):
        return ()

    def update(self):
        for n, value in self._init.items():
            c = getattr(self, n)
            if n.startswith('in'):
                c.value = value
            else:
                value.value = c.value
        for g in self._elements:
            g.update()
        for c in self._conductors:
            c.update()
        for n in self._input_names:
            getattr(self, n).update()

    def run(self, n=100):
        for _ in range(n):
            self.update()


class Bridge(Circuit):
    def inout(self):
        return {
            "in1": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = self.in1.value


class NOT(Circuit):
    def inout(self):
        return {
            "in1": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = int(not self.in1.value)


class AND(Circuit):
    def inout(self):
        return {
            "in1": None,
            "in2": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = int(self.in1.value and self.in2.value)


class OR(Circuit):
    def inout(self):
        return {
            "in1": None,
            "in2": None,
            "out1": None
        }

    def update(self):
        super().update()
        self.out1.value = int(self.in1.value or self.in2.value)


class NOR(Circuit):
    ELEMENTS = {
        OR: ("o1",),
        NOT: ("n1",)
    }

    def inout(self):
        return {
            "in1": self.o1.in1,
            "in2": self.o1.in2,
            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.o1.out1, self.n1.in1),
        )


class NAND(Circuit):
    ELEMENTS = {
        NOT: ("n1",),
        AND: ("a1",)
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a1.in2,
            "out1": self.n1.out1
        }

    def connect(self):
        return (
            (self.a1.out1, self.n1.in1),
        )


class XOR(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2"),
        NOT: ("n1", "n2"),
        OR: ("o1",),
        Bridge: ("b1", "b2",)
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "out1": self.o1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a1.in1),
            (self.b2.out1, self.n1.in1),
            (self.n1.out1, self.a1.in2),
            (self.b1.out1, self.n2.in1),
            (self.b2.out1, self.a2.in1),
            (self.n2.out1, self.a2.in2),
            (self.a1.out1, self.o1.in1),
            (self.a2.out1, self.o1.in2)
        )


class AND3(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2"),
        Bridge: ("b1", "b2", "b3")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "out1": self.a2.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a1.in1),
            (self.b2.out1, self.a1.in2),
            (self.b3.out1, self.a2.in1),
            (self.a1.out1, self.a2.in2),
        )


class AND4(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2", "a3"),
        Bridge: ("b1", "b2", "b3", "b4")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "out1": self.a3.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a1.in1),
            (self.b2.out1, self.a1.in2),
            (self.b3.out1, self.a2.in1),
            (self.a1.out1, self.a2.in2),
            (self.b4.out1, self.a3.in1),
            (self.a2.out1, self.a3.in2)
        )


class OR3(Circuit):
    ELEMENTS = {
        OR: ("o1", "o2"),
        Bridge: ("b1", "b2", "b3")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "out1": self.o2.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.o1.in1),
            (self.b2.out1, self.o1.in2),
            (self.b3.out1, self.o2.in1),
            (self.o1.out1, self.o2.in2),
        )


class XNOR(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2"),
        NOT: ("n1", "n2"),
        OR: ("o1",),
        Bridge: ("b1", "b2")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "out1": self.o1.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.n1.in1),
            (self.b2.out1, self.n2.in1),
            (self.n1.out1, self.a1.in1),
            (self.n2.out1, self.a1.in2),
            (self.b1.out1, self.a2.in1),
            (self.b2.out1, self.a2.in2),
            (self.a1.out1, self.o1.in1),
            (self.a2.out1, self.o1.in2)
        )


class ODD(Circuit):
    ELEMENTS = {
        OR: ("o1",),
        XNOR: ("xn1", "xn2",),
        XOR: ("x1", "x2"),
        AND: ("a1", "a2"),
        Bridge: ("a", "b", "c", "d")
    }

    def inout(self):
        return {
            "in1": self.a.in1,
            "in2": self.b.in1,
            "in3": self.c.in1,
            "in4": self.d.in1,
            "out1": self.o1.out1
        }

    def connect(self):
        return (
            (self.a.out1, self.x1.in1),
            (self.b.out1, self.x1.in2),
            (self.a.out1, self.xn1.in1),
            (self.b.out1, self.xn1.in2),
            (self.c.out1, self.x2.in1),
            (self.d.out1, self.x2.in2),
            (self.c.out1, self.xn2.in1),
            (self.d.out1, self.xn2.in2),
            (self.x1.out1, self.a1.in1),
            (self.xn2.out1, self.a1.in2),
            (self.x2.out1, self.a2.in1),
            (self.xn1.out1, self.a2.in2),
            (self.a1.out1, self.o1.in1),
            (self.a2.out1, self.o1.in2)
        )


class MT1(Circuit):
    ELEMENTS = {
        AND3: ("at1", "at2"),
        AND: ("a1",),
        OR: ("o1", "o2",),
        Bridge: ("a", "b", "c", "d"),
        NOT: ("n1", "n2", "n3", "n4", "n7"),
        XOR: ("x1",)
    }

    def inout(self):
        return {
            "in1": self.a.in1,
            "in2": self.b.in1,
            "in3": self.c.in1,
            "in4": self.d.in1,
            "out1": self.n7.out1
        }

    def connect(self):
        return (
            (self.n1.in1, self.a.out1),
            (self.n2.in1, self.b.out1),
            (self.n3.in1, self.c.out1),
            (self.n4.in1, self.d.out1),
            (self.n4.out1, self.a1.in1),
            (self.a.out1, self.a1.in2),
            (self.n1.out1, self.o1.in1),
            (self.a1.out1, self.o1.in2),
            (self.n2.out1, self.at1.in1),
            (self.n3.out1, self.at1.in2),
            (self.o1.out1, self.at1.in3),
            (self.b.out1, self.x1.in1),
            (self.c.out1, self.x1.in2),
            (self.n1.out1, self.at2.in1),
            (self.n4.out1, self.at2.in2),
            (self.x1.out1, self.at2.in3),
            (self.at1.out1, self.o2.in1),
            (self.at2.out1, self.o2.in2),
            (self.o2.out1, self.n7.in1)
        )


class SC(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2"),
        AND3: ("at1", "at2", "at3", "at4"),
        XOR: ("x1",),
        OR: ("o1", "o2"),
        NOT: ("n1", "n2", "n3"),
        Bridge: ("a", "b", "c")
    }

    def inout(self):
        return {
            "in1": self.a.in1,
            "in2": self.b.in1,
            "in3": self.c.in1,
            "out1": self.at1.out1,
            "out2": self.o1.out1,
            "out3": self.o2.out1,
            "out4": self.at2.out1
        }

    def connect(self):
        return (
            (self.a.out1, self.n1.in1),
            (self.b.out1, self.n2.in1),
            (self.c.out1, self.n3.in1),
            (self.n1.out1, self.at1.in1),
            (self.n2.out1, self.at1.in2),
            (self.n3.out1, self.at1.in3),
            (self.a.out1, self.at2.in1),
            (self.b.out1, self.at2.in2),
            (self.c.out1, self.at2.in3),
            (self.n1.out1, self.at3.in1),
            (self.n2.out1, self.at3.in2),
            (self.c.out1, self.at3.in3),
            (self.n3.out1, self.a1.in1),
            (self.a.out1, self.x1.in1),
            (self.b.out1, self.x1.in2),
            (self.x1.out1, self.a1.in2),
            (self.at3.out1, self.o1.in1),
            (self.a1.out1, self.o1.in2),
            (self.c.out1, self.a2.in1),
            (self.x1.out1, self.a2.in2),
            (self.a.out1, self.at4.in1),
            (self.b.out1, self.at4.in2),
            (self.n3.out1, self.at4.in3),
            (self.a2.out1, self.o2.in1),
            (self.at4.out1, self.o2.in2),
        )


class HADD(Circuit):
    ELEMENTS = {
        XOR: ("x1",),
        AND: ("a1",),
        Bridge: ("a", "b")
    }

    def inout(self):
        return {
            "in1": self.a.in1,
            "in2": self.b.in1,
            "out1": self.x1.out1,
            "out2": self.a1.out1
        }

    def connect(self):
        return (
            (self.a.out1, self.x1.in1),
            (self.b.out1, self.x1.in2),
            (self.a.out1, self.a1.in1),
            (self.b.out1, self.a1.in2),
        )


class ADD(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2", "a3", "a4"),
        XOR: ("x1", "x2"),
        XNOR: ("xn1",),
        OR: ("o1", "o2"),
        NOT: ("n1",),
        Bridge: ("a", "b", "c"),
    }

    def inout(self):
        return {
            "in1": self.a.in1,
            "in2": self.b.in1,
            "in3": self.c.in1,
            "out1": self.o1.out1,
            "out2": self.o2.out1
        }

    def connect(self):
        return (
            (self.c.out1, self.a1.in1),
            (self.a.out1, self.xn1.in1),
            (self.b.out1, self.xn1.in2),
            (self.xn1.out1, self.a1.in2),
            (self.c.out1, self.n1.in1),
            (self.n1.out1, self.a2.in1),
            (self.a.out1, self.x1.in1),
            (self.b.out1, self.x1.in2),
            (self.x1.out1, self.a2.in2),
            (self.a1.out1, self.o1.in1),
            (self.a2.out1, self.o1.in2),
            (self.c.out1, self.a3.in1),
            (self.x1.out1, self.a3.in2),
            (self.a.out1, self.a4.in1),
            (self.b.out1, self.a4.in2),
            (self.a3.out1, self.o2.in1),
            (self.a4.out1, self.o2.in2)
        )


class NOT8(Circuit):
    ELEMENTS = {
        NOT: ("n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8"),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "out1": self.n1.out1,
            "out2": self.n2.out1,
            "out3": self.n3.out1,
            "out4": self.n4.out1,
            "out5": self.n5.out1,
            "out6": self.n6.out1,
            "out7": self.n7.out1,
            "out8": self.n8.out1,
        }

    def connect(self):
        return (
            (self.a1.out1, self.n1.in1),
            (self.a2.out1, self.n2.in1),
            (self.a3.out1, self.n3.in1),
            (self.a4.out1, self.n4.in1),
            (self.a5.out1, self.n5.in1),
            (self.a6.out1, self.n6.in1),
            (self.a7.out1, self.n7.in1),
            (self.a8.out1, self.n8.in1),
        )


class OR8(Circuit):
    ELEMENTS = {
        OR: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "in9": self.b1.in1,
            "in10": self.b2.in1,
            "in11": self.b3.in1,
            "in12": self.b4.in1,
            "in13": self.b5.in1,
            "in14": self.b6.in1,
            "in15": self.b7.in1,
            "in16": self.b8.in1,
            "out1": self.o1.out1,
            "out2": self.o2.out1,
            "out3": self.o3.out1,
            "out4": self.o4.out1,
            "out5": self.o5.out1,
            "out6": self.o6.out1,
            "out7": self.o7.out1,
            "out8": self.o8.out1,
        }

    def connect(self):
        return (
            (self.a1.out1, self.o1.in1),
            (self.b1.out1, self.o1.in2),
            (self.a2.out1, self.o2.in1),
            (self.b2.out1, self.o2.in2),
            (self.a3.out1, self.o3.in1),
            (self.b3.out1, self.o3.in2),
            (self.a4.out1, self.o4.in1),
            (self.b4.out1, self.o4.in2),
            (self.a5.out1, self.o5.in1),
            (self.b5.out1, self.o5.in2),
            (self.a6.out1, self.o6.in1),
            (self.b6.out1, self.o6.in2),
            (self.a7.out1, self.o7.in1),
            (self.b7.out1, self.o7.in2),
            (self.a8.out1, self.o8.in1),
            (self.b8.out1, self.o8.in2),
        )


class AND8(Circuit):
    ELEMENTS = {
        AND: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "in9": self.b1.in1,
            "in10": self.b2.in1,
            "in11": self.b3.in1,
            "in12": self.b4.in1,
            "in13": self.b5.in1,
            "in14": self.b6.in1,
            "in15": self.b7.in1,
            "in16": self.b8.in1,
            "out1": self.o1.out1,
            "out2": self.o2.out1,
            "out3": self.o3.out1,
            "out4": self.o4.out1,
            "out5": self.o5.out1,
            "out6": self.o6.out1,
            "out7": self.o7.out1,
            "out8": self.o8.out1,
        }

    def connect(self):
        return (
            (self.a1.out1, self.o1.in1),
            (self.b1.out1, self.o1.in2),
            (self.a2.out1, self.o2.in1),
            (self.b2.out1, self.o2.in2),
            (self.a3.out1, self.o3.in1),
            (self.b3.out1, self.o3.in2),
            (self.a4.out1, self.o4.in1),
            (self.b4.out1, self.o4.in2),
            (self.a5.out1, self.o5.in1),
            (self.b5.out1, self.o5.in2),
            (self.a6.out1, self.o6.in1),
            (self.b6.out1, self.o6.in2),
            (self.a7.out1, self.o7.in1),
            (self.b7.out1, self.o7.in2),
            (self.a8.out1, self.o8.in1),
            (self.b8.out1, self.o8.in2),
        )


class OR8M(Circuit):
    ELEMENTS = {
        OR: ("a1", "a2", "a3", "a4", "a5", "a6", "o"),
        Bridge: ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "in5": self.b5.in1,
            "in6": self.b6.in1,
            "in7": self.b7.in1,
            "in8": self.b8.in1,
            "out1": self.o.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a1.in1),
            (self.b2.out1, self.a1.in2),
            (self.b3.out1, self.a2.in1),
            (self.b4.out1, self.a2.in2),
            (self.b5.out1, self.a3.in1),
            (self.b6.out1, self.a3.in2),
            (self.b7.out1, self.a4.in1),
            (self.b8.out1, self.a4.in2),
            (self.a1.out1, self.a5.in1),
            (self.a2.out1, self.a5.in2),
            (self.a3.out1, self.a6.in1),
            (self.a4.out1, self.a6.in2),
            (self.a5.out1, self.o.in1),
            (self.a6.out1, self.o.in2),
        )


class AND8M(Circuit):
    ELEMENTS = {
        AND: ("a1", "a2", "a3", "a4", "a5", "a6", "o"),
        Bridge: ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "in5": self.b5.in1,
            "in6": self.b6.in1,
            "in7": self.b7.in1,
            "in8": self.b8.in1,
            "out1": self.o.out1
        }

    def connect(self):
        return (
            (self.b1.out1, self.a1.in1),
            (self.b2.out1, self.a1.in2),
            (self.b3.out1, self.a2.in1),
            (self.b4.out1, self.a2.in2),
            (self.b5.out1, self.a3.in1),
            (self.b6.out1, self.a3.in2),
            (self.b7.out1, self.a4.in1),
            (self.b8.out1, self.a4.in2),
            (self.a1.out1, self.a5.in1),
            (self.a2.out1, self.a5.in2),
            (self.a3.out1, self.a6.in1),
            (self.a4.out1, self.a6.in2),
            (self.a5.out1, self.o.in1),
            (self.a6.out1, self.o.in2),
        )


class EQ8(Circuit):
    ELEMENTS = {
        AND8M: ("ae1",),
        XNOR: ("xn1", "xn2", "xn3", "xn4", "xn5", "xn6", "xn7", "xn8"),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "in9": self.b1.in1,
            "in10": self.b2.in1,
            "in11": self.b3.in1,
            "in12": self.b4.in1,
            "in13": self.b5.in1,
            "in14": self.b6.in1,
            "in15": self.b7.in1,
            "in16": self.b8.in1,
            "out1": self.ae1.out1,
        }

    def connect(self):
        return (
            (self.a1.out1, self.xn1.in1),
            (self.b1.out1, self.xn1.in2),
            (self.xn1.out1, self.ae1.in1),
            (self.a2.out1, self.xn2.in1),
            (self.b2.out1, self.xn2.in2),
            (self.xn2.out1, self.ae1.in2),
            (self.a3.out1, self.xn3.in1),
            (self.b3.out1, self.xn3.in2),
            (self.xn3.out1, self.ae1.in3),
            (self.a4.out1, self.xn4.in1),
            (self.b4.out1, self.xn4.in2),
            (self.xn4.out1, self.ae1.in4),
            (self.a5.out1, self.xn5.in1),
            (self.b5.out1, self.xn5.in2),
            (self.xn5.out1, self.ae1.in5),
            (self.a6.out1, self.xn6.in1),
            (self.b6.out1, self.xn6.in2),
            (self.xn6.out1, self.ae1.in6),
            (self.a7.out1, self.xn7.in1),
            (self.b7.out1, self.xn7.in2),
            (self.xn7.out1, self.ae1.in7),
            (self.a8.out1, self.xn8.in1),
            (self.b8.out1, self.xn8.in2),
            (self.xn8.out1, self.ae1.in8),
        )


class NEQ8(Circuit):
    ELEMENTS = {
        NOT: ("n",),
        EQ8: ("ae1",),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "in9": self.b1.in1,
            "in10": self.b2.in1,
            "in11": self.b3.in1,
            "in12": self.b4.in1,
            "in13": self.b5.in1,
            "in14": self.b6.in1,
            "in15": self.b7.in1,
            "in16": self.b8.in1,
            "out1": self.n.out1,
        }

    def connect(self):
        return (
            (self.a1.out1, self.ae1.in1),
            (self.a2.out1, self.ae1.in2),
            (self.a3.out1, self.ae1.in3),
            (self.a4.out1, self.ae1.in4),
            (self.a5.out1, self.ae1.in5),
            (self.a6.out1, self.ae1.in6),
            (self.a7.out1, self.ae1.in7),
            (self.a8.out1, self.ae1.in8),
            (self.b1.out1, self.ae1.in9),
            (self.b2.out1, self.ae1.in10),
            (self.b3.out1, self.ae1.in11),
            (self.b4.out1, self.ae1.in12),
            (self.b5.out1, self.ae1.in13),
            (self.b6.out1, self.ae1.in14),
            (self.b7.out1, self.ae1.in15),
            (self.b8.out1, self.ae1.in16),
            (self.ae1.out1, self.n.in1)
        )


class GT8(Circuit):
    ELEMENTS = {
        NOT: ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"),
        XOR: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"),
        AND: ("g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "and1", "and2", "and3", "and4", "and5", "and6", "and7", "and8", "check"),
        OR: ("or1", "or2", "or3", "or4", "or5", "or6", "or7", "or8"),
        NEQ8: ("neq8",),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "ae1", "ae2", "ae3", "ae4", "ae5", "ae6", "ae7", "ae8", "oe1", "oe2", "oe3", "oe4", "oe5", "oe6", "oe7", "oe8", "re")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "in9": self.b1.in1,
            "in10": self.b2.in1,
            "in11": self.b3.in1,
            "in12": self.b4.in1,
            "in13": self.b5.in1,
            "in14": self.b6.in1,
            "in15": self.b7.in1,
            "in16": self.b8.in1,
            "out1": self.re.out1
        }

    def connect(self):
        return (
            (self.a1.out1, self.g1.in1),
            (self.b1.out1, self.g1.in2),
            (self.a1.out1, self.o1.in1),
            (self.b1.out1, self.o1.in2),
            (self.g1.out1, self.ae1.in1),
            (self.o1.out1, self.oe1.in1),

            (self.a2.out1, self.g2.in1),
            (self.b2.out1, self.g2.in2),
            (self.a2.out1, self.o2.in1),
            (self.b2.out1, self.o2.in2),
            (self.g2.out1, self.ae2.in1),
            (self.o2.out1, self.oe2.in1),

            (self.a3.out1, self.g3.in1),
            (self.b3.out1, self.g3.in2),
            (self.a3.out1, self.o3.in1),
            (self.b3.out1, self.o3.in2),
            (self.g3.out1, self.ae3.in1),
            (self.o3.out1, self.oe3.in1),

            (self.a4.out1, self.g4.in1),
            (self.b4.out1, self.g4.in2),
            (self.a4.out1, self.o4.in1),
            (self.b4.out1, self.o4.in2),
            (self.g4.out1, self.ae4.in1),
            (self.o4.out1, self.oe4.in1),

            (self.a5.out1, self.g5.in1),
            (self.b5.out1, self.g5.in2),
            (self.a5.out1, self.o5.in1),
            (self.b5.out1, self.o5.in2),
            (self.g5.out1, self.ae5.in1),
            (self.o5.out1, self.oe5.in1),

            (self.a6.out1, self.g6.in1),
            (self.b6.out1, self.g6.in2),
            (self.a6.out1, self.o6.in1),
            (self.b6.out1, self.o6.in2),
            (self.g6.out1, self.ae6.in1),
            (self.o6.out1, self.oe6.in1),

            (self.a7.out1, self.g7.in1),
            (self.b7.out1, self.g7.in2),
            (self.a7.out1, self.o7.in1),
            (self.b7.out1, self.o7.in2),
            (self.g7.out1, self.ae7.in1),
            (self.o7.out1, self.oe7.in1),

            (self.a8.out1, self.g8.in1),
            (self.b8.out1, self.g8.in2),
            (self.a8.out1, self.o8.in1),
            (self.b8.out1, self.o8.in2),
            (self.g8.out1, self.ae8.in1),
            (self.o8.out1, self.oe8.in1),

            (self.ae8.out1, self.or8.in1),
            (self.oe8.out1, self.or8.in2),

            (self.or8.out1, self.and8.in1),
            (self.oe7.out1, self.and8.in2),
            (self.and8.out1, self.or7.in1),
            (self.ae7.out1, self.or7.in2),

            (self.or7.out1, self.and7.in1),
            (self.oe6.out1, self.and7.in2),
            (self.and7.out1, self.or6.in1),
            (self.ae6.out1, self.or6.in2),

            (self.or6.out1, self.and6.in1),
            (self.oe5.out1, self.and6.in2),
            (self.and6.out1, self.or5.in1),
            (self.ae5.out1, self.or5.in2),

            (self.or5.out1, self.and5.in1),
            (self.oe4.out1, self.and5.in2),
            (self.and5.out1, self.or4.in1),
            (self.ae4.out1, self.or4.in2),

            (self.or4.out1, self.and4.in1),
            (self.oe3.out1, self.and4.in2),
            (self.and4.out1, self.or3.in1),
            (self.ae3.out1, self.or3.in2),

            (self.or3.out1, self.and3.in1),
            (self.oe2.out1, self.and3.in2),
            (self.and3.out1, self.or2.in1),
            (self.ae2.out1, self.or2.in2),

            (self.or2.out1, self.and2.in1),
            (self.oe1.out1, self.and2.in2),
            (self.and2.out1, self.or1.in1),
            (self.ae1.out1, self.or1.in2),

            (self.a1.out1, self.neq8.in1),
            (self.a2.out1, self.neq8.in2),
            (self.a3.out1, self.neq8.in3),
            (self.a4.out1, self.neq8.in4),
            (self.a5.out1, self.neq8.in5),
            (self.a6.out1, self.neq8.in6),
            (self.a7.out1, self.neq8.in7),
            (self.a8.out1, self.neq8.in8),

            (self.b1.out1, self.c1.in1),
            (self.b2.out1, self.c2.in1),
            (self.b3.out1, self.c3.in1),
            (self.b4.out1, self.c4.in1),
            (self.b5.out1, self.c5.in1),
            (self.b6.out1, self.c6.in1),
            (self.b7.out1, self.c7.in1),
            (self.b8.out1, self.c8.in1),

            (self.c1.out1, self.neq8.in9),
            (self.c2.out1, self.neq8.in10),
            (self.c3.out1, self.neq8.in11),
            (self.c4.out1, self.neq8.in12),
            (self.c5.out1, self.neq8.in13),
            (self.c6.out1, self.neq8.in14),
            (self.c7.out1, self.neq8.in15),
            (self.c8.out1, self.neq8.in16),

            (self.or1.out1, self.check.in1),
            (self.neq8.out1, self.check.in2),
            (self.check.out1, self.re.in1)
        )


class LT8(Circuit):
    ELEMENTS = {
        NOT: ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"),
        XOR: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"),
        AND: ("g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "and1", "and2", "and3", "and4", "and5", "and6", "and7", "and8", "check"),
        OR: ("or1", "or2", "or3", "or4", "or5", "or6", "or7", "or8"),
        NEQ8: ("neq8",),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "ae1", "ae2", "ae3", "ae4", "ae5", "ae6", "ae7", "ae8", "oe1", "oe2", "oe3", "oe4", "oe5", "oe6", "oe7", "oe8", "re")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "in5": self.b5.in1,
            "in6": self.b6.in1,
            "in7": self.b7.in1,
            "in8": self.b8.in1,
            "in9": self.a1.in1,
            "in10": self.a2.in1,
            "in11": self.a3.in1,
            "in12": self.a4.in1,
            "in13": self.a5.in1,
            "in14": self.a6.in1,
            "in15": self.a7.in1,
            "in16": self.a8.in1,
            "out1": self.re.out1
        }

    def connect(self):
        return (
            (self.a1.out1, self.g1.in1),
            (self.b1.out1, self.g1.in2),
            (self.a1.out1, self.o1.in1),
            (self.b1.out1, self.o1.in2),
            (self.g1.out1, self.ae1.in1),
            (self.o1.out1, self.oe1.in1),

            (self.a2.out1, self.g2.in1),
            (self.b2.out1, self.g2.in2),
            (self.a2.out1, self.o2.in1),
            (self.b2.out1, self.o2.in2),
            (self.g2.out1, self.ae2.in1),
            (self.o2.out1, self.oe2.in1),

            (self.a3.out1, self.g3.in1),
            (self.b3.out1, self.g3.in2),
            (self.a3.out1, self.o3.in1),
            (self.b3.out1, self.o3.in2),
            (self.g3.out1, self.ae3.in1),
            (self.o3.out1, self.oe3.in1),

            (self.a4.out1, self.g4.in1),
            (self.b4.out1, self.g4.in2),
            (self.a4.out1, self.o4.in1),
            (self.b4.out1, self.o4.in2),
            (self.g4.out1, self.ae4.in1),
            (self.o4.out1, self.oe4.in1),

            (self.a5.out1, self.g5.in1),
            (self.b5.out1, self.g5.in2),
            (self.a5.out1, self.o5.in1),
            (self.b5.out1, self.o5.in2),
            (self.g5.out1, self.ae5.in1),
            (self.o5.out1, self.oe5.in1),

            (self.a6.out1, self.g6.in1),
            (self.b6.out1, self.g6.in2),
            (self.a6.out1, self.o6.in1),
            (self.b6.out1, self.o6.in2),
            (self.g6.out1, self.ae6.in1),
            (self.o6.out1, self.oe6.in1),

            (self.a7.out1, self.g7.in1),
            (self.b7.out1, self.g7.in2),
            (self.a7.out1, self.o7.in1),
            (self.b7.out1, self.o7.in2),
            (self.g7.out1, self.ae7.in1),
            (self.o7.out1, self.oe7.in1),

            (self.a8.out1, self.g8.in1),
            (self.b8.out1, self.g8.in2),
            (self.a8.out1, self.o8.in1),
            (self.b8.out1, self.o8.in2),
            (self.g8.out1, self.ae8.in1),
            (self.o8.out1, self.oe8.in1),

            (self.ae8.out1, self.or8.in1),
            (self.oe8.out1, self.or8.in2),

            (self.or8.out1, self.and8.in1),
            (self.oe7.out1, self.and8.in2),
            (self.and8.out1, self.or7.in1),
            (self.ae7.out1, self.or7.in2),

            (self.or7.out1, self.and7.in1),
            (self.oe6.out1, self.and7.in2),
            (self.and7.out1, self.or6.in1),
            (self.ae6.out1, self.or6.in2),

            (self.or6.out1, self.and6.in1),
            (self.oe5.out1, self.and6.in2),
            (self.and6.out1, self.or5.in1),
            (self.ae5.out1, self.or5.in2),

            (self.or5.out1, self.and5.in1),
            (self.oe4.out1, self.and5.in2),
            (self.and5.out1, self.or4.in1),
            (self.ae4.out1, self.or4.in2),

            (self.or4.out1, self.and4.in1),
            (self.oe3.out1, self.and4.in2),
            (self.and4.out1, self.or3.in1),
            (self.ae3.out1, self.or3.in2),

            (self.or3.out1, self.and3.in1),
            (self.oe2.out1, self.and3.in2),
            (self.and3.out1, self.or2.in1),
            (self.ae2.out1, self.or2.in2),

            (self.or2.out1, self.and2.in1),
            (self.oe1.out1, self.and2.in2),
            (self.and2.out1, self.or1.in1),
            (self.ae1.out1, self.or1.in2),

            (self.a1.out1, self.neq8.in1),
            (self.a2.out1, self.neq8.in2),
            (self.a3.out1, self.neq8.in3),
            (self.a4.out1, self.neq8.in4),
            (self.a5.out1, self.neq8.in5),
            (self.a6.out1, self.neq8.in6),
            (self.a7.out1, self.neq8.in7),
            (self.a8.out1, self.neq8.in8),

            (self.b1.out1, self.c1.in1),
            (self.b2.out1, self.c2.in1),
            (self.b3.out1, self.c3.in1),
            (self.b4.out1, self.c4.in1),
            (self.b5.out1, self.c5.in1),
            (self.b6.out1, self.c6.in1),
            (self.b7.out1, self.c7.in1),
            (self.b8.out1, self.c8.in1),

            (self.c1.out1, self.neq8.in9),
            (self.c2.out1, self.neq8.in10),
            (self.c3.out1, self.neq8.in11),
            (self.c4.out1, self.neq8.in12),
            (self.c5.out1, self.neq8.in13),
            (self.c6.out1, self.neq8.in14),
            (self.c7.out1, self.neq8.in15),
            (self.c8.out1, self.neq8.in16),

            (self.or1.out1, self.check.in1),
            (self.neq8.out1, self.check.in2),
            (self.check.out1, self.re.in1)
        )


class GTE8(Circuit):
    ELEMENTS = {
        NOT: ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"),
        XOR: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"),
        AND: ("g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "and1", "and2", "and3", "and4", "and5", "and6", "and7", "and8"),
        OR: ("or1", "or2", "or3", "or4", "or5", "or6", "or7", "or8"),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "ae1", "ae2", "ae3", "ae4", "ae5", "ae6", "ae7", "ae8", "oe1", "oe2", "oe3", "oe4", "oe5", "oe6", "oe7", "oe8", "re")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "in9": self.b1.in1,
            "in10": self.b2.in1,
            "in11": self.b3.in1,
            "in12": self.b4.in1,
            "in13": self.b5.in1,
            "in14": self.b6.in1,
            "in15": self.b7.in1,
            "in16": self.b8.in1,
            "out1": self.re.out1
        }

    def connect(self):
        return (
            (self.a1.out1, self.g1.in1),
            (self.b1.out1, self.g1.in2),
            (self.a1.out1, self.o1.in1),
            (self.b1.out1, self.o1.in2),
            (self.g1.out1, self.ae1.in1),
            (self.o1.out1, self.oe1.in1),

            (self.a2.out1, self.g2.in1),
            (self.b2.out1, self.g2.in2),
            (self.a2.out1, self.o2.in1),
            (self.b2.out1, self.o2.in2),
            (self.g2.out1, self.ae2.in1),
            (self.o2.out1, self.oe2.in1),

            (self.a3.out1, self.g3.in1),
            (self.b3.out1, self.g3.in2),
            (self.a3.out1, self.o3.in1),
            (self.b3.out1, self.o3.in2),
            (self.g3.out1, self.ae3.in1),
            (self.o3.out1, self.oe3.in1),

            (self.a4.out1, self.g4.in1),
            (self.b4.out1, self.g4.in2),
            (self.a4.out1, self.o4.in1),
            (self.b4.out1, self.o4.in2),
            (self.g4.out1, self.ae4.in1),
            (self.o4.out1, self.oe4.in1),

            (self.a5.out1, self.g5.in1),
            (self.b5.out1, self.g5.in2),
            (self.a5.out1, self.o5.in1),
            (self.b5.out1, self.o5.in2),
            (self.g5.out1, self.ae5.in1),
            (self.o5.out1, self.oe5.in1),

            (self.a6.out1, self.g6.in1),
            (self.b6.out1, self.g6.in2),
            (self.a6.out1, self.o6.in1),
            (self.b6.out1, self.o6.in2),
            (self.g6.out1, self.ae6.in1),
            (self.o6.out1, self.oe6.in1),

            (self.a7.out1, self.g7.in1),
            (self.b7.out1, self.g7.in2),
            (self.a7.out1, self.o7.in1),
            (self.b7.out1, self.o7.in2),
            (self.g7.out1, self.ae7.in1),
            (self.o7.out1, self.oe7.in1),

            (self.a8.out1, self.g8.in1),
            (self.b8.out1, self.g8.in2),
            (self.a8.out1, self.o8.in1),
            (self.b8.out1, self.o8.in2),
            (self.g8.out1, self.ae8.in1),
            (self.o8.out1, self.oe8.in1),

            (self.ae8.out1, self.or8.in1),
            (self.oe8.out1, self.or8.in2),

            (self.or8.out1, self.and8.in1),
            (self.oe7.out1, self.and8.in2),
            (self.and8.out1, self.or7.in1),
            (self.ae7.out1, self.or7.in2),

            (self.or7.out1, self.and7.in1),
            (self.oe6.out1, self.and7.in2),
            (self.and7.out1, self.or6.in1),
            (self.ae6.out1, self.or6.in2),

            (self.or6.out1, self.and6.in1),
            (self.oe5.out1, self.and6.in2),
            (self.and6.out1, self.or5.in1),
            (self.ae5.out1, self.or5.in2),

            (self.or5.out1, self.and5.in1),
            (self.oe4.out1, self.and5.in2),
            (self.and5.out1, self.or4.in1),
            (self.ae4.out1, self.or4.in2),

            (self.or4.out1, self.and4.in1),
            (self.oe3.out1, self.and4.in2),
            (self.and4.out1, self.or3.in1),
            (self.ae3.out1, self.or3.in2),

            (self.or3.out1, self.and3.in1),
            (self.oe2.out1, self.and3.in2),
            (self.and3.out1, self.or2.in1),
            (self.ae2.out1, self.or2.in2),

            (self.or2.out1, self.and2.in1),
            (self.oe1.out1, self.and2.in2),
            (self.and2.out1, self.or1.in1),
            (self.ae1.out1, self.or1.in2),

            (self.or1.out1, self.re.in1)
        )


class LTE8(Circuit):
    ELEMENTS = {
        NOT: ("b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"),
        XOR: ("o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"),
        AND: ("g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "and1", "and2", "and3", "and4", "and5", "and6", "and7", "and8"),
        OR: ("or1", "or2", "or3", "or4", "or5", "or6", "or7", "or8"),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "ae1", "ae2", "ae3", "ae4", "ae5", "ae6", "ae7", "ae8", "oe1", "oe2", "oe3", "oe4", "oe5", "oe6", "oe7", "oe8", "re")
    }

    def inout(self):
        return {
            "in1": self.b1.in1,
            "in2": self.b2.in1,
            "in3": self.b3.in1,
            "in4": self.b4.in1,
            "in5": self.b5.in1,
            "in6": self.b6.in1,
            "in7": self.b7.in1,
            "in8": self.b8.in1,
            "in9": self.a1.in1,
            "in10": self.a2.in1,
            "in11": self.a3.in1,
            "in12": self.a4.in1,
            "in13": self.a5.in1,
            "in14": self.a6.in1,
            "in15": self.a7.in1,
            "in16": self.a8.in1,
            "out1": self.re.out1
        }

    def connect(self):
        return (
            (self.a1.out1, self.g1.in1),
            (self.b1.out1, self.g1.in2),
            (self.a1.out1, self.o1.in1),
            (self.b1.out1, self.o1.in2),
            (self.g1.out1, self.ae1.in1),
            (self.o1.out1, self.oe1.in1),

            (self.a2.out1, self.g2.in1),
            (self.b2.out1, self.g2.in2),
            (self.a2.out1, self.o2.in1),
            (self.b2.out1, self.o2.in2),
            (self.g2.out1, self.ae2.in1),
            (self.o2.out1, self.oe2.in1),

            (self.a3.out1, self.g3.in1),
            (self.b3.out1, self.g3.in2),
            (self.a3.out1, self.o3.in1),
            (self.b3.out1, self.o3.in2),
            (self.g3.out1, self.ae3.in1),
            (self.o3.out1, self.oe3.in1),

            (self.a4.out1, self.g4.in1),
            (self.b4.out1, self.g4.in2),
            (self.a4.out1, self.o4.in1),
            (self.b4.out1, self.o4.in2),
            (self.g4.out1, self.ae4.in1),
            (self.o4.out1, self.oe4.in1),

            (self.a5.out1, self.g5.in1),
            (self.b5.out1, self.g5.in2),
            (self.a5.out1, self.o5.in1),
            (self.b5.out1, self.o5.in2),
            (self.g5.out1, self.ae5.in1),
            (self.o5.out1, self.oe5.in1),

            (self.a6.out1, self.g6.in1),
            (self.b6.out1, self.g6.in2),
            (self.a6.out1, self.o6.in1),
            (self.b6.out1, self.o6.in2),
            (self.g6.out1, self.ae6.in1),
            (self.o6.out1, self.oe6.in1),

            (self.a7.out1, self.g7.in1),
            (self.b7.out1, self.g7.in2),
            (self.a7.out1, self.o7.in1),
            (self.b7.out1, self.o7.in2),
            (self.g7.out1, self.ae7.in1),
            (self.o7.out1, self.oe7.in1),

            (self.a8.out1, self.g8.in1),
            (self.b8.out1, self.g8.in2),
            (self.a8.out1, self.o8.in1),
            (self.b8.out1, self.o8.in2),
            (self.g8.out1, self.ae8.in1),
            (self.o8.out1, self.oe8.in1),

            (self.ae8.out1, self.or8.in1),
            (self.oe8.out1, self.or8.in2),

            (self.or8.out1, self.and8.in1),
            (self.oe7.out1, self.and8.in2),
            (self.and8.out1, self.or7.in1),
            (self.ae7.out1, self.or7.in2),

            (self.or7.out1, self.and7.in1),
            (self.oe6.out1, self.and7.in2),
            (self.and7.out1, self.or6.in1),
            (self.ae6.out1, self.or6.in2),

            (self.or6.out1, self.and6.in1),
            (self.oe5.out1, self.and6.in2),
            (self.and6.out1, self.or5.in1),
            (self.ae5.out1, self.or5.in2),

            (self.or5.out1, self.and5.in1),
            (self.oe4.out1, self.and5.in2),
            (self.and5.out1, self.or4.in1),
            (self.ae4.out1, self.or4.in2),

            (self.or4.out1, self.and4.in1),
            (self.oe3.out1, self.and4.in2),
            (self.and4.out1, self.or3.in1),
            (self.ae3.out1, self.or3.in2),

            (self.or3.out1, self.and3.in1),
            (self.oe2.out1, self.and3.in2),
            (self.and3.out1, self.or2.in1),
            (self.ae2.out1, self.or2.in2),

            (self.or2.out1, self.and2.in1),
            (self.oe1.out1, self.and2.in2),
            (self.and2.out1, self.or1.in1),
            (self.ae1.out1, self.or1.in2),

            (self.or1.out1, self.re.in1)
        )


class ADD8(Circuit):
    ELEMENTS = {
        HADD: ("g8",),
        ADD: ("g2", "g3", "g4", "g5", "g6", "g7", "g1", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "j1", "j2", "j3", "j4", "j5", "j6", "j7", "j8"),
        Bridge: ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "g9")
    }

    def inout(self):
        return {
            "in1": self.a1.in1,
            "in2": self.a2.in1,
            "in3": self.a3.in1,
            "in4": self.a4.in1,
            "in5": self.a5.in1,
            "in6": self.a6.in1,
            "in7": self.a7.in1,
            "in8": self.a8.in1,
            "in9": self.b1.in1,
            "in10": self.b2.in1,
            "in11": self.b3.in1,
            "in12": self.b4.in1,
            "in13": self.b5.in1,
            "in14": self.b6.in1,
            "in15": self.b7.in1,
            "in16": self.b8.in1,
            "out1": self.g8.out1,
            "out2": self.g7.out1,
            "out3": self.g6.out1,
            "out4": self.g5.out1,
            "out5": self.g4.out1,
            "out6": self.g3.out1,
            "out7": self.g2.out1,
            "out8": self.g1.out1,
            "out9": self.g1.out2
        }

    def connect(self):
        return (
            (self.a8.out1, self.g8.in1),
            (self.b8.out1, self.g8.in2),

            (self.g8.out2, self.g7.in1),
            (self.a7.out1, self.g7.in2),
            (self.b7.out1, self.g7.in3),

            (self.g7.out2, self.g6.in1),
            (self.a6.out1, self.g6.in2),
            (self.b6.out1, self.g6.in3),

            (self.g6.out2, self.g5.in1),
            (self.a5.out1, self.g5.in2),
            (self.b5.out1, self.g5.in3),

            (self.g5.out2, self.g4.in1),
            (self.a4.out1, self.g4.in2),
            (self.b4.out1, self.g4.in3),

            (self.g4.out2, self.g3.in1),
            (self.a3.out1, self.g3.in2),
            (self.b3.out1, self.g3.in3),

            (self.g3.out2, self.g2.in1),
            (self.a2.out1, self.g2.in2),
            (self.b2.out1, self.g2.in3),

            (self.g2.out2, self.g1.in1),
            (self.a1.out1, self.g1.in2),
            (self.b1.out1, self.g1.in3),
        )


class ALU(Circuit):
    pass
