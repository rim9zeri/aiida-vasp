"""Test the KPOINTS parser."""
# pylint: disable=unused-import,redefined-outer-name,unused-argument,unused-wildcard-import,wildcard-import

import math
import pytest
import numpy as np

from aiida_vasp.utils.fixtures import *
from aiida_vasp.utils.fixtures.testdata import data_path
from aiida_vasp.parsers.content_parsers.kpoints import KpointsParser
from aiida_vasp.utils.aiida_utils import get_data_class


@pytest.mark.parametrize(['kpoints_parser'], [('kpoints',)], indirect=True)
def test_parse_kpoints_explicit(kpoints_parser):
    """Load a reference KPOINTS parser.

    We check that it parses and provides the correct content for mesh mode.

    """

    # The kpoints for KPOINTS parser should have the key `kpoints-kpoints`
    result = kpoints_parser.get_quantity('kpoints-kpoints')
    result_ref = {
        'comment': 'K-points',
        'divisions': None,
        'shifts': None,
        'points': [[np.array([0., 0., 0.]), 1.0, True], [np.array([0., 0., 0.5]), 1.0, True]],
        'tetra': None,
        'tetra_volume': None,
        'mode': 'explicit',
        'centering': None,
        'num_kpoints': 2
    }
    compare_kpoints_content(result, result_ref)


@pytest.mark.parametrize(['kpoints_parser'], [(['kpoints', 'KPOINTS_mesh'],)], indirect=True)
def test_parse_kpoints_mesh(kpoints_parser):
    """Load a reference KPOINTS parser.

    We check that it parses and provides the correct content for mesh mode.

    """

    # The kpoints for KPOINTS parser should have the key `kpoints-kpoints`
    result = kpoints_parser.get_quantity('kpoints-kpoints')
    result_ref = {
        'comment': 'K-points',
        'divisions': [2, 2, 2],
        'shifts': [0.0, 0.0, 0.0],
        'points': None,
        'tetra': None,
        'tetra_volume': None,
        'mode': 'automatic',
        'centering': 'Monkhorst-Pack',
        'num_kpoints': 0
    }
    compare_kpoints_content(result, result_ref)


@pytest.mark.parametrize(['kpoints_parser'], [('kpoints',)], indirect=True)
def test_parse_kpoints_write(kpoints_parser, tmpdir):
    """Load a reference KPOINTS parser and check that the write functionality works.

    Here we make sure the write function of the content parser works.

    """

    # Write the loaded reference KPOINTS content to file
    temp_path = str(tmpdir.join('KPOINTS'))
    kpoints_parser.write(temp_path)
    # Load the written KPOINTS using a new content parser instance and compare
    content = None
    with open(temp_path, 'r') as handler:
        content = handler.readlines()
    ref_content = [
        '# K-points\n', '     2\n', 'Direct\n', '  0.000000000   0.000000000   0.000000000   1.000000000\n',
        '  0.000000000   0.000000000   0.500000000   1.000000000\n'
    ]
    assert content == ref_content


def test_parse_kpoints_data(vasp_kpoints, tmpdir):
    """Load a reference AiiDA KpointsData and check that the parser can
    initialize using the data.

    Using the KpointsData sitting in the initialized parser it should
    write that content to a KPOINTS file when issuing write which is also tested,
    file is reloaded and content checked.

    """

    # Initialize parser with an existing reference KpointsData
    kpoints_data, _ = vasp_kpoints
    kpoints_parser = KpointsParser(data=kpoints_data)

    # Write the loaded KpointsData to file, which behind the scenes convert it
    # to a KPOINTS format
    temp_path = str(tmpdir.join('KPOINTS'))
    kpoints_parser.write(temp_path)

    # Load the written KPOINTS using a new content parser instance and compare
    parser = None
    with open(temp_path, 'r') as handler:
        parser = KpointsParser(handler=handler)
    result = parser.get_quantity('kpoints-kpoints')
    if result['mode'] == 'automatic':
        result_ref = {
            'comment': 'No comment',
            'divisions': [2, 2, 2],
            'shifts': [0.0, 0.0, 0.0],
            'points': None,
            'tetra': None,
            'tetra_volume': None,
            'mode': 'automatic',
            'centering': 'Gamma',
            'num_kpoints': 0
        }
    else:
        result_ref = {
            'comment': 'No comment',
            'divisions': None,
            'shifts': None,
            'points': [[np.array([0., 0., 0.]), 1.0, True], [np.array([0., 0., 0.5]), 1.0, True]],
            'tetra': None,
            'tetra_volume': None,
            'mode': 'explicit',
            'centering': None,
            'num_kpoints': 2
        }
    compare_kpoints_content(result, result_ref)


def compare_kpoints_content(kpoints, kpoints_ref):
    """Compare the KPOINTS content with supplied reference data."""
    if kpoints['mode'] == 'explicit':
        kpoints_ref_no_points = dict(kpoints_ref)
        del kpoints_ref_no_points['points']
        kpoints_no_points = dict(kpoints)
        del kpoints_no_points['points']
        assert kpoints_no_points == kpoints_ref_no_points
        for index, item in enumerate(kpoints['points']):
            assert np.allclose(item[0], kpoints_ref['points'][index][0])
            assert math.isclose(item[1], kpoints_ref['points'][index][1])
            assert item[2] == kpoints_ref['points'][index][2]
    elif kpoints['mode'] == 'automatic':
        assert kpoints == kpoints_ref
