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
#
from unlock.model import FastPadModel
from unlock.view import FastPadView
from unlock.controller import UnlockControllerFragment, UnlockControllerChain, EEGControllerFragment, Canvas
import inspect
import os


class FastPad(UnlockControllerFragment):
    def __init__(self, model, view, standalone=False):
        super(FastPad, self).__init__(model, view)
        self.standalone = standalone
        
    @staticmethod
    def create_fastpad_fragment(canvas):
        fastpad_model = FastPadModel()            
        fastpad_view = FastPadView(fastpad_model, canvas)
        fastpad = FastPad(fastpad_model, fastpad_view)        
        return fastpad
        
    @staticmethod
    def create_fastpad(window, signal, timer, base=None, color='bw'):
        canvas = Canvas.create(window.width, window.height)
        if base == None:
            base = EEGControllerFragment.create_ssvep(canvas, signal, timer, color)
            
        fastpad = FastPad.create_fastpad_fragment(canvas)
        base.views.append(fastpad.view)
        controller_chain = UnlockControllerChain(window, canvas, base.command_receiver,
                                                 [base, fastpad] , 'FastPad', 'LazerToggleS.png',
                                                 standalone=False)
        return controller_chain
            
            