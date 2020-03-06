"""
Bank stuff
"""
from .utils import convert_magic, read_b_uint, range_pop, write_uint_b, CURRENT_VERSION
from .preset import Preset, process_fxp
from pathlib import Path
from typing import List, Union
import base64


def return_bank_presets(bank_prog_data: bytearray, prog_count: int = 100) -> List['Preset']:
    """
    Get the programs from the bank
    :param bank_prog_data:
    :param prog_count:
    :return:
    """
    version = read_b_uint(bank_prog_data, False)

    preset_list = []

    for i in range(0, prog_count, 1):
        preset = Preset()
        preset.version = version
        preset.name = range_pop(bank_prog_data, 0, 24).decode('utf-8').rstrip('\x00')  # Could still be padded...

        param_chunk_size = read_b_uint(bank_prog_data, False)
        param_chunk_data = range_pop(bank_prog_data, 0, param_chunk_size)

        if not preset.insert_param_chunk_into_fxp_preset(param_chunk_data):
            print(f'Preset chunk data load failure for bank program: {preset.name}')
            continue  # I think we can get away with skipping the preset

        preset_list.append(preset)

    return preset_list


class Bank:
    """
    A VST Bank (FXB)
    """
    def __init__(self, presets: Union[List['Preset'], None] = None) -> None:
        """
        Construct the bank object
        :param presets:
        """
        if presets is None:
            self.presets = []
        elif len(presets) <= 100:
            self.presets = presets
        else:
            print('Preset count is more than 100. Only adding first 100')
        self.presets = presets if presets is not None else []

    def add_preset(self, preset: 'Preset') -> None:
        if len(self.presets) >= 100:
            print('Bank already has 100 presets. Unable to add more.')
            return None

        self.presets.append(preset)
        return None

    def return_bank_data(self) -> bytes:
        """
        Return data representing an FXB file
        :return:
        """
        # @TODO: This doesn't work yet - fix me
        bank_bytes = bytes()

        bank_bytes += write_uint_b(convert_magic('FBCh'))
        bank_bytes += write_uint_b(1)
        bank_bytes += write_uint_b(convert_magic('kHs1'))
        bank_bytes += write_uint_b(CURRENT_VERSION)

        bank_bytes += write_uint_b(100)
        for i in range(0, 128, 1):
            bank_bytes += b'\x00'

        preset_data = self._build_bank_chunk()

        bank_bytes += write_uint_b(len(preset_data))
        bank_bytes += preset_data

        r_data = write_uint_b(convert_magic('CcnK'))
        r_data += write_uint_b(len(bank_bytes))
        r_data += bank_bytes

        return r_data

    def _build_bank_chunk(self) -> bytes:
        """
        Returns the preset data
        :return:
        """
        preset_list_len = len(self.presets)
        if preset_list_len > 100:
            print('Preset count greater than 100. Only using the first 100.')
            presets = self.presets[:100]
        elif preset_list_len < 100:
            print('Preset count less than 100. Padding with the Init Patch.')
            presets = self.presets[:]
            init_preset_data = base64.b64decode(Path(__file__).parent.joinpath('init_patch.b64').read_text(),
                                                validate=True)
            for i in range(0, 100 - preset_list_len, 1):
                presets.append(process_fxp(init_preset_data))
        else:
            presets = self.presets[:]

        chunk_data = bytes()
        chunk_data += write_uint_b(CURRENT_VERSION, False)

        for p in presets:
            cropped_name = p.name[0:24] if len(p.name) >= 24 else p.name
            chunk_data += cropped_name.encode('utf-8')
            for x in range(0, 28 - len(cropped_name)):
                chunk_data += b'\x00'
            p_data = p.return_fxp_param_chunk()
            chunk_data += write_uint_b(len(p_data), False)
            chunk_data += p_data

        return chunk_data


def process_fxb(bank_file: Path) -> Union[Bank, None]:
    """
    Parse an FXB Bank
    :param bank_file:
    :return:
    """

    data = bytearray(bank_file.read_bytes())

    chunk_magic = read_b_uint(data)
    read_b_uint(data)  # size = read_b_uint(data)
    fx_magic = read_b_uint(data)
    read_b_uint(data)  # format_version = read_b_uint(data)
    fx_id = read_b_uint(data)
    version = read_b_uint(data)
    num_programs = read_b_uint(data)

    range_pop(data, 0, 128)

    program_chunk_size = read_b_uint(data)
    program_chunk_data = range_pop(data, 0, program_chunk_size)

    if chunk_magic != convert_magic('CcnK'):
        print('Invalid chunkMagic')
        return None

    if fx_magic != convert_magic('FBCh'):
        print('Unsupported fxMagic')
        return None

    if fx_id != convert_magic('kHs1'):
        print('Preset does not seem to be for kHs ONE')
        return None

    if version < CURRENT_VERSION:
        print('Presets saved with a version of kHs ONE earlier than 1.014 are not supported')
        return None

    bank_presets = return_bank_presets(program_chunk_data, prog_count=num_programs)
    return Bank(bank_presets)
