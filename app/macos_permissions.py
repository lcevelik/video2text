from Foundation import NSObject
from AVFoundation import AVAudioSession
import logging

logger = logging.getLogger(__name__)

def request_microphone_permission():
    session = AVAudioSession.sharedInstance()
    def handler(granted):
        if granted:
            logger.info("Microphone access granted")
        else:
            logger.warning("Microphone access denied")
    session.requestRecordPermission_(handler)
