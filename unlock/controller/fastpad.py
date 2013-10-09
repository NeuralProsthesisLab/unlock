# Created By: Karl Wiegand (wiegand@ccs.neu.edu)
# Date Created: Tue Mar  5 12:14:06 EST 2013
# Description: Main program file for FastPad, a letter-based
#   typing interface for the Unlock project

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
#from unlock.decode import HarmonicSumDecision, RawInlineSignalReceiver, ClassifiedCommandReceiver
from unlock.controller import UnlockController, Canvas, VEP
import inspect
import os


class FastPad(UnlockController):
    def __init__(self, window, views, canvas, vep, fastpad_model, icon="LazerToggleS.png", name="FastPad"):
        super(UnlockController, self).__init__(window, views, canvas)
        self.vep = vep
        self.fastpad_model = fastpad_model
        self.name = name
        self.icon = icon
        self.icon_path = os.path.join(os.path.dirname(inspect.getabsfile(FastPad)),
                                      'resource', self.icon)
        
    def keyboard_input(self, command):
        self.fastpad_model.process_command(command)
        
    def poll_signal(self, delta):
        command = self.command_receiver.next_command(delta)
        self.fastpad_model.process_command(command)
        self.vep.update_state(command)
        
    def activate(self):
        self.fastpad_model.start()
        return self.vep.start()
        
    def deactivate(self):
        self.fastpad_model.stop()
        return self.vep.stop()
        
    @staticmethod
    def create_ssvep(window, signal, timer, base=None, color='bw'):
        if base == None:
            base = VEP.create_ssvep(window, signal, timer, color)
            
        fastpadmodel = FastPadModel()            
        fastpadview = FastPadView(fastpadmodel, canvas)
        base.views.append(fastpadview)
        return FastPad(window, base.views, base.canvas, fastpadmodel)
        
        