__metaclass__ = type

from ansible import constants as C
from ansible.plugins.callback.default import CallbackModule as CallbackModule_default


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

    def v2_runner_on_start(self, host, task):
        pass

    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        if "pull" in result.task_name.lower() and "docker" in result.task_name.lower():
            msg = "Docker image pulling in progress... Message count: "+str(result._result['attempts'])
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)
        elif "arp" in result.task_name.lower() and "mac" in result.task_name.lower():
            msg = "Waiting for the MAC address of a connected adapter to appear in arp... Message count: "+str(result._result['attempts'])
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)
        else:
            msg = "FAILED - RETRYING: %s (%d retries left)." % (task_name, result._result['retries'] - result._result['attempts'])
            if (self._display.verbosity > 2 or '_ansible_verbose_always' in result._result) and '_ansible_verbose_override' not in result._result:
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)

CallbackModule = CallbackModule_custom_retry_runner
