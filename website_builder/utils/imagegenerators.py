class FixJustInTime:
    def on_source_saved(self, file):
        try:
            file.generate()
        except:
            pass

    def on_content_required(self, file):
        try:
            file.generate()
        except:
            pass

    def on_existence_required(self, file):
        try:
            file.generate()
        except:
            pass

class Optimistic(object):
    """
    A strategy that acts immediately when the source file changes and assumes
    that the cache files will not be removed (i.e. it doesn't ensure the
    cache file exists when it's accessed).
    """

    def on_source_saved(self, file):
        try:
            file.generate()
        except:
            pass

    def should_verify_existence(self, file):
        return False
