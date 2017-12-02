#!/usr/bin/python3

import shlex, textwrap, http.client

class CmdParser:
    def __init__(self, sender):
        if not callable(sender):
            raise TypeError("'sender' argument must be a callable object")
        self._cmdtypes = {'help': {'description': 'Prints this help message',
            'args': '', 'action': self.printHelp}}
        self._sender = sender

    def _fixed(s, width):
        if len(s) > width:
            return s
        else
            return s + ' ' * (width - len(s))
       

    def addCommand(self, name, args, descript, action):
        self._cmdtypes[name] = {'args': args, 'description': descript, 'action': action}
        if action != None and not callable(action):
            raise TypeError("'action' argument must be a callable object or null")

    def printHelp(self):
        cmds = self._cmdtypes
        cwidth = max([len(x) for x in cmds.keys()]) + 2
        awidth = max([len(x['args']) for x in cmds.values()]) + 1

        fix = self._fixed
        msg = [fix(cmd, cwidth) + fix(cmds[cmd]['args'], awidth) + \
                textwrap.fill(cmds[cmd]['description'], subsequent_indent=cwidth)
                for cmd in sorted(cmds.keys())]
        msg = '\n'.join(msg)
        sendMsg('>Usage: /<command> [<args...>]\n' + msg)
        #TODO: write to paste bin

    def parseMessage(self, msg):
        if len(msg) > 0 and msg[0] != '/':
            return

        args = shlex.split(msg)
        cmd = args[0][1:]
        args = args[1:]

        if not args[0] in self._cmdtypes:
            self.sendMsg("Invalid command '%s'." % args[0])
        else:
            self._cmdtypes[cmd]['action'](self, args)
        
    def sendMsg(self, msg):
        self._sender(msg)
