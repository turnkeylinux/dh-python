class FakeOptions:
    def __init__(self, **kwargs):
        opts = {
            'depends': (),
            'depends_section': (),
            'guess_deps': False,
            'no_ext_rename': False,
            'recommends': (),
            'recommends_section': (),
            'requires': (),
            'suggests': (),
            'suggests_section': (),
            'vrange': None,
            'accept_upstream_versions': False,
        }
        opts.update(kwargs)
        for k, v in opts.items():
            setattr(self, k, v)
