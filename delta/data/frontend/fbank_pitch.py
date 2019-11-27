# Copyright (C) 2017 Beijing Didi Infinity Technology and Development Co.,Ltd.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import delta.compat as tf
from delta.utils.hparam import HParams
from delta.data.frontend.base_frontend import BaseFrontend
from delta.data.frontend.pitch import Pitch
from delta.data.frontend.fbank import Fbank

class FbankPitch(BaseFrontend):

  def __init__(self, config: dict):
    super().__init__(config)
    self.fbank = Fbank(config)
    self.pitch = Pitch(config)

  @classmethod
  def params(cls, config=None):
    """
    Set params.
    :param config: contains eight optional parameters:upper_frequency_limit(float, default=4000.0),
    lower_frequency_limit(float, default=20.0), filterbank_channel_count(float, default=40.0),
    window_length(float, default=0.025), frame_length(float, default=0.010),
    thres_autoc(float, default=0.3), output_type(int, default=2), sample_rate(int, default=16000).
    :return: An object of class HParams, which is a set of hyperparameters as name-value pairs.
    """
    hparams = HParams(cls=cls)

    upper_frequency_limit = 0
    lower_frequency_limit = 20.0
    filterbank_channel_count = 23.0
    window_length = 0.025
    frame_length = 0.010
    raw_energy = 1
    preeph_coeff = 0.97
    window_type = 'povey'
    remove_dc_offset = True
    is_fbank = True
    output_type = 1
    sample_rate = 16000
    snip_edges = True
    preemph_coeff = 0.0
    min_f0 = 50.0
    max_f0 = 400.0
    soft_min_f0 = 10.0
    penalty_factor = 0.1
    lowpass_cutoff = 1000.0
    resample_freq = 4000.0
    delta_pitch = 0.005
    nccf_ballast = 7000.0
    lowpass_filter_width = 1
    upsample_filter_width = 5
    max_frames_latency = 0
    frames_per_chunk = 0
    simulate_first_pass_online = False
    recompute_frame = 500
    nccf_ballast_online = False

    hparams.add_hparam('sample_rate', sample_rate)
    hparams.add_hparam('snip_edges', snip_edges)
    hparams.add_hparam('preemph_coeff', preemph_coeff)
    hparams.add_hparam('min_f0', min_f0)
    hparams.add_hparam('max_f0', max_f0)
    hparams.add_hparam('soft_min_f0', soft_min_f0)
    hparams.add_hparam('penalty_factor', penalty_factor)
    hparams.add_hparam('lowpass_cutoff', lowpass_cutoff)
    hparams.add_hparam('resample_freq', resample_freq)
    hparams.add_hparam('delta_pitch', delta_pitch)
    hparams.add_hparam('nccf_ballast', nccf_ballast)
    hparams.add_hparam('lowpass_filter_width', lowpass_filter_width)
    hparams.add_hparam('upsample_filter_width', upsample_filter_width)
    hparams.add_hparam('max_frames_latency', max_frames_latency)
    hparams.add_hparam('frames_per_chunk', frames_per_chunk)
    hparams.add_hparam('simulate_first_pass_online', simulate_first_pass_online)
    hparams.add_hparam('recompute_frame', recompute_frame)
    hparams.add_hparam('nccf_ballast_online', nccf_ballast_online)
    hparams.add_hparam('upper_frequency_limit', upper_frequency_limit)
    hparams.add_hparam('lower_frequency_limit', lower_frequency_limit)
    hparams.add_hparam('filterbank_channel_count', filterbank_channel_count)
    hparams.add_hparam('window_length', window_length)
    hparams.add_hparam('frame_length', frame_length)
    hparams.add_hparam('output_type', output_type)
    hparams.add_hparam('raw_energy', raw_energy)
    hparams.add_hparam('preeph_coeff', preeph_coeff)
    hparams.add_hparam('window_type', window_type)
    hparams.add_hparam('remove_dc_offset', remove_dc_offset)
    hparams.add_hparam('is_fbank', is_fbank)

    if config is not None:
      hparams.override_from_dict(config)

    return hparams

  def call(self, audio_data, sample_rate=None):
    """
    Caculate fbank && pitch(concat) features of wav.
    :param audio_data: the audio signal from which to compute spectrum. Should be an (1, N) tensor.
    :param sample_rate: [option]the samplerate of the signal we working with, default is 16kHz.
    :return: A tensor with shape (num_frames, dim_features), containing fbank && pitch feature of every frame in speech.
    """

    p = self.config
    with tf.name_scope('fbank_pitch'):

      if sample_rate == None:
        sample_rate = tf.constant(p.sample_rate, dtype=tf.int32)

      assert_op = tf.assert_equal(
          tf.constant(p.sample_rate), tf.cast(sample_rate, dtype=tf.int32))
      with tf.control_dependencies([assert_op]):

        fbank_feats = tf.squeeze(self.fbank(audio_data, sample_rate))
        pitch_feats = tf.squeeze(self.pitch(audio_data, sample_rate))
        fbank_pitch_feats = tf.concat([fbank_feats, pitch_feats], 1)

        return fbank_pitch_feats
