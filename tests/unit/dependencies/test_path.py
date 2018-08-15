from layer_linter.dependencies.path import ImportPath


class TestImportPath:
    def test_repr(self):
        import_path = ImportPath(
            importer='foo', imported='bar'
        )
        assert repr(import_path) == '<ImportPath: foo <- bar>'

    def test_equals(self):
        a = ImportPath(importer='foo', imported='bar')
        b = ImportPath(importer='foo', imported='bar')

        assert a == b

    def test_hash(self):
        a = ImportPath(importer='foo', imported='bar')
        b = ImportPath(importer='foo', imported='bar')
        c = ImportPath(importer='bar', imported='foo')

        assert hash(a) == hash(b)
        assert hash(a) != hash(c)
