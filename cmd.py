#!/usr/bin/python3

import shlex, textwrap, http.client

class CmdParser:
    @staticmethod
    def printHelp(self, args):
        cmds = self._cmdtypes
        cwidth = max([len(x) for x in cmds.keys()]) + 3
        awidth = max([len(x['args']) for x in cmds.values()]) + 1

        fix = self._fixed
        msg = [fix(cmd, cwidth) + fix(cmds[cmd]['args'], awidth) + ': ' +  \
                textwrap.fill(cmds[cmd]['description'], subsequent_indent=cwidth)
                for cmd in sorted(cmds.keys())]
        msg = '\n'.join(msg)
        self.sendMsg('>Usage: /<command> [<args...>]\n\nCommands:\n' + msg)

    @staticmethod
    def _fixed(s, width):
        if len(s) > width:
            return s
        else:
            return s + ' ' * (width - len(s))
       
    def __init__(self, sender):
        if not callable(sender):
            raise TypeError("'sender' argument must be a callable object")
        self._cmdtypes = {'help': {'description': 'Prints this help message',
            'args': '', 'action': self.printHelp}}
        self._sender = sender

    #TODO: write to paste bin
    def addCommand(self, name, args, descript, action):
        self._cmdtypes[name] = {'args': args, 'description': descript, 'action': action}
        if action != None and not callable(action):
            raise TypeError("'action' argument must be a callable object or null")

    def parseMessage(self, msg):
        if len(msg) > 0 and msg[0] != '/':
            return

        args = shlex.split(msg)
        cmd = args[0][1:]
        args = args[1:]

        if not cmd in self._cmdtypes:
            self.sendMsg("Invalid command '%s'." % cmd)
        else:
            self._cmdtypes[cmd]['action'](self, args)
        
    def sendMsg(self, msg):
        self._sender(msg)
