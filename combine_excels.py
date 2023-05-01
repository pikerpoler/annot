import argparse
import pandas

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_labels', type=str, required=True, help='excel input with labels and bbox')
    parser.add_argument('--input_vec', type=str, required=True, help='excel input with vectors')
    parser.add_argument('--output', type=str, required=True, help='excel output with labels, bbox and vectors')
    args = parser.parse_args()

    # read both excels as dataframe
    df_labels = pandas.read_excel(args.input_labels)
    df_vec = pandas.read_excel(args.input_vec)
    print(f'length of df_vec: {len(df_vec)}')
    df_vec = df_vec[df_vec.label != 0]
    # delete the rows with label nan
    df_vec = df_vec.dropna(subset=['label'])
    print(f'length of df_vec after deleting rows with label 0: {len(df_vec)}')
    # change the names of the columns label, x1, x2, y1, y2 to contain the word bbox or vector


    df_vec = df_vec.rename(columns={'label': 'label_vec', 'x1': 'x1_vec', 'x2': 'x2_vec', 'y1': 'y1_vec',
                                            'y2': 'y2_vec'})
    # merge the two dataframes on the column image path, left join
    df = df_labels.merge(df_vec, on='image path', how='left')
    df.to_csv(args.output)


def prepare_excel():
    """
    this function gets an excel file with the following columns: image path, label, x1, x2, y1, y2
    it creates a new excel file with the same columns, but with the following changes:
    1. it deletes the rows with label 0
    2. it deletes all the enties to columns x1, x2, y1, y2 and label (keeps only the image path)
    :return:
    """
    input_excel = '/Users/nadav.nissim/Documents/Coding/data/cat1data/catlab1.xlsx'
    output_excel = '/Users/nadav.nissim/Documents/Coding/data/cat1data/catvec1_clean.xlsx'
    df = pandas.read_excel(input_excel)
    # delete rows with label 0
    df = df[df.label != 0]
    # delete all the enties to columns x1, x2, y1, y2 and label (keeps only the image path)
    # df = df.drop(columns=['label', 'x1', 'x2', 'y1', 'y2'],)
    df.to_excel(output_excel)

if __name__ == '__main__':

    main()
    # prepare_excel()