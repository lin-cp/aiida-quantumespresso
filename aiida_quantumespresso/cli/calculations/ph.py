# -*- coding: utf-8 -*-
"""Command line scripts to launch a `PhCalculation` for testing and demonstration purposes."""
from aiida.cmdline.params import options as options_core
from aiida.cmdline.params import types
from aiida.cmdline.utils import decorators
import click

from . import cmd_launch
from ..utils import launch, options


@cmd_launch.command('ph')
@options_core.CODE(required=True, type=types.CodeParamType(entry_point='quantumespresso.ph'))
@options_core.CALCULATION(required=True)
@options.KPOINTS_MESH(default=[1, 1, 1])
@options.MAX_NUM_MACHINES()
@options.MAX_WALLCLOCK_SECONDS()
@options.WITH_MPI()
@options.DAEMON()
@decorators.with_dbenv()
def launch_calculation(code, kpoints_mesh, calculation, max_num_machines, max_wallclock_seconds, with_mpi, daemon):
    """Run a PhCalculation."""
    from aiida import orm
    from aiida.plugins import CalculationFactory

    from aiida_quantumespresso.utils.resources import get_default_options

    # Check that the parent calculation node comes from quantumespresso.pw.
    # I cannot move this check into the option declaration, because CalcJobNode is not subclassed by the specific
    # calculation plugins (only Process is), and there is no feature yet to filter by the associated process_type.
    expected_process_type = 'aiida.calculations:quantumespresso.pw'
    if calculation.process_type != expected_process_type:
        raise click.BadParameter(
            f'input calculation node has process_type: {calculation.process_type}; should be {expected_process_type}'
        )

    parent_folder = calculation.get_outgoing(node_class=orm.RemoteData, link_label_filter='remote_folder').one().node

    inputs = {
        'code': code,
        'qpoints': kpoints_mesh,
        'parameters': orm.Dict(dict={'INPUTPH': {}}),
        'parent_folder': parent_folder,
        'metadata': {
            'options': get_default_options(max_num_machines, max_wallclock_seconds, with_mpi),
        }
    }

    launch.launch_process(CalculationFactory('quantumespresso.ph'), daemon, **inputs)
