"""
Package to facilitate converting kHs One presets

Original ActionScript code courtesy of Kilohearts
Python version started by Jason Gillman Jr.
"""

from utils import convert_magic, range_pop, read_b_uint, write_uint_b
from typing import Union
from collections import OrderedDict
from pathlib import Path
import lxml.etree as et
import struct
import base64


CURRENT_VERSION = 1014


class Parameter:
    """
    A kHs ONE Preset Parameter
    """
    def __init__(self, name: str, param_type: str = 'number', steps: int = -1):
        self.name = name
        self.param_type = param_type
        self.steps = steps
        self.normalized_value = float(0)

    def get_logical_value(self) -> float:
        if self.steps != -1:
            logical_value = round(self.normalized_value * (self.steps - 1))
        else:
            logical_value = self.normalized_value

        return logical_value

    def set_logical_value(self, logical_value: float) -> None:
        logical_value = float(logical_value)  # Just in case it doesn't come in as one
        if self.steps != -1:
            self.normalized_value = logical_value / (self.steps - 1)
        else:
            self.normalized_value = logical_value

    def get_formatted_value(self) -> str:
        if self.param_type == 'boolean':
            formatted_value = 'true' if self.normalized_value > float(0.5) else 'false'
        else:
            formatted_value = str(self.get_logical_value())

        return formatted_value

    def set_formatted_value(self, formatted_value: str) -> None:
        if self.param_type == 'boolean':
            self.normalized_value = 1 if formatted_value == 'true' else 0
        else:
            self.set_logical_value(float(formatted_value))

    def get_xml(self) -> et.Element:
        """
        Return an XML element of the parameter
        :return:
        """
        attributes = {
            'property': self.name,
            'type': self.param_type,
        }
        if self.param_type == 'number' and float(self.get_formatted_value()) % 1 == 0:
            tvalue = int(float(self.get_formatted_value()))
        else:
            tvalue = self.get_formatted_value()
        element = et.Element('Value', attrib=attributes)
        element.text = str(tvalue)
        return element


