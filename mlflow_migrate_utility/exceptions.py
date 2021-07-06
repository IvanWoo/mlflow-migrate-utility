class MmuException(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        super().__init__(msg or self.__doc__, *args, **kwargs)


class InvalidCloudVendorError(MmuException):
    """Invalid CloudVendor name"""


class InvalidLocationError(MmuException):
    pass


class EmptyStorageAccountError(MmuException):
    pass
