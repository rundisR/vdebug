import sys
import os
import inspect

dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
sys.path.append(dir)

import socket
import vim
import traceback
import vdebug.runner
import vdebug.event

class DebuggerInterface:
    """ Acts as an interface, and as an extra layer above the Runner class.

    Fatal exceptions are caught and handled here.
    """
    def __init__(self):
        self.runner = vdebug.runner.Runner()
        self.event_dispatcher = vdebug.event.Dispatcher(self.runner)

    def __del__(self):
        self.runner.close()

    def handle_timeout(self):
        self.runner.close()
        self.runner.ui.say("No connection was made")

    def handle_socket_end(self):
        self.runner.ui.say("Connection to the debugger has been closed")
        self.runner.close_connection()

    def handle_vim_error(self,e):
        self.runner.ui.error("A Vim error occured: "+\
                str(e)+\
                "\n"+ traceback.format_exc())

    def handle_helpful_error(self,e):
        self.runner.ui.error(str(e))

    def handle_general_exception(self):
        self.runner.ui.error("An error occured: "+\
                str(sys.exc_info()[0])+\
                "\n"+ traceback.format_exc())

    def handle_exception(self,e):
        if isinstance(e,vdebug.dbgp.TimeoutError):
            self.handle_timeout()
        elif isinstance(e,vdebug.event.EventError):
            self.runner.ui.error(e)
        elif isinstance(e,vdebug.breakpoint.BreakpointError):
            self.runner.ui.error(e)
        elif isinstance(e,vdebug.log.LogError):
            self.handle_helpful_error(e)
        elif isinstance(e,(EOFError,socket.error)):
            self.handle_socket_end()
        elif isinstance(e,KeyboardInterrupt):
            print "Keyboard interrupt - debugging session cancelled"
            try:
                self.runner.close()
            except:
                pass
        elif isinstance(e,vim.error):
            self.handle_vim_error(e)
        else:
            self.handle_general_exception()

    def run(self):
        try:
            self.runner.run()
        except Exception, e:
            self.handle_exception(e)

    def run_to_cursor(self):
        try:
            self.runner.run_to_cursor()
        except Exception, e:
            self.handle_exception(e)

    def handle_return_keypress(self):
        try:
            return self.event_dispatcher.by_position()
        except Exception, e:
            self.handle_exception(e)

    def handle_double_click(self):
        try:
            return self.event_dispatcher.by_position()
        except Exception, e:
            self.handle_exception(e)

    def handle_visual_eval(self):
        try:
            return self.event_dispatcher.visual_eval()
        except Exception, e:
            self.handle_exception(e)

    def handle_eval(self,args):
        try:
            return self.runner.eval(args)
        except Exception, e:
            self.handle_exception(e)

    def toggle_breakpoint_window(self):
        try:
            return self.runner.toggle_breakpoint_window()
        except Exception, e:
            self.handle_exception(e)

    def step_over(self):
        try:
            self.runner.step_over()
        except Exception, e:
            self.handle_exception(e)

    def step_into(self):
        try:
            self.runner.step_into()
        except Exception, e:
            self.handle_exception(e)

    def step_out(self):
        try:
            self.runner.step_out()
        except Exception, e:
            self.handle_exception(e)

    def set_breakpoint(self,args = None):
        try:
            self.runner.set_breakpoint(args)
        except Exception, e:
            self.handle_exception(e)

    def remove_breakpoint(self,args = None):
        try:
            self.runner.remove_breakpoint(args)
        except Exception, e:
            self.handle_exception(e)

    def detach(self):
        try:
            self.runner.detach()
        except Exception, e:
            self.handle_exception(e)

    def close(self):
        if self.runner.is_alive():
            self.runner.close_connection()
        else:
            self.runner.close()
