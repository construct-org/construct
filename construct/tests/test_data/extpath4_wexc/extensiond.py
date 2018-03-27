from construct import Extension


class ExtensionD(Extension):
    name = 'ExtensionD'
    attr_name = 'extension_d'

    def load(self):
        raise RuntimeError('Load error...')