class Preset:
    """
    A kHs ONE Preset
    """
    def __init__(self):
        """
        We're basically instantiating a shit ton of Parameters here
        But doing some other stuff as well
        """
        self.name = None
        self.version = None

        self.parameters = OrderedDict()

        self.parameters['OSC_1_WAVEFORM'] = Parameter('OSC_1_WAVEFORM', 'number', 3)
        self.parameters['OSC_1_GAIN'] = Parameter('OSC_1_GAIN')
        self.parameters['OSC_1_PW'] = Parameter('OSC_1_PW')
        self.parameters['OSC_1_OCTAVE'] = Parameter('OSC_1_OCTAVE', 'number', 11)
        self.parameters['OSC_1_SEMI'] = Parameter('OSC_1_SEMI', 'number', 23)
        self.parameters['OSC_1_CENTS'] = Parameter('OSC_1_CENTS', 'number', 199)

        self.parameters['OSC_2_WAVEFORM'] = Parameter('OSC_2_WAVEFORM', 'number', 3)
        self.parameters['OSC_2_GAIN'] = Parameter('OSC_2_GAIN')
        self.parameters['OSC_2_PW'] = Parameter('OSC_2_PW')
        self.parameters['OSC_2_OCTAVE'] = Parameter('OSC_2_OCTAVE', 'number', 11)
        self.parameters['OSC_2_SEMI'] = Parameter('OSC_2_SEMI', 'number', 23)
        self.parameters['OSC_2_CENTS'] = Parameter('OSC_2_CENTS', 'number', 199)

        self.parameters['OSC_SUB_SHAPE'] = Parameter('OSC_SUB_SHAPE')
        self.parameters['OSC_SUB_GAIN'] = Parameter('OSC_SUB_GAIN')
        self.parameters['OSC_SUB_OCTAVE'] = Parameter('OSC_SUB_OCTAVE', 'number', 11)

        self.parameters['AMP_ENV_A'] = Parameter('AMP_ENV_A')
        self.parameters['AMP_ENV_D'] = Parameter('AMP_ENV_D')
        self.parameters['AMP_ENV_S'] = Parameter('AMP_ENV_S')
        self.parameters['AMP_ENV_R'] = Parameter('AMP_ENV_R')

        self.parameters['FILTER_ENV_A'] = Parameter('FILTER_ENV_A')
        self.parameters['FILTER_ENV_D'] = Parameter('FILTER_ENV_D')
        self.parameters['FILTER_ENV_S'] = Parameter('FILTER_ENV_S')
        self.parameters['FILTER_ENV_R'] = Parameter('FILTER_ENV_R')

        self.parameters['FILTER_1_CUTOFF'] = Parameter('FILTER_1_CUTOFF')
        self.parameters['FILTER_1_Q'] = Parameter('FILTER_1_Q')
        self.parameters['FILTER_1_ENV_AMT'] = Parameter('FILTER_1_ENV_AMT')
        self.parameters['FILTER_1_MODE'] = Parameter('FILTER_1_MODE', 'number', 4)
        self.parameters['FILTER_1_KEY_TRACK'] = Parameter('FILTER_1_KEY_TRACK')

        self.parameters['SHAPER_MODE'] = Parameter('SHAPER_MODE', 'number', 4)
        self.parameters['SHAPER_GAIN'] = Parameter('SHAPER_GAIN')
        self.parameters['SHAPER_MIX'] = Parameter('SHAPER_MIX')

        self.parameters['FILTER_2_CUTOFF'] = Parameter('FILTER_2_CUTOFF')
        self.parameters['FILTER_2_Q'] = Parameter('FILTER_2_Q')
        self.parameters['FILTER_2_ENV_AMT'] = Parameter('FILTER_2_ENV_AMT')
        self.parameters['FILTER_2_MODE'] = Parameter('FILTER_2_MODE', 'number', 4)
        self.parameters['FILTER_2_KEY_TRACK'] = Parameter('FILTER_2_KEY_TRACK')

        self.parameters['CHORUS_DELAY'] = Parameter('CHORUS_DELAY')
        self.parameters['CHORUS_RATE'] = Parameter('CHORUS_RATE')
        self.parameters['CHORUS_DEPTH'] = Parameter('CHORUS_DEPTH')
        self.parameters['CHORUS_WIDTH'] = Parameter('CHORUS_WIDTH')
        self.parameters['CHORUS_MIX'] = Parameter('CHORUS_MIX')

        self.parameters['DELAY_TIME'] = Parameter('DELAY_TIME')
        self.parameters['DELAY_FEEDBACK'] = Parameter('DELAY_FEEDBACK')
        self.parameters['DELAY_WIDTH'] = Parameter('DELAY_WIDTH')
        self.parameters['DELAY_SEND'] = Parameter('DELAY_SEND')
        self.parameters['DELAY_SYNC'] = Parameter('DELAY_SYNC', 'number', 2)

        self.parameters['CONF_PITCH_BEND_RANGE'] = Parameter('CONF_PITCH_BEND_RANGE', 'number', 49)
        self.parameters['CONF_UNISON_VOICES'] = Parameter('CONF_UNISON_VOICES', 'number', 8)
        self.parameters['CONF_UNISON_DETUNE'] = Parameter('CONF_UNISON_DETUNE')
        self.parameters['CONF_UNISON_WIDTH'] = Parameter('CONF_UNISON_WIDTH')
        self.parameters['CONF_PORTAMENTO_TIME'] = Parameter('CONF_PORTAMENTO_TIME')
        self.parameters['CONF_POLYPHONY'] = Parameter('CONF_POLYPHONY', 'number', 24)

        self.parameters['MOD_WHEEL_TARGET_1'] = Parameter('MOD_WHEEL_TARGET_1', 'number', 48)
        self.parameters['MOD_WHEEL_AMT_1'] = Parameter('MOD_WHEEL_AMT_1')
        self.parameters['MOD_WHEEL_TARGET_2'] = Parameter('MOD_WHEEL_TARGET_2', 'number', 48)
        self.parameters['MOD_WHEEL_AMT_2'] = Parameter('MOD_WHEEL_AMT_2')
        self.parameters['MOD_WHEEL_TARGET_3'] = Parameter('MOD_WHEEL_TARGET_3', 'number', 48)
        self.parameters['MOD_WHEEL_AMT_3'] = Parameter('MOD_WHEEL_AMT_3')

        self.parameters['MOD_ENV_A'] = Parameter('MOD_ENV_A')
        self.parameters['MOD_ENV_D'] = Parameter('MOD_ENV_D')
        self.parameters['MOD_ENV_S'] = Parameter('MOD_ENV_S')
        self.parameters['MOD_ENV_R'] = Parameter('MOD_ENV_R')

        self.parameters['MOD_ENV_TARGET_1'] = Parameter('MOD_ENV_TARGET_1', 'number', 26)
        self.parameters['MOD_ENV_AMT_1'] = Parameter('MOD_ENV_AMT_1')
        self.parameters['MOD_ENV_TARGET_2'] = Parameter('MOD_ENV_TARGET_2', 'number', 26)
        self.parameters['MOD_ENV_AMT_2'] = Parameter('MOD_ENV_AMT_2')
        self.parameters['MOD_ENV_TARGET_3'] = Parameter('MOD_ENV_TARGET_3', 'number', 26)
        self.parameters['MOD_ENV_AMT_3'] = Parameter('MOD_ENV_AMT_3')
        self.parameters['MOD_ENV_DEPTH'] = Parameter('MOD_ENV_DEPTH')

        self.parameters['VELOCITY_TARGET_1'] = Parameter('VELOCITY_TARGET_1', 'number', 39)
        self.parameters['VELOCITY_AMT_1'] = Parameter('VELOCITY_AMT_1')
        self.parameters['VELOCITY_TARGET_2'] = Parameter('VELOCITY_TARGET_2', 'number', 39)
        self.parameters['VELOCITY_AMT_2'] = Parameter('VELOCITY_AMT_2')
        self.parameters['VELOCITY_TARGET_3'] = Parameter('VELOCITY_TARGET_3', 'number', 39)
        self.parameters['VELOCITY_AMT_3'] = Parameter('VELOCITY_AMT_3')

        self.parameters['LFO_1_RATE'] = Parameter('LFO_1_RATE')
        self.parameters['LFO_1_DEPTH'] = Parameter('LFO_1_DEPTH')
        self.parameters['LFO_1_PHASE'] = Parameter('LFO_1_PHASE')
        self.parameters['LFO_1_WAVEFORM'] = Parameter('LFO_1_WAVEFORM', 'number', 6)

        self.parameters['LFO_1_TARGET_1'] = Parameter('LFO_1_TARGET_1', 'number', 23)
        self.parameters['LFO_1_AMT_1'] = Parameter('LFO_1_AMT_1')
        self.parameters['LFO_1_TARGET_2'] = Parameter('LFO_1_TARGET_2', 'number', 23)
        self.parameters['LFO_1_AMT_2'] = Parameter('LFO_1_AMT_2')
        self.parameters['LFO_1_TARGET_3'] = Parameter('LFO_1_TARGET_3', 'number', 23)
        self.parameters['LFO_1_AMT_3'] = Parameter('LFO_1_AMT_3')
        self.parameters['LFO_1_KEY_TRACK'] = Parameter('LFO_1_KEY_TRACK')

        self.parameters['LFO_2_RATE'] = Parameter('LFO_2_RATE')
        self.parameters['LFO_2_DEPTH'] = Parameter('LFO_2_DEPTH')
        self.parameters['LFO_2_PHASE'] = Parameter('LFO_2_PHASE')
        self.parameters['LFO_2_WAVEFORM'] = Parameter('LFO_2_WAVEFORM', 'number', 6)
        self.parameters['LFO_2_SYNC'] = Parameter('LFO_2_SYNC', 'boolean')
        self.parameters['LFO_2_SAMPLE_HOLD'] = Parameter('LFO_2_SAMPLE_HOLD', 'boolean')

        self.parameters['LFO_2_TARGET_1'] = Parameter('LFO_2_TARGET_1', 'number', 46)
        self.parameters['LFO_2_AMT_1'] = Parameter('LFO_2_AMT_1')
        self.parameters['LFO_2_TARGET_2'] = Parameter('LFO_2_TARGET_2', 'number', 46)
        self.parameters['LFO_2_AMT_2'] = Parameter('LFO_2_AMT_2')
        self.parameters['LFO_2_TARGET_3'] = Parameter('LFO_2_TARGET_3', 'number', 46)
        self.parameters['LFO_2_AMT_3'] = Parameter('LFO_2_AMT_3')

        self.parameters['MASTER_GAIN'] = Parameter('MASTER_GAIN')
        self.parameters['MASTER_LIMITER_ENABLED'] = Parameter('MASTER_LIMITER_ENABLED', 'boolean')
        self.parameters['MASTER_EQ_GAIN_LOW'] = Parameter('MASTER_EQ_GAIN_LOW')
        self.parameters['MASTER_EQ_GAIN_HIGH'] = Parameter('MASTER_EQ_GAIN_HIGH')
        self.parameters['MASTER_EQ_FREQ_LOW'] = Parameter('MASTER_EQ_FREQ_LOW')
        self.parameters['MASTER_EQ_FREQ_HIGH'] = Parameter('MASTER_EQ_FREQ_HIGH')

        self.parameters['CONF_LEGATO'] = Parameter('CONF_LEGATO', 'boolean')
        self.parameters['CONF_AUTO_GLIDE'] = Parameter('CONF_AUTO_GLIDE', 'boolean')

        self.parameters['OSC_1_SYNC'] = Parameter('OSC_1_SYNC')
        self.parameters['OSC_2_SYNC'] = Parameter('OSC_2_SYNC')

        self.param_keys = self.parameters.keys()  # Mostly so we can access the ordered dict by index

        # Treat these different - I believe these are Reason specific
        self.delay_time_ms = Parameter('DELAY_TIME_MS')  # Derives from DELAY_TIME
        self.delay_time_16 = Parameter('DELAY_TIME_16TH', 'number', 24)  # Derives from DELAY_TIME
        self.lfo2_rate_free = Parameter('LFO_2_RATE_FREE')  # Derives from LFO_2_RATE
        self.lfo2_rate_sync = Parameter('LFO_2_RATE_SYNC', 'number', 24)  # Derives from LFO_2_RATE

        self.re_exclude_params = ['LFO_2_RATE', 'DELAY_TIME', 'MOD_ENV_DEPTH']

    def save_re(self) -> bytes:
        """
        Return a bytes object of the Reason format
        :return:
        """

        # Boilerplate
        jukebox_patch = et.Element('JukeboxPatch', version='1.0')

        dnie = et.Element('DeviceNameInEnglish')
        dnie.text = 'kiloHearts kHs ONE'
        jukebox_patch.append(dnie)

        jbprops = et.Element('Properties', deviceProductID='com.kilohearts.khsONE', deviceVersion='0.0.1')
        jbprops_o = et.Element('Object', name='custom_properties')
        # End boilerplate

        # Reason special snowflakes
        dt = self.parameters['DELAY_TIME']
        l2r = self.parameters['LFO_2_RATE']
        self.delay_time_ms.normalized_value = pow(dt.normalized_value, float(0.25))
        self.delay_time_16.normalized_value = dt.normalized_value
        self.lfo2_rate_free.normalized_value = l2r.normalized_value
        self.lfo2_rate_sync.normalized_value = l2r.normalized_value

        for pn, pd in self.parameters.items():
            if pn not in self.re_exclude_params:
                jbprops_o.append(pd.get_xml())

        jbprops_o.append(self.delay_time_ms.get_xml())
        jbprops_o.append(self.delay_time_16.get_xml())
        jbprops_o.append(self.lfo2_rate_free.get_xml())
        jbprops_o.append(self.lfo2_rate_sync.get_xml())

        jbprops.append(jbprops_o)
        jukebox_patch.append(jbprops)

        jbprops.append(jbprops_o)
        jukebox_patch.append(jbprops)

        return et.tostring(jukebox_patch, encoding='UTF-8', xml_declaration=True, pretty_print=True)

    def save_au(self) -> bytes:
        """
        Return a bytes object of the AU format
        :return:
        """
        dctyp = '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
        plist = et.Element('plist', version='1.0')

        pld_dict = {
            'manufacturer': ('integer', 543901811),
            'name': ('string', self.name),
            'subtype': ('integer', 1799910193),
            'type': ('integer', 1635085685),
            'version': ('integer', 1),
            'vstdata': ('data', base64.b64encode(self.save_fxp()).decode('utf-8')),
        }
        pld = et.Element('dict')
        for k, v in pld_dict.items():
            t = et.Element('key')
            t.text = k
            pld.append(t)

            t = et.Element(v[0])
            t.text = str(v[1])
            pld.append(t)

        plist.append(pld)

        return et.tostring(plist, encoding='UTF-8', xml_declaration=True, pretty_print=True, doctype=dctyp)

    def save_fxp(self) -> bytes:
        """
        Return a bytes object of the FXP format
        :return:
        """
        data = bytearray()
        data += write_uint_b(convert_magic('FPCh'))
        data += write_uint_b(1)
        data += write_uint_b(convert_magic('kHs1'))
        data += write_uint_b(self.version)
        data += write_uint_b(len(self.parameters))

        cropped_name = self.name[0:24] if len(self.name) >= 24 else self.name
        data += cropped_name.encode('utf-8')
        for x in range(0, 28 - len(cropped_name)):
            data += b'\x00'  # Spoiler alert: I'm a dumbass and found out bytes(0) doesn't work like I expected...

        chunk_data = self.save_to_chunk()
        data += write_uint_b(len(chunk_data))
        data += chunk_data

        final_data = bytearray()
        final_data += write_uint_b(convert_magic('CcnK'))
        final_data += write_uint_b(len(data))
        final_data += data

        return final_data

    def save_to_chunk(self) -> bytes:
        """
        This does... something
        :return:
        """
        data = bytearray()
        data += write_uint_b(self.version, False)
        data += write_uint_b(len(self.parameters), False)
        for x in self.parameters.values():
            data += struct.pack('<f', x.normalized_value)

        return data


