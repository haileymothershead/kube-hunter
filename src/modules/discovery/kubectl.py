
import logging
import subprocess 
import json

from ...core.types import Discovery
from ...core.events import handler
from ...core.events.types import HuntStarted, Event


class KubectlClientEvent(Event):
    """The API server is in charge of all operations on the cluster."""
    def __init__(self, version):
        self.version = version

    def location(self):
        return "local machine"

# Will be triggered on start of every hunt 
@handler.subscribe(HuntStarted)
class KubectlClientDiscovery(Discovery):
    """Kubectl Client Discovery
    Checks for the existence of a local kubectl client
    """
    def __init__(self, event):
        self.event = event

    def get_kubectl_binary_version(self):
        version = None
        try:
            # kubectl version --client does not make any connection to the cluster/internet whatsoever.
            version_info = subprocess.check_output(["kubectl", "version", "--client"], stderr=subprocess.STDOUT)
            if b"GitVersion" in version_info:
                # extracting version from kubectl output
                version_info = version_info.decode()
                start = version_info.find('GitVersion')
                version = version_info[start + len("GitVersion':\"") : version_info.find("\",", start)]
        except Exception as e:
            logging.debug("Exception " + str(e))
            logging.debug("Could not find kubectl client")
        return version
    
    def execute(self):
        logging.debug("Attempting to discover a local kubectl client")
        version = self.get_kubectl_binary_version() 
        if version:
            self.publish_event(KubectlClientEvent(version=version))