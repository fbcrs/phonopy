import unittest
import numpy as np
from phonopy.structure.brillouin_zone import BrillouinZone
from phonopy.structure.spglib import (get_stabilized_reciprocal_mesh,
                                      relocate_BZ_grid_address)


class TestBrillouinZone(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_FCC(self):
        direct_lat = [[0, 2.73, 2.73], [2.73, 0, 2.73], [2.73, 2.73, 0]]
        mesh = [4, 4, 4]
        is_shift = [0, 0, 0]
        self._testBrillouinZone(direct_lat, mesh, is_shift)

    def test_Hexagonal(self):
        direct_lat = [[3.0751691007292523, 0, 0],
                      [-1.5375845503646262, 2.6631745621644800, 0],
                      [0, 0, 3.5270080068586522]]
        mesh = [4, 4, 4]
        is_shift = [0, 0, 0]
        self._testBrillouinZone(direct_lat, mesh, is_shift)

    def _testBrillouinZone(self, direct_lat, mesh, is_shift):
        _, grid_address = get_stabilized_reciprocal_mesh(
            mesh,
            rotations=[np.eye(3, dtype='intc'), ],
            is_shift=is_shift)
        rec_lat = np.linalg.inv(direct_lat)
        bz_grid_address, bz_map = relocate_BZ_grid_address(
            grid_address,
            mesh,
            rec_lat,
            is_shift=is_shift)

        qpoints = (grid_address + np.array(is_shift) / 2.0) / mesh
        bz = BrillouinZone(rec_lat)
        bz.run(qpoints)
        sv_all = bz.shortest_qpoints  # including BZ boundary duplicates
        sv = [v[0] for v in sv_all]
        bz_qpoints = (bz_grid_address + np.array(is_shift) / 2.0) / mesh
        d2_this = (np.dot(sv, rec_lat.T) ** 2).sum(axis=1)
        d2_spglib = (np.dot(bz_qpoints[:np.prod(mesh)],
                            rec_lat.T) ** 2).sum(axis=1)
        diff = d2_this - d2_spglib
        diff -= np.rint(diff)

        # Following both of two tests are necessary.
        # Check equivalence of vectors by lattice translation
        np.testing.assert_allclose(diff, 0, atol=1e-8)
        # Check being in same (hopefull first) Brillouin zone by their lengths
        np.testing.assert_allclose(d2_this, d2_spglib, atol=1e-8)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBrillouinZone)
    unittest.TextTestRunner(verbosity=2).run(suite)
