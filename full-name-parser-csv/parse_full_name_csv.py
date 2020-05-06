from optparse import OptionParser
from nameparser import HumanName
from kitir import *

log = logging.getLogger('parse_full_name_csv')


class ParseFullNameCSV(object):
    output_file_format = '{input_file_base}{output_postfix}.csv'
    output_postfix_constant = '_parsedName'
    output_headers_to_add = ['parsed_{}'.format(h) for h in HumanName._members]
    default_input_field_to_parse = 'name'

    def __init__(self, input_file, output_file=None, field_name=None, save_names_only=False):
        self.input_file = input_file
        assert os.path.exists(self.input_file)
        assert self.input_file.endswith(".csv")
        self.output_file = output_file or self.make_output_file_path_from_input_file_path(input_file)
        self.fieldname = field_name or self.default_input_field_to_parse
        self.save_names_only = save_names_only
        log.debug('ParseFullNameCSV object created: input={} output={} fieldname={} save_names_only={}'.format(
            self.input_file, self.output_file, self.fieldname, self.save_names_only))
        super().__init__()

    @classmethod
    def make_output_file_path_from_input_file_path(cls, file_path):
        log.debug('making output file path from input file path: input={}'.format(file_path))
        assert os.path.exists(file_path)
        basename, extension = os.path.splitext(file_path)
        output_path = cls.output_file_format.format(
            input_file_base=basename, output_postfix=cls.output_postfix_constant)
        log.debug('new output file path: output={}'.format(output_path))
        return output_path

    def process_input_file(self):
        log.info('processing input file: input={}'.format(self.input_file))
        rows, headers = utils.read_csv(self.input_file, return_headers=True)
        log.debug('finished reading input file: rows={} headers={}'.format(len(rows), len(headers)))
        new_rows = self.process_rows(rows)
        if self.save_names_only:
            new_headers = self.output_headers_to_add + [self.fieldname]
        else:
            new_headers = self.output_headers_to_add + headers
        log.debug('preparing to write output file: rows={} headers={}'.format(len(new_rows), len(new_headers)))
        write_path = utils.write_csv(self.output_file, new_rows, new_headers, lineterminator="\n")
        log.info('finished processing file: output={}'.format(write_path))
        return 0

    def process_rows(self, rows):
        new_rows = []
        for row in rows:
            new_rows.append(self.process_row(row))
        return new_rows

    def process_row(self, row):
        new_row = row.copy()
        hn = HumanName(row[self.fieldname])
        new_data = {'parsed_{}'.format(k): v for k, v in hn.as_dict().items()}
        new_row.update(new_data)
        return new_row


def main(args):
    parser = OptionParser()
    # logging
    parser.add_option('--log-level', '--ll', dest='log_level', help='Log Level (0=info, 1=debug, 2=trace)')
    parser.add_option('--log-file', '--lf', dest='log_file', help='Log file',
                      default=init_working_directory + '/parse_full_name.log')
    # data
    parser.add_option('--input-file', '-i', dest='input_file',
                      help='read from input file (.csv) instead of first arg')
    parser.add_option('--output-file', '-o', dest='output_file',
                      help='write to output file (.csv) instead of default (adjacent copy)')
    parser.add_option('--field-name', '-f', dest='field_name', default='name',
                      help='specify the field name if not using default (name)')
    # options
    parser.add_option('--save-names-only', dest='save_names_only', default=False, action='store_true',
                      help='save only the names in the output, ignoring all other data')
    options, args = parser.parse_args(args)

    utils.logging_setup(log_level=options.log_level, log_file=options.log_file)

    if args and not options.input_file:
        if len(args) == 1:
            options.input_file = args[0]
        else:
            parser.error('too many arguments, please supply only one argument (input_file)')
    elif not options.input_file:
        parser.error('please provide an input_file by argument or -i option')

    pfn = ParseFullNameCSV(options.input_file, options.output_file, options.field_name,
                           save_names_only=options.save_names_only)
    status = pfn.process_input_file()
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
