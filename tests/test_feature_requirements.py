#!/usr/bin/env python
from orch.features import requirements
from orch.deconf import format_flat_dict

def test_pool():
    p = {x.name:str(x.default) for x in requirements.pool.values()}
    r = format_flat_dict(p)
    assert r


if '__main__' == __name__:
    test_pool()
