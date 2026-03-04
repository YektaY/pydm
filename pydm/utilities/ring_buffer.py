"""A fixed-capacity ring buffer backed by a 2D numpy array for O(1) append operations."""

import numpy as np

MINIMUM_BUFFER_SIZE = 2


class RingBuffer:
    """A fixed-capacity ring buffer backed by a 2D numpy array.

    Stores data in (num_rows, capacity) format using a write cursor
    to avoid O(n) np.roll on every insertion.

    Parameters
    ----------
    num_rows : int
        Number of data rows (e.g. 2 for x/y pairs).
    capacity : int
        Maximum number of data points the buffer can hold.
    dtype : numpy dtype, optional
        Data type of the underlying array. Defaults to float.
    """

    def __init__(self, num_rows: int, capacity: int, dtype=float):
        self._num_rows = num_rows
        self._capacity = max(capacity, MINIMUM_BUFFER_SIZE)
        self._dtype = dtype
        self._buffer = np.zeros((num_rows, self._capacity), order="f", dtype=dtype)
        self._cursor = 0
        self._count = 0

    @property
    def capacity(self) -> int:
        """The maximum number of points the buffer can hold."""
        return self._capacity

    @property
    def count(self) -> int:
        """The number of valid data points accumulated."""
        return self._count

    @count.setter
    def count(self, value: int):
        self._count = value

    @property
    def is_full(self) -> bool:
        """Whether the buffer has reached capacity."""
        return self._count >= self._capacity

    def append(self, *values):
        """Append a single data point with one value per row. O(1) operation.

        Parameters
        ----------
        *values : float
            One value per row. Must provide exactly num_rows values.
        """
        if len(values) != self._num_rows:
            raise ValueError(f"Expected {self._num_rows} values, got {len(values)}")
        for i, val in enumerate(values):
            self._buffer[i, self._cursor] = val
        self._cursor = (self._cursor + 1) % self._capacity
        if self._count < self._capacity:
            self._count += 1

    def get_ordered_data(self, row: int = None) -> np.ndarray:
        """Return the valid data in chronological (insertion) order.

        Parameters
        ----------
        row : int, optional
            If specified, return only this row's data as a 1D array.
            Otherwise return all rows as a 2D array.

        Returns
        -------
        np.ndarray
            Shape (num_rows, count) if row is None, or (count,) if row is int.
        """
        if self._count == 0:
            if row is not None:
                return np.empty(0, dtype=self._dtype)
            return np.empty((self._num_rows, 0), dtype=self._dtype)

        if self._count < self._capacity:
            # Buffer not yet full — data is contiguous from 0 to cursor
            data = self._buffer[:, : self._count].copy()
        else:
            # Buffer wrapped — reorder around cursor
            data = np.concatenate(
                (self._buffer[:, self._cursor :], self._buffer[:, : self._cursor]),
                axis=1,
            )

        if row is not None:
            return data[row]
        return data

    def get_newest(self, row: int = None):
        """Return the most recently written value(s). O(1).

        Parameters
        ----------
        row : int, optional
            If specified, return only that row's latest value.

        Returns
        -------
        float or np.ndarray or None
            None if buffer is empty.
        """
        if self._count == 0:
            return None
        idx = (self._cursor - 1) % self._capacity
        if row is not None:
            return self._buffer[row, idx]
        return self._buffer[:, idx].copy()

    def get_oldest(self, row: int = None):
        """Return the oldest valid value(s). O(1).

        Parameters
        ----------
        row : int, optional
            If specified, return only that row's oldest value.

        Returns
        -------
        float or np.ndarray or None
            None if buffer is empty.
        """
        if self._count == 0:
            return None
        if self._count < self._capacity:
            idx = 0
        else:
            idx = self._cursor
        if row is not None:
            return self._buffer[row, idx]
        return self._buffer[:, idx].copy()

    def clear(self):
        """Reset the buffer, zeroing all data."""
        self._buffer = np.zeros((self._num_rows, self._capacity), order="f", dtype=self._dtype)
        self._cursor = 0
        self._count = 0

    def resize(self, new_capacity: int):
        """Resize the buffer, preserving the most recent data.

        Parameters
        ----------
        new_capacity : int
            The new capacity. Will be clamped to MINIMUM_BUFFER_SIZE.
        """
        new_capacity = max(new_capacity, MINIMUM_BUFFER_SIZE)
        if new_capacity == self._capacity:
            return

        old_data = self.get_ordered_data()
        old_count = self._count

        self._capacity = new_capacity
        self._buffer = np.zeros((self._num_rows, new_capacity), order="f", dtype=self._dtype)

        if old_count > 0:
            keep = min(old_count, new_capacity)
            self._buffer[:, :keep] = old_data[:, -keep:]
            self._count = keep
            self._cursor = keep % new_capacity
        else:
            self._count = 0
            self._cursor = 0

    def load_from_array(self, data: np.ndarray):
        """Bulk load data from a numpy array, replacing buffer contents.

        The data is assumed to be in chronological order. If the data is
        larger than the buffer capacity, the buffer is resized to fit.

        Parameters
        ----------
        data : np.ndarray
            Array of shape (num_rows, n_points).
        """
        if data.ndim == 1:
            data = data.reshape(1, -1)

        n_points = data.shape[1]
        if n_points == 0:
            self.clear()
            return

        # Resize internal buffer if shapes don't match
        if data.shape[0] != self._num_rows:
            self._num_rows = data.shape[0]

        # Expand capacity if needed to fit all the data
        if n_points > self._capacity:
            self._capacity = n_points

        self._buffer = np.zeros((self._num_rows, self._capacity), order="f", dtype=self._dtype)
        self._buffer[:, :n_points] = data
        self._count = n_points
        self._cursor = n_points % self._capacity

    def get_padded_data(self) -> np.ndarray:
        """Return a (num_rows, capacity) array with data right-aligned.

        Zeros fill the left side, valid data is at the right. This matches
        the old np.roll-based layout where newest data is at index [-1]
        and oldest valid data is at index [-count].

        Used for backward compatibility with code that indexes data_buffer
        directly (e.g. ArchivePlotCurveItem).
        """
        result = np.zeros((self._num_rows, self._capacity), order="f", dtype=self._dtype)
        if self._count > 0:
            ordered = self.get_ordered_data()
            result[:, -self._count :] = ordered
        return result

    def __len__(self) -> int:
        return self._count
