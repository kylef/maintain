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

    @classmethod
    def config_name(cls):
        """
        The releasers configuration key.
        """
        return cls.name.lower().replace(' ', '_')

    @classmethod
    def schema(cls):
        """
        Returns a schema for validating the configuration for the releaser.
        """
        return None

    def __init__(self, config=None):
        pass

    def determine_current_version(self):
        """
        Called to determine the current version number.
        """
        raise NotImplementedError()

    def determine_next_version(self):
        """
        Called to determine the next version number.
        """
        return None

    def pre_bump(self, new_version):
        """
        Called before bumping the version.
        """
        pass

    def bump(self, new_version):
        """
        Called to bump the version number in the project.
        After called, ``determine_current_version()`` should return
        the new version.
        """

        raise NotImplementedError()

    def post_bump(self, new_version):
        """
        Called after bumping the version.
        """
        pass

    def pre_release(self, new_version):
        """
        Called before releasing the version.
        """
        pass

    def release(self, new_version):
        """
        This method is called to perform actual release actions
        such as submission to a package manager.
        """

        raise NotImplementedError()

    def post_release(self, new_version):
        """
        Called after releasing the version.
        """
        pass
