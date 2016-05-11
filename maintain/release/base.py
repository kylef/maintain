class Releaser(object):
    """
    Base class for Releasers.
    """

    """
    The name of the Releaser.
    """
    name = 'Unknown'

    @classmethod
    def detect(cls):
        """
        Returns True when the Releaser detects the current project.
        """

        return False

    def determine_current_version(self):
        """
        Called to determine the current version number.
        """
        raise NotImplemented

    def determine_next_version(self):
        """
        Called to determine the next version number.
        """
        return None

    def bump(self, new_version):
        """
        Called to bump the version number in the project.
        """

        raise NotImplemented

    def release(self):
        """
        This method is called to perform actual release actions
        such as submission to a package manager.
        """

        raise NotImplemented
