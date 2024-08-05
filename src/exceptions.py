class LoginException(Exception):
    """
    Exception raised for errors that occur during login operations.
    """
    def __init__(self, *args, **kwargs):
        default_message = 'An error occurred while logging in'
        # If any arguments are passed, use them
        if args:
            super().__init__(*args, **kwargs)
        else:
            # Otherwise, use the default message
            super().__init__(default_message, **kwargs)


class UploadException(Exception):
    """
    Exception raised for errors that occur during upload operations.
    """
    def __init__(self, *args, **kwargs):
        default_message = 'An error occurred while uploading'
        # If any arguments are passed, use them
        if args:
            super().__init__(*args, **kwargs)
        else:
            # Otherwise, use the default message
            super().__init__(default_message, **kwargs)


class XEMNotFound(Exception):
    """
    Exception raised when an XEM (extra episode metadata) is not found.
    """
    pass


class WeirdSystem(Exception):
    """
    Exception raised for unexpected or unsupported system configurations.
    """
    pass


class ManualDateException(Exception):
    """
    Exception raised for issues related to manually specified dates.
    """
    pass