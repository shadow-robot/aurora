# written for python2.7
# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible import constants as C
from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor

class CallbackModule_custom_retry_runner(CallbackModule_default):

    ''''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'custom_retry_runner'

    def __init__(self):

        self._play = None
        self._last_task_banner = None
        super(CallbackModule, self).__init__()

    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        if "pull" in result.task_name:
            msg = "Docker image pulling in progress...%s ."
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)
        else:
            msg = "FAILED - RETRYING: %s (%d retries left)." % (task_name, result._result['retries'] - result._result['attempts'])
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)

    def v2_playbook_on_notify(self, handler, host):
        if self._display.verbosity > 1:
            self._display.display("NOTIFIED HANDLER %s for %s" % (handler.get_name(), host), color=C.COLOR_VERBOSE, screen_only=True)