def process_re(xml_data: bytes, preset_file: Path = Path('Test.file')) -> Union[Preset, None]:  # Preset name from file
    """
    Kick out a Reason Preset
    :param xml_data:
    :param preset_file:
    :return:
    """
    jukebox_xml = et.XML(xml_data)

    device_product_id = jukebox_xml[1].get('deviceProductID')
    if device_product_id != 'com.kilohearts.khsONE':
        print('Preset does not seem to be for kHs ONE')
        return None

    custom_properties = jukebox_xml[1][0]

    preset = Preset()
    preset.name = preset_file.stem

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


def process_au(xml_data: bytes) -> Union[Preset, None]:
    """
    Kick out an AU Preset
    :param xml_data:
    :return:
    """
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


def process_fxp(data: bytes) -> Union[Preset, None]:
    """
    Kick out an FXP Preset
    :param data:
    :return:
    """
    preset = Preset()

    data = bytearray(data)  # Now with 100% more mutability!

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

    if not read_chunk_into_preset(preset, chunk_data):
        print('Preset chunk data load failure')
        return None

    preset.name = preset.name.rstrip('\x00')
    return preset


def read_chunk_into_preset(preset: Preset, chunk_data: bytearray) -> bool:
    """
    Load chunk data into the preset
    :param preset:
    :param chunk_data:
    :return:
    """
    preset.version = read_b_uint(chunk_data, False)
    read_b_uint(chunk_data, False)  # param_count = read_b_uint(chunk_data, False)
    for k in preset.param_keys:
        preset.parameters[k].normalized_value = struct.unpack('<f', range_pop(chunk_data, 0, 4))[0]

    return True


def find_au_value(plist_xml_bytes: bytes, search_key: str) -> Union[et.Element, None]:
    """
    Get a particular value based on the key
    :param plist_xml_bytes:
    :param search_key:
    :return:
    """
    plist = et.XML(plist_xml_bytes)

    result_idx = None

    for i, x in enumerate(plist[0]):
        if x.tag == 'key' and x.text == search_key:
            result_idx = i + 1
            break

    if result_idx is not None:
        return plist[0][result_idx]
