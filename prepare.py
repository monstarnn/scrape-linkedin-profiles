import csv
import sys

# source data delimiter
src_delimiter = ';'

# target data filename
data_file_name = 'data.csv'


def main():
    if len(sys.argv) < 5:
        print("usage: %s <source-filename.csv> [first-and-last-name-col position-col company-col "
              "additional-cols...]" % sys.argv[0])
        exit(1)

    src_cols = [int(i) for i in sys.argv[2:5]]
    col_titles = ["First and Last Name", "Position", "Company"]

    if len(src_cols) < 3:
        raise ValueError('must be set at least 3 cols for first-and-last-name, position and company')

    if len(sys.argv) > 5:
        for a in sys.argv[5:]:
            ap = a.split(':')
            if len(ap) != 2:
                raise ValueError('additional cols must be represent as <col-num>:<title>')
            src_cols.append(int(ap[0]))
            col_titles.append(ap[1])

    with open(sys.argv[1], mode='r', encoding='utf-8') as source:
        with open(data_file_name, 'w', newline='') as data:
            csv_reader = csv.reader(source, delimiter=src_delimiter)
            next(csv_reader)
            data_writer = csv.writer(data, delimiter=';')
            data_writer.writerow(col_titles)
            rows, persons = 0, 0
            for row in csv_reader:
                rows += 1
                # name = ("%s %s" % (row[src_cols[0]], row[src_cols[1]])).strip()
                name = row[src_cols[0]].strip()
                position = row[src_cols[1]].strip()
                company = row[src_cols[2]].strip()
                if name == "" or (position == "" and company == ""):
                    continue
                persons += 1
                row_data = [name, position, company]
                if len(src_cols):
                    for i in src_cols[3:]:
                        row_data.append(row[i] if len(row) > i else '')
                data_writer.writerow(row_data)

    print("Prepared %d persons from %d rows" % (persons, rows))


if __name__ == '__main__':
    main()
