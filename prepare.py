import csv
import sys

# source data cols
src_cols = [
    0,  # first name col
    1,  # last name col
    2,  # position name
    3,  # company name
]
# source data delimiter
src_delimiter = ','

# target data filename
data_file_name = 'data.csv'


def main():
    if len(sys.argv) < 2:
        print("usage: %s <source-filename>" % sys.argv[0])
        exit(1)

    with open(sys.argv[1], mode='r', encoding='utf-8') as source:
        with open(data_file_name, 'w', newline='') as data:
            csv_reader = csv.reader(source, delimiter=src_delimiter)
            next(csv_reader)
            data_writer = csv.writer(data, delimiter=';')
            data_writer.writerow(["First and Last Name", "Position", "Company"])
            rows, persons = 0, 0
            for row in csv_reader:
                rows += 1
                name = ("%s %s" % (row[src_cols[0]], row[src_cols[1]])).strip()
                position = row[src_cols[2]].strip()
                company = row[src_cols[3]].strip()
                if name == "" or (position == "" and company == ""):
                    continue
                persons += 1
                data_writer.writerow([name, position, company])

    print("Prepared %d persons from %d rows" % (persons, rows))


if __name__ == '__main__':
    main()
