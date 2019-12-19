from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import time
import sys
from ansible import constants as C
from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback.default import CallbackModule as CallbackModule_default
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
        self.animation = "|/-\\"
        super(CallbackModule, self).__init__()

    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        if "pull" in result.task_name and "docker" in result.task_name.lower():
            msg = """                                      s
                     Docker image pulling in progress... c[_]

                  """
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)
        else:
            msg = "FAILED - RETRYING: %s (%d retries left)." % (task_name, result._result['retries'] - result._result['attempts'])
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)

CallbackModule = CallbackModule_custom_retry_runner
