"""
DOSCAR parser.

--------------
Contains the parsing interfaces to parsevasp used to parse DOSCAR.
"""
# pylint: disable=unsubscriptable-object  # pylint/issues/3139
import numpy as np

from aiida_vasp.parsers.node_composer import NodeComposer, get_node_composer_inputs_from_object_parser
from aiida_vasp.parsers.content_parsers.parser import BaseFileParser

from parsevasp.doscar import Doscar


class DoscarParser(BaseFileParser):
    """The parser interface that enables parsing of DOSCAR.

    The parser is triggered by using the `doscar-dos` quantity key. The quantity key `dos`
    will on the other hand parse the structure using the XML parser.

    """

    DEFAULT_OPTIONS = {'quantities_to_parse': ['doscar-dos']}

    PARSABLE_QUANTITIES = {
        'doscar-dos': {
            'inputs': [],
            'name': 'dos',
            'prerequisites': [],
        },
    }

    def _init_from_handler(self, handler):
        """Initialize using a file like handler."""

        try:
            self._content_parser = Doscar(file_handler=handler, logger=self._logger)
        except SystemExit:
            self._logger.warning('Parsevasp exited abnormally.')

    @property
    def dos(self):
        """
        Return the total and partial density of states, and in addition some metadata.

        Returns
        -------
        dos : dict
            A dict containing the keys `tdos`, `pdos` and `header`, which contain
            for the two first, NumPy arrays for the total density of states and partial
            density of states, respectively.

        """
        metadata = self._content_parser.get_metadata()
        total_dos = self._content_parser.get_dos()
        partial_dos = self._content_parser.get_pdos()
        dos = {'tdos': total_dos, 'pdos': partial_dos, 'header': metadata}

        return dos
