
import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import as_strided
import psycopg2
from sklearn.model_selection import train_test_split

def __make_views(
    arr,
    win_size,
    step_size,
    writeable=False,
):
    """
    https://krbnite.github.io/Memory-Efficient-Windowing-of-Time-Series-Data-in-Python-3-Memory-Strides-in-Pandas/
    arr: any 2D array whose columns are distinct variables and
      rows are data records at some timestamp t
    win_size: size of data window (given in data points along record/time axis)
    step_size: size of window step (given in data point along record/time axis)
    writable: if True, elements can be modified in new data structure, which will affect
      original array (defaults to False)

    Note that step_size is related to window overlap (overlap = win_size - step_size), in
    case you think in overlaps.

    This function can work with C-like and F-like arrays, and with DataFrames.  Yay.
    """

    # If DataFrame, use only underlying NumPy array
    if type(arr) == type(pd.DataFrame()):
        arr = arr.values

    # Compute Shape Parameter for as_strided
    n_records = arr.shape[0]
    n_columns = arr.shape[1]
    remainder = (n_records - win_size) % step_size
    num_windows = 1 + int((n_records - win_size - remainder) / step_size)
    shape = (num_windows, win_size, n_columns)

    # Compute Strides Parameter for as_strided
    next_win = step_size * arr.strides[0]
    next_row, next_col = arr.strides
    strides = (next_win, next_row, next_col)

    new_view_structure = as_strided(
        arr,
        shape=shape,
        strides=strides,
        writeable=writeable,
    )
    return new_view_structure

def __reduce_timeframe(X: np.array, y: list, win_size: int = 100, step_size_1: int = 1, step_size_0: int = 10, win_begin: int = -80, win_end: int = 1) -> (np.array, np.array):
    """
    Reduce the time frame of a data array by sliding a window of size win_size over it.
    """

    samples = []
    labels = []

    for i, sample in enumerate(X):
        # if sample has label 1.0 in label_list
        if y[i] == 1.:
            # make views of 50 time steps and save them in a list
            views = __make_views(sample, win_size=win_size, step_size=step_size_1)

            # get the mean variance of each view (given by the accelerometer data)
            view_vars = np.var(views[:, :3], axis=1)
            view_vars = np.mean(view_vars, axis=1)

            # get n indeces of highest variance in view_vars
            max_index = np.argmax(view_vars)

            # get views with highest variance (stop if max index is reached)
            max_views = [views[i] for i in range(max_index + win_begin if max_index + win_begin > 0 else 0, max_index + win_end if max_index + win_end < len(views) else len(views))]

            samples.append(np.array(max_views))
            labels.append([1.] * len(max_views))

        else:
            views = __make_views(sample, win_size=win_size, step_size=step_size_0)
            labels.append([0.] * len(views))
            samples.append(np.array(views))

    samples = np.concatenate(samples)
    labels = np.concatenate(labels)

    return samples, labels

def load_data(win_size=150, step_size_1=1, step_size_0=10, win_begin=-20, win_end=5):
    CONNECTION = "xxx"
    DATA_HEADERS = ["row", "ax", "ay", "az", "gx", "gy", "gz", "qx", "qy", "qz", "qw", "p", "sample_id"]
    SAMPLE_HEADERS = ["sample_id", "subject", "label"]

    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()

        # select all data from samples table
        SQL_SAMPLE = "SELECT * FROM samples;"
        SQL_DATA = "SELECT * FROM data;"

        try:
            cursor.execute(SQL_SAMPLE)
            samples = cursor.fetchall()
            print("Samples fetched")
            cursor.execute(SQL_DATA)
            data = cursor.fetchall()
            print("Data fetched")

        except (Exception, psycopg2.Error) as error:
            print(error.pgerror)

    # create dataframe from samples and set "id" as index
    sample_df = pd.DataFrame(samples, columns=SAMPLE_HEADERS)
    sample_df.set_index("sample_id", inplace=True)
    data_df = pd.DataFrame(data, columns=DATA_HEADERS)

    #get sample_ids from sample_df
    sample_ids = sample_df.index.values

    # merge sample_df with data_df on sample_id
    data_df = pd.merge(sample_df, data_df, on="sample_id")

    features = ["sample_id", "label", "ax", "ay", "az", "gx", "gy", "gz", "qx", "qy", "qz", "qw", "p"]
    data_df = data_df[features]

    # make multiple dataframes for each sample_id
    sample_list = []
    label_list = []

    # for each sample_id
    # create a dataframe with the data from the sample_id (optionally create views)
    # and add it to the list
    for sample_id in sample_ids:
        sample_df = data_df[data_df["sample_id"] == sample_id].drop(columns=["sample_id"])
        label = sample_df.iloc[0]["label"] # get label from first row of sample
        sample_df.drop(columns=["label"], inplace=True)
        sample_npy = sample_df.to_numpy() # convert to numpy array
        sample_npy = __make_views(sample_npy, win_size=200, step_size=1) # make views
        sample_list.append(sample_npy) # add to list
        label_list.append([label] * sample_npy.shape[0]) # add to list

    # convert to numpy array

    all_samples = np.concatenate(sample_list)
    all_labels = np.concatenate(label_list)

    print(f"all_samples shape: {all_samples.shape}")
    print(f"all_labels shape: {all_labels.shape}")

    # F1: 1, F2: 1, F3: 1, F4: 1, D1: 0, D2: 0, D3: 0, D4: 0
    # create a dict to map labels to numbers
    label_dict = {
        "F1": 1.,
        "F2": 1.,
        "F3": 1.,
        "F4": 1.,
        "D1": 0.,
        "D2": 0.,
        "D3": 0.,
        "D4": 0.
    }

    # map labels to numbers
    label_list = np.array([label_dict[label] for label in all_labels])

    # train test split
    X_train, X_test, y_train, y_test = train_test_split(all_samples, label_list, test_size=0.3, random_state=42, stratify=label_list)
    X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.5, random_state=42, stratify=y_test)

    print(f"X_train shape: {X_train.shape}")
    print(f"X_val shape: {X_val.shape}")
    print(f"X_test shape: {X_test.shape}")

    X_train, y_train = __reduce_timeframe(X_train, y_train, win_size=win_size, step_size_1=step_size_1, step_size_0=step_size_0, win_begin=win_begin, win_end=win_end)
    X_val, y_val = __reduce_timeframe(X_val, y_val, win_size=win_size, step_size_1=step_size_1, step_size_0=step_size_0, win_begin=win_begin, win_end=win_end)
    X_test, y_test = __reduce_timeframe(X_test, y_test, win_size=win_size, step_size_1=step_size_1, step_size_0=step_size_0, win_begin=win_begin, win_end=win_end)

    print(f"X_train shape: {X_train.shape}, 1/0 ratio: {np.sum(y_train)/len(y_train)}")
    print(f"X_val shape: {X_val.shape}, 1/0 ratio: {np.sum(y_val)/len(y_val)}")
    print(f"X_test shape: {X_test.shape}, 1/0 ratio: {np.sum(y_test)/len(y_test)}")

    return X_train, X_val, X_test, y_train, y_val, y_test

if __name__ == "__main__":
    X_train, X_val, X_test, y_train, y_val, y_test = load_data(200)
    print(f"X_train shape: {X_train.shape}")
    print(f"X_val shape: {X_val.shape}")
    print(f"X_test shape: {X_test.shape}")
    print(f"y_train shape: {y_train.shape}")
    print(f"y_val shape: {y_val.shape}")
    print(f"y_test shape: {y_test.shape}")
