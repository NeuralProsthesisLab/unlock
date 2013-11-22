# Copyright (c) James Percent, Byron Galbraith and Unlock contributors.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#    
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#    3. Neither the name of Unlock nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from unlock.model import VepDiagnosticState
from unlock.controller import Canvas, CalibratedControllerFragment, \
    UnlockControllerChain, EEGControllerFragment, FrequencyScope
from unlock.decode import CommandReceiverFactory, HarmonicSumDecisionDiagnostic
from unlock.view import PygletDynamicTextLabel

class Diagnostic(CalibratedControllerFragment):
    def __init__(self, window, model, views, batch, standalone=False):
        super(Diagnostic, self).__init__(window, model, views, batch, standalone)
        
    @staticmethod
    def create_vep_diagnostic_fragment(window, canvas, scope, stimulus, **kwargs):
        model = VepDiagnosticState(scope, stimulus, **kwargs)
        feedback = PygletDynamicTextLabel(model, canvas, '', canvas.width/2,
                                          canvas.height*0.9, size=20)
        diagnostic = Diagnostic(window, model, [feedback], canvas.batch)
        return diagnostic
        
    @staticmethod
    def create_femg_diagnostic_fragment(self, window, decoder, **kwargs):
        command_receiver = CommandReceiverFactory.create(CommandReceiverFactory.Raw, decoder.signal, decoder.timer)
        #command_receiver = RawInlineSignalReceiver(decoder.signal, decoder.timer)                                                           
        #controller_chain = UnlockControllerChain(window, command_receiver,
        #                                         [collector] , 'Diagnostic', 'frequency2-128x128.png',
        #                                         standalone=False)
        #return controller_chain
        #
        #if base is None:
        #    command_receiver = CommandReceiverFactory.create(
        #        CommandReceiverFactory.Raw, decoder.signal, decoder.timer)
        #else:
        #    command_receiver = base.command_receiver
        #
        #stimuli_canvas = Canvas.create(window.width / 2, window.height)
        #stimuli = EEGControllerFragment.create_single_ssvep(
        #    stimuli_canvas, command_receiver, 15.0, **kwargs['stimulus'])
        #
        #scope_canvas = Canvas.create(window.width / 2, window.height,
        #                             xoffset=(window.width / 2))
        #scope = FrequencyScope.create_frequency_scope_fragment(
        #    scope_canvas, **kwargs['scope'])
        #
        #hsd_args = {'targets': [12, 13, 14, 15], 'duration': 3, 'fs': 256,
        #            'electrodes': 4, 'label': 'HSD1'}
        #hsd = HarmonicSumDecisionDiagnostic(**hsd_args)
        #hsd2_args = {'targets': [13, 14, 15, 16], 'duration': 3, 'fs': 256,
        #             'electrodes': 4, 'label': 'HSD2'}
        #hsd2 = HarmonicSumDecisionDiagnostic(**hsd2_args)
        #
        #diagnostic_canvas = Canvas.create(window.width, window.height)
        #diagnostic = Diagnostic.create_diagnostic_fragment(
        #    diagnostic_canvas, scope, stimuli, decoders=[hsd, hsd2],
        #    **kwargs['diagnostic'])
        #
        #controller_chain = UnlockControllerChain(
        #    window, command_receiver, [diagnostic, stimuli, scope],
        #    'Diagnostic', 'frequency2-128x128.png', standalone=False)
        #return controller_chain
        pass
    
    @staticmethod
    def create_vep_diagnostic(window, decoder, base=None, **kwargs):
        if base is None:
            command_receiver = CommandReceiverFactory.create(
                CommandReceiverFactory.Raw, decoder.signal, decoder.timer)
        else:
            command_receiver = base.command_receiver

        controllers = list()

        stimuli_canvas = Canvas.create(window.width, window.height)
        stimuli = EEGControllerFragment.create_single_ssvep(
            stimuli_canvas, command_receiver, 10.0, **kwargs['stimulus'])
        controllers.append(stimuli)

        #scope_canvas = Canvas.create(window.width / 2, window.height,
        #                             xoffset=(window.width / 2))
        #scope = FrequencyScope.create_frequency_scope_fragment(
        #    scope_canvas, **kwargs['scope'])
        #controllers.append(scope)
        scope = None

        decoders = list()
        hsd_args = {'targets': [12, 13, 14, 15], 'duration': 3, 'fs': 500,
                    'electrodes': 8, 'label': 'HSD'}
        hsd = HarmonicSumDecisionDiagnostic(**hsd_args)
        decoders.append(hsd)
        #hsd2_args = {'targets': [13, 14, 15, 16], 'duration': 3, 'fs': 256,
        #             'electrodes': 4, 'label': 'HSD2'}
        #hsd2 = HarmonicSumDecisionDiagnostic(**hsd2_args)

        diagnostic_canvas = Canvas.create(window.width, window.height)
        diagnostic = Diagnostic.create_vep_diagnostic_fragment(
            window, diagnostic_canvas, scope, stimuli, decoders=decoders,
            **kwargs['diagnostic'])
        controllers.append(diagnostic)

        controller_chain = UnlockControllerChain(
            window, command_receiver, controllers,
            'Diagnostic', 'frequency2-128x128.png', standalone=False)
        return controller_chain