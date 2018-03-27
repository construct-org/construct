from construct import Extension


class ExtensionD(Extension):
    name = 'ExtensionD'

    def load(self):
        raise RuntimeError('Load error...')
