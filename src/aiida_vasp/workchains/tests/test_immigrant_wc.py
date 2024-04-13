"""Test submitting a VaspImmigrantWorkChain."""
# pylint: disable=unused-import,wildcard-import,unused-wildcard-import,unused-argument,redefined-outer-name, import-outside-toplevel
import numpy as np
import pytest

from aiida.common.extendeddicts import AttributeDict
from aiida.engine import run

from aiida_vasp.utils.aiida_utils import create_authinfo, get_data_node
from aiida_vasp.utils.fixtures import (
    fresh_aiida_env,
    localhost,
    localhost_dir,
    mock_vasp,
    phonondb_run,
    potcar_family,
    temp_pot_folder,
)
from aiida_vasp.utils.fixtures.data import POTCAR_FAMILY_NAME, POTCAR_MAP


@pytest.fixture
def immigrant_wc_builder_deprecated(fresh_aiida_env, potcar_family, phonondb_run, localhost, mock_vasp):
    """Return VaspImmigrantWorkChain builder

    Parameters
    ----------
    fresh_aiida_env() : Refresh database
    potcar_family() : Create POTCAR family
    localhost() : Computer
    phonondb_run() : pathlib.PosixPath
    mock_vasp() :Code

    Note
    ----
    The following methods have to be visible
    localhost_dir() : pathlib.Path generated by tmp_path_factory, and is used in localhost()
    temp_pot_folder() : pathlib.Path generated by tmp_path_factory, and is used in potcar_family()

    """

    from aiida.plugins import WorkflowFactory

    workchain = WorkflowFactory('vasp.immigrant')

    create_authinfo(localhost, store=True)

    builder = workchain.get_builder()
    builder.code = mock_vasp
    builder.folder_path = get_data_node('core.str', phonondb_run)
    builder.potential_family = get_data_node('core.str', POTCAR_FAMILY_NAME)
    builder.potential_mapping = get_data_node('core.dict', dict=POTCAR_MAP)
    builder.options = get_data_node(
        'core.dict',
        dict={
            'withmpi': False,
            'queue_name': 'None',
            'resources': {
                'num_machines': 1,
                'num_mpiprocs_per_machine': 1
            },
            'max_wallclock_seconds': 3600
        },
    )
    return builder


@pytest.fixture
def immigrant_wc_builder(fresh_aiida_env, potcar_family, phonondb_run, localhost, mock_vasp):
    """Return VaspImmigrantWorkChain builder

    Parameters
    ----------
    fresh_aiida_env() : Refresh database
    potcar_family() : Create POTCAR family
    localhost() : Computer
    phonondb_run() : pathlib.PosixPath
    mock_vasp() :Code

    Note
    ----
    The following methods have to be visible.
    localhost_dir() : pathlib.Path generated by tmp_path_factory, and is used in localhost()
    temp_pot_folder() : pathlib.Path generated by tmp_path_factory, and is used in potcar_family()

    """

    from aiida.plugins import WorkflowFactory

    workchain = WorkflowFactory('vasp.immigrant')

    create_authinfo(localhost, store=True)

    builder = workchain.get_builder()
    builder.code = mock_vasp
    builder.remote_workdir = str(phonondb_run)
    builder.potential_family = get_data_node('core.str', POTCAR_FAMILY_NAME)
    builder.potential_mapping = get_data_node('core.dict', dict=POTCAR_MAP)
    builder.options = get_data_node(
        'core.dict',
        dict={
            'withmpi': False,
            'queue_name': 'None',
            'resources': {
                'num_machines': 1,
                'num_mpiprocs_per_machine': 1
            },
            'max_wallclock_seconds': 3600
        },
    )
    return builder


def test_vasp_immigrant_wc(immigrant_wc_builder):
    """VaspImmigrantWorkChain test"""
    _test_vasp_immigrant_wc(immigrant_wc_builder)


def test_vasp_immigrant_wc_deprecated(immigrant_wc_builder_deprecated):  # pylint: disable=invalid-name
    """VaspImmigrantWorkChain test with deprecated input"""
    _test_vasp_immigrant_wc(immigrant_wc_builder_deprecated)


def _test_vasp_immigrant_wc(immigrant_wc_builder):
    """VaspImmigrantWorkChain test"""
    results, node = run.get_node(immigrant_wc_builder)

    assert node.exit_status == 0
    assert 'retrieved' in results
    assert 'misc' in results
    assert 'remote_folder' in results
    misc = results['misc'].get_dict()
    np.testing.assert_almost_equal(misc['total_energies']['energy_extrapolated'], -459.87614130)


def test_vasp_immigrant_wc_additional(immigrant_wc_builder):  # pylint: disable=invalid-name
    """VaspImmigrantWorkChain test"""
    _test_vasp_immigrant_wc_additional(immigrant_wc_builder)


def test_vasp_immigrant_wc_additional_deprecated(immigrant_wc_builder_deprecated):  # pylint: disable=invalid-name
    """VaspImmigrantWorkChain test with deprecated input."""
    _test_vasp_immigrant_wc_additional(immigrant_wc_builder_deprecated)


def _test_vasp_immigrant_wc_additional(immigrant_wc_builder):
    """VaspImmigrantWorkChain test"""
    immigrant_wc_builder.use_chgcar = get_data_node('core.bool', True)
    immigrant_wc_builder.use_wavecar = get_data_node('core.bool', True)
    results, node = run.get_node(immigrant_wc_builder)

    assert node.exit_status == 0
    assert 'retrieved' in results
    assert 'misc' in results
    assert 'remote_folder' in results

    calc_node = node.base.links.get_outgoing(link_label_filter='iteration_01').first().node
    assert 'charge_density' in calc_node.inputs
    assert 'wavefunctions' in calc_node.inputs