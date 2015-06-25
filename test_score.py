import unittest

import mock

from score import score_reader, read_records, calculate_score


class PatcherMixin(object):

    def _start_patch(self, patcher):
        thing = patcher.start()
        self.addCleanup(patcher.stop)

        return thing

    def create_patch(self, path):
        patcher = mock.patch(path)
        return self._start_patch(patcher)


class TestScoreReader(unittest.TestCase, PatcherMixin):

    def setUp(self):
        self.logging_mock = self.create_patch('score.logging')

    def test_valid_line(self):
        self.assertEqual(score_reader('1, web, 1.0'), (1, 1.0))

    def test_wrong_format(self):
        self.assertIsNone(score_reader('1, web, 1.0, 123'))

    def test_wrong_contact_id(self):
        self.assertIsNone(score_reader('1s, web, 1.0'))

    def test_wrong_event(self):
        self.assertIsNone(score_reader('1, web-, 1.0, 123'))

    def test_wrong_score(self):
        self.assertIsNone(score_reader('1, web, 1.*0'))


class TestReadRecords(unittest.TestCase, PatcherMixin):

    def setUp(self):
        self.line_reader_mock = mock.Mock(return_value='Ok')
        self.logging_mock = self.create_patch('score.logging')

        self.open_mock = self.create_patch('__builtin__.open')
        self.open_mock.return_value.__enter__.return_value.__iter__.return_value = iter(['2, web, 15'])

    def test_read_records(self):
        self.assertEqual(list(read_records('f.csv')), ['2, web, 15'])

    def test_use_line_reader(self):
        self.assertEqual(list(read_records('f.csv', self.line_reader_mock)), ['Ok'])
        self.line_reader_mock.assert_called_once_with('2, web, 15')


class TestCalculateScore(unittest.TestCase, PatcherMixin):

    def setUp(self):
        self.read_records_mock = self.create_patch('score.read_records')
        self.logging_mock = self.create_patch('score.logging')

    def test_calculate(self):
        self.read_records_mock.return_value = [(1, 0), (2, 50), (2, 50)]
        self.assertEqual(list(calculate_score('f.csv')),  [(1, 'bronze', 0.0), (2, 'platinum', 100.0)])

    def test_calculate_single_record(self):
        self.read_records_mock.return_value = [(1, 50)]
        self.assertEqual(list(calculate_score('f.csv')), [])

    def test_calculate_no_records(self):
        self.read_records_mock.return_value = []
        self.assertEqual(list(calculate_score('f.csv')), [])


if __name__ == '__main__':
    unittest.main()
