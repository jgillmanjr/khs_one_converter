"""
Package to facilitate converting kHs One presets

Original ActionScript code courtesy of Kilohearts
Python version started by Jason Gillman Jr.
"""

__all__ = ['process_fxp', 'process_au', 'process_re']

from .main import insert_param_chunk_into_fxp_preset, Parameter, Preset
from .utils import convert_magic, find_au_value, range_pop, read_b_uint
from typing import Union
from pathlib import Path
import lxml.etree as et
import base64


CURRENT_VERSION = 1014


def process_re(preset_file: Path) -> Union[Preset, None]:  # Preset name from file
    """
    Parse a Reason Preset
    :param preset_file:
    :return:
    """
    jukebox_xml = et.XML(preset_file.read_bytes())

    device_product_id = jukebox_xml[1].get('deviceProductID')
    if device_product_id != 'com.kilohearts.khsONE':
        print('Preset does not seem to be for kHs ONE')
        return None

    custom_properties = jukebox_xml[1][0]

    preset = Preset()
    preset.name = preset_file.stem
    preset.version = CURRENT_VERSION  # Because we don't have that information from the repatch file

    dt16: Parameter
    dtms: Parameter
    l2rs: Parameter
    l2rf: Parameter
    xfer_params = {}
    for x in custom_properties:
        param = x.get('property')
        if param in preset.parameters:
            preset.parameters[param].set_formatted_value(x.text)
        else:
            xfer_params[param] = Parameter(param, x.get('type'))
            xfer_params[param].set_formatted_value(x.text)

    dt16 = xfer_params['DELAY_TIME_16TH']
    dtms = xfer_params['DELAY_TIME_MS']
    if preset.parameters['DELAY_SYNC'].get_formatted_value():
        preset.delay_time_16.set_formatted_value(dt16.get_formatted_value())
        preset.parameters['DELAY_TIME'].set_formatted_value(dt16.get_formatted_value())
    else:
        preset.delay_time_ms.set_formatted_value(dtms.get_formatted_value())
        preset.parameters['DELAY_TIME'].set_formatted_value(str(pow(dtms.normalized_value, float(4))))

    l2rs = xfer_params['LFO_2_RATE_SYNC']
    l2rf = xfer_params['LFO_2_RATE_FREE']
    if preset.parameters['LFO_2_SYNC'].get_formatted_value():
        preset.lfo2_rate_sync.set_formatted_value(l2rs.get_formatted_value())
        preset.parameters['LFO_2_RATE'].set_formatted_value(l2rs.get_formatted_value())
    else:
        preset.lfo2_rate_free.set_formatted_value(l2rf.get_formatted_value())
        preset.parameters['LFO_2_RATE'].set_formatted_value(l2rf.get_formatted_value())

    return preset


def process_au(preset_file: Path) -> Union[Preset, None]:
    """
    Parse an AU Preset
    :param preset_file:
    :return:
    """
    xml_data = et.XML(preset_file.read_bytes())
    fx_id = int(find_au_value(xml_data, 'subtype').text)
    if fx_id != convert_magic('kHs1'):
        print('Preset does not appear to be for kHs ONE')
        return None

    fxp_data = base64.b64decode(find_au_value(xml_data, 'vstdata').text, validate=True)

    preset = process_fxp(fxp_data)

    if isinstance(preset, Preset):
        preset.name = find_au_value(xml_data, 'name').text
        return preset

    return None


def process_fxp(preset_data: Union[Path, bytes]) -> Union[Preset, None]:
    """
    Parse an FXP Preset
    :param preset_data:
    :return:
    """
    preset = Preset()

    if isinstance(preset_data, Path):
        data = bytearray(preset_data.read_bytes())  # Now with 100% more mutability! Probably should bytestream it, tho
    else:
        data = bytearray(preset_data)  # I think Rush once said "Why does it happen? Because it happens: Roll the bones"

    chunk_magic = read_b_uint(data)
    read_b_uint(data)  # size = read_b_uint(data)
    fx_magic = read_b_uint(data)
    read_b_uint(data)  # format_version = read_b_uint(data)
    fx_id = read_b_uint(data)
    preset.version = read_b_uint(data)
    read_b_uint(data)  # num_params = read_b_uint(data)
    preset.name = range_pop(data, 0, 28).decode('utf-8')
    chunk_size = read_b_uint(data)
    chunk_data = range_pop(data, 0, chunk_size)

    if chunk_magic != convert_magic('CcnK'):
        print('Invalid chunkMagic')
        return None

    if fx_magic != convert_magic('FPCh'):
        print('Unsupported fxMagic')
        return None

    if fx_id != convert_magic('kHs1'):
        print('Preset does not seem to be for kHs ONE')
        return None

    if preset.version < CURRENT_VERSION:
        print('Presets saved with a version of kHs ONE earlier than 1.014 are not supported')
        return None

    if not insert_param_chunk_into_fxp_preset(preset, chunk_data):
        print('Preset chunk data load failure')
        return None

    preset.name = preset.name.rstrip('\x00')
    return preset
