def is_valid_signal(signal, confidence_threshold):
    if signal['confidence'] < confidence_threshold:
        return False
    if signal['momentum'] < 40:
        return False
    return True