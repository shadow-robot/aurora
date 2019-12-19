# written for python2.7
# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from __main__ import cli

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DOCUMENTATION = '''
    callback: example_callback_plugin
    type: notification
    short_description: Send callback on various runners to an API endpoint.
    description:
      - On ansible runner calls report state and task output to an API endpoint.
      - Configuration via callback_config.ini, place the file in the same directory
        as the plugin.
    requirements:
      - python requests library
      - HTTPBasicAuth library from python requests.auth
      - ConfigParser for reading configuration file
    '''

class CallbackModule(CallbackBase):

    '''
    Callback to API endpoints on ansible runner calls.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'retry_output_msg_callback_plugin'

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__()

    def v2_runner_retry(self, result):
        task_name = result.task_name or result._task
        if "pull" in result.task_name:
            msg = "PULLING IN PROGRESS: %s (%d retries left)." % (task_name, result._result['retries'] - result._result['attempts'])
            if self._run_is_verbose(result, verbosity=2):
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)
        else:
            msg = "PEPEPEP - RETRYING: %s (%d retries left)." % (task_name, result._result['retries'] - result._result['attempts'])
            if self._run_is_verbose(result, verbosity=2):
                msg += "Result was: %s" % self._dump_results(result._result)
            self._display.display(msg, color=C.COLOR_DEBUG)
