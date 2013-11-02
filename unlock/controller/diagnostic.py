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

from unlock.model import UnlockModel
from unlock.controller import Canvas, UnlockControllerFragment, \
    UnlockControllerChain, EEGControllerFragment, FrequencyScope
from unlock.decode import CommandReceiverFactory

class Diagnostic(UnlockControllerFragment):
    def __init__(self, model, views, batch, standalone=False):
        super(Diagnostic, self).__init__(model, views, batch, standalone)
        
    @staticmethod
    def create_diagnostic_fragment(canvas):
        model = UnlockModel(state=True)
        diagnostic = Diagnostic(model, [], canvas.batch)
        return diagnostic
        
    @staticmethod
    def create_diagnostic(window, decoder, **kwargs):
        command_receiver = CommandReceiverFactory.create(
            CommandReceiverFactory.Raw, decoder.signal, decoder.timer)

        stimulus_canvas = Canvas.create(window.width / 2, window.height)
        stimulus = EEGControllerFragment.create_single_ssvep(
            stimulus_canvas, command_receiver, 15.0, **kwargs['stimulus'])

        scope_canvas = Canvas.create(window.width / 2, window.height,
                                     xoffset=(window.width / 2))
        scope = FrequencyScope.create_frequency_scope_fragment(
            scope_canvas, **kwargs['scope'])


        controller_chain = UnlockControllerChain(
            window, command_receiver, [stimulus, scope], 'Diagnostic',
            'gridcursor.png', standalone=False)
        return controller_chain
        
        