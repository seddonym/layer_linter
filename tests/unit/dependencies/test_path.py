from layer_linter.dependencies.path import ImportPath
from layer_linter.module import Module


class TestImportPath:
    def test_repr(self):
        import_path = ImportPath(
            importer=Module('foo'), imported=Module('bar')
        )
        assert repr(import_path) == '<ImportPath: foo <- bar>'

    def test_equals(self):
        a = ImportPath(importer=Module('foo'), imported=Module('bar'))
        b = ImportPath(importer=Module('foo'), imported=Module('bar'))
        c = ImportPath(importer=Module('foo'), imported=Module('foo.baz'))

        assert a == b
        assert a != c
        # Also non-ImportPath instances should not be treated as equal.
        assert a != 'foo'

    def test_hash(self):
        a = ImportPath(importer=Module('foo'), imported=Module('bar'))
        b = ImportPath(importer=Module('foo'), imported=Module('bar'))
        c = ImportPath(importer=Module('bar'), imported=Module('foo'))

        assert hash(a) == hash(b)
        assert hash(a) != hash(c)
