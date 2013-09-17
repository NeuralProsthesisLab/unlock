import socket
import json

class Controller():
    """
    Handles the import of data and sends the decisions and selections to the update methods of each app
    """
    def __init__(self, apps):

        self.debug_commands = {}
        self.set_apps(apps)

        # UDP sockets for receiving decoder and acquisition output
        self._socket_decision = socket.socket(type=socket.SOCK_DGRAM)
        self._socket_decision.settimeout(0.001)
        self._socket_decision.bind(('127.0.0.1',33445))

        self._socket_selection = socket.socket(type=socket.SOCK_DGRAM)
        self._socket_selection.settimeout(0.001)
        self._socket_selection.bind(('127.0.0.1',33446))

        self._socket_data = socket.socket(type=socket.SOCK_DGRAM)
        self._socket_data.settimeout(0.001)
        self._socket_data.bind(('127.0.0.1',33447))

    def set_apps(self, apps):
        self.apps = apps
        for app in apps:
            app.controller = self

    def quit(self):
        self._socket_data.close()
        self._socket_selection.close()
        self._socket_decision.close()
        for app in self.apps:
            app.root().quit()

    def acquire(self):
        decision = None
        try:
            decision, _ = self._socket_decision.recvfrom(1)
            decision = int(decision)
        except socket.timeout:
            pass
        except socket.error:
            pass
        except ValueError:
            pass
        if 'decision' in self.debug_commands:
            decision = self.debug_commands['decision']
            del self.debug_commands['decision']

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

    def update(self, dt):
        decision, selection, data = self.acquire()

        for app in self.apps:
            app.update(dt, decision, selection)
            if app.gets_samples:
                app.sample(data)

    def draw(self):
        for app in self.apps:
            app.screen.batch.draw()