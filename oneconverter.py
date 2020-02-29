"""
Package to facilitate converting kHs One presets

Original ActionScript code courtesy of Kilohearts
Python version started by Jason Gillman Jr.
"""

from decimal import Decimal
import xml.etree.ElementTree as ET


class Parameter:
    """
    A kHs ONE Preset Parameter
    """
    def __init__(self, name: str, param_type: str = 'number', steps: int = -1):
        self.name = name
        self.param_type = param_type
        self.steps = steps
        self.normalized_value = Decimal(0)

    def get_logical_value(self):
        if self.steps != -1:
            logical_value = round(self.normalized_value * (self.steps - 1))
        else:
            logical_value = self.normalized_value

        return logical_value

    def set_logical_value(self, logical_value: Decimal):
        logical_value = Decimal(logical_value)  # Just in case it doesn't come in as one
        if self.steps != -1:
            self.normalized_value = logical_value / (self.steps - 1)
        else:
            self.normalized_value = logical_value

    def get_formatted_value(self):
        if self.param_type == 'boolean':
            formatted_value = 'true' if self.normalized_value > Decimal(0.5) else 'false'
        else:
            formatted_value = str(self.normalized_value)

        return formatted_value

    def set_formatted_value(self, formatted_value: str):
        if self.param_type == 'boolean':
            self.normalized_value = 1 if formatted_value == 'true' else 0
        else:
            self.normalized_value = Decimal(formatted_value)

    def get_xml(self):
        """
        Return an XML element of the parameter
        :return:
        """
        attributes = {
            'property': self.name,
            'type': self.param_type,
        }
        element = ET.Element('Value', attrib=attributes)
        element.text = self.get_formatted_value()
        return element

class Preset:
    """
    A kHs ONE Preset
    """
    def __init__(self, name: str, version: int = 1014):
        """
        We're basically instantiating a shit ton of Parameters here
        But doing some other stuff as well
        """
        self.name = name
        self.version = version

        # Apparently these bad johnsons were cool enough to be set independently
        self.delay_time_ms = Parameter('DELAY_TIME_MS')
        self.delay_time_16 = Parameter('DELAY_TIME_16TH', 'number', 24)
        self.lfo2_rate_free = Parameter('LFO_2_RATE_FREE')
        self.lfo2_rate_sync = Parameter('LFO_2_RATE_SYNC', 'number', 24)

        self.parameters = {}

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
        # I think MOD_ENV_DEPTH was supposed to go here, but it wasn't defined...

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
