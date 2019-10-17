import csv
import sys

# source data delimiter
src_delimiter = ';'

# target data filename
data_file_name = 'data.csv'


def main():
    if len(sys.argv) < 5:
        print(
            "usage: %s <source-filename.csv> <target-filename.csv> first-name-col-num last-name-col-num" % sys.argv[0])
        exit(1)

    first_col, second_col, first_name_col, last_name_col = 0, 0, 0, 0
    try:
        first_name_col, last_name_col = int(sys.argv[3]), int(sys.argv[4])
        first_col = min(first_name_col, last_name_col)
        second_col = max(first_name_col, last_name_col)
        if first_col == second_col:
            raise ValueError('first-name-col-num and last-name-col-num are the same')
    except:
        print('first-name-col-num and last-name-col-num must be different integers')
        exit(1)

    with open(sys.argv[1], mode='r', encoding='utf-8') as source:
        with open(sys.argv[2], mode='w', newline='') as data:
            csv_reader = csv.reader(source, delimiter=src_delimiter)
            header = next(csv_reader)
            header[first_col] = "First and Last Name"
            header = header[:second_col] + header[second_col + 1:]
            data_writer = csv.writer(data, delimiter=';')
            data_writer.writerow(header)
            rows, persons = 0, 0
            for row in csv_reader:
                rows += 1
                row[first_col] = row[first_name_col] + ' ' + row[last_name_col]
                row = row[:second_col] + row[second_col + 1:]
                data_writer.writerow(row)

    print("Joined first and last names for %d rows" % rows)


if __name__ == '__main__':
    main()
