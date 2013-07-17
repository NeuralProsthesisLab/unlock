import socket
import json

class ControlManager(object):
    """
    Handles the import of data and sends the decisions and selections to the update methods of each app
    """
    def __init__(self, bci_sampler, apps):

        self.debug_commands = {}
        self.set_apps(apps)



    def set_apps(self, apps):
        self.apps = apps
        for app in apps:
            app.controller = self
                
    def replace_app(self, old, new):
        self.apps.remove(old)
        self.apps.append(new)
        new.controller = self
            
    def quit(self):
        self.command_reciever.stop()
        for app in self.apps:
            app.root().quit()
            
    def acquire(self):
        selection = None
        try:
            selection, _ = self._socket_selection.recvfrom(1)
            selection = int(selection)
        except socket.timeout:
            pass
        except socket.error:
            pass
        except ValueError:
            pass
        if 'selection' in self.debug_commands:
            selection = self.debug_commands['selection']
            del self.debug_commands['selection']

        data = []
        while True:
            try:
                d, _ = self._socket_data.recvfrom(64)
                data.append(json.loads(d))
            except socket.timeout:
                break
            except socket.error:
                break

        return decision, selection, data
    def override_bci_input(self, key, value):
        manual_override_key = key
        manual_override_value = value

    def update(self, dt):
        check_for_manual_override()
        decision, selection, data = self.acquire()

        for app in self.apps:
            app.update(dt, decision, selection)
            if app.gets_samples:
                app.sample(data)

    def draw(self):
        for app in self.apps:
            app.draw()
            
            