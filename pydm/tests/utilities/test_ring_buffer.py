import numpy as np
import pytest
from pydm.utilities.ring_buffer import RingBuffer, MINIMUM_BUFFER_SIZE


class TestRingBufferConstruction:
    def test_basic_construction(self):
        rb = RingBuffer(2, 10)
        assert rb.capacity == 10
        assert rb.count == 0
        assert len(rb) == 0
        assert not rb.is_full

    def test_minimum_capacity_clamping(self):
        rb = RingBuffer(2, 0)
        assert rb.capacity == MINIMUM_BUFFER_SIZE
        rb2 = RingBuffer(2, 1)
        assert rb2.capacity == MINIMUM_BUFFER_SIZE

    def test_custom_dtype(self):
        rb = RingBuffer(2, 5, dtype=np.float32)
        rb.append(1.0, 2.0)
        data = rb.get_ordered_data()
        assert data.dtype == np.float32


class TestRingBufferAppend:
    def test_single_append(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        assert rb.count == 1
        assert not rb.is_full

    def test_wrong_number_of_values(self):
        rb = RingBuffer(2, 5)
        with pytest.raises(ValueError, match="Expected 2 values"):
            rb.append(1.0)
        with pytest.raises(ValueError, match="Expected 2 values"):
            rb.append(1.0, 2.0, 3.0)

    def test_fill_to_capacity(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        assert rb.count == 3
        assert rb.is_full

    def test_wrap_around(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        rb.append(4.0, 40.0)  # overwrites first
        assert rb.count == 3
        assert rb.is_full


class TestRingBufferGetOrderedData:
    def test_empty(self):
        rb = RingBuffer(2, 5)
        data = rb.get_ordered_data()
        assert data.shape == (2, 0)

    def test_empty_single_row(self):
        rb = RingBuffer(2, 5)
        data = rb.get_ordered_data(row=0)
        assert data.shape == (0,)

    def test_partial_fill(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        data = rb.get_ordered_data()
        assert data.shape == (2, 3)
        np.testing.assert_array_equal(data[0], [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(data[1], [10.0, 20.0, 30.0])

    def test_full_no_wrap(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [1.0, 2.0, 3.0])
        np.testing.assert_array_equal(data[1], [10.0, 20.0, 30.0])

    def test_wrap_around_order(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        rb.append(4.0, 40.0)
        rb.append(5.0, 50.0)
        data = rb.get_ordered_data()
        # Oldest should be 3.0, newest should be 5.0
        np.testing.assert_array_equal(data[0], [3.0, 4.0, 5.0])
        np.testing.assert_array_equal(data[1], [30.0, 40.0, 50.0])

    def test_single_row(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        x = rb.get_ordered_data(row=0)
        y = rb.get_ordered_data(row=1)
        np.testing.assert_array_equal(x, [1.0, 2.0])
        np.testing.assert_array_equal(y, [10.0, 20.0])


class TestRingBufferGetNewestOldest:
    def test_empty_returns_none(self):
        rb = RingBuffer(2, 5)
        assert rb.get_newest() is None
        assert rb.get_oldest() is None
        assert rb.get_newest(row=0) is None
        assert rb.get_oldest(row=0) is None

    def test_single_element(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        assert rb.get_newest(row=0) == 1.0
        assert rb.get_newest(row=1) == 10.0
        assert rb.get_oldest(row=0) == 1.0
        assert rb.get_oldest(row=1) == 10.0

    def test_partial_fill(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        assert rb.get_newest(row=0) == 3.0
        assert rb.get_oldest(row=0) == 1.0

    def test_after_wrap(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        rb.append(4.0, 40.0)
        assert rb.get_newest(row=0) == 4.0
        assert rb.get_oldest(row=0) == 2.0

    def test_all_rows(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        newest = rb.get_newest()
        np.testing.assert_array_equal(newest, [1.0, 10.0])


class TestRingBufferClear:
    def test_clear(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.clear()
        assert rb.count == 0
        assert rb.capacity == 5
        data = rb.get_ordered_data()
        assert data.shape == (2, 0)


class TestRingBufferResize:
    def test_resize_larger(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.resize(5)
        assert rb.capacity == 5
        assert rb.count == 2
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [1.0, 2.0])

    def test_resize_smaller_preserves_recent(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        rb.append(4.0, 40.0)
        rb.resize(2)
        assert rb.capacity == 2
        assert rb.count == 2
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [3.0, 4.0])
        np.testing.assert_array_equal(data[1], [30.0, 40.0])

    def test_resize_same_is_noop(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        rb.resize(5)
        assert rb.count == 1
        assert rb.capacity == 5

    def test_resize_clamps_to_minimum(self):
        rb = RingBuffer(2, 5)
        rb.resize(0)
        assert rb.capacity == MINIMUM_BUFFER_SIZE

    def test_resize_after_wrap(self):
        rb = RingBuffer(2, 3)
        for i in range(5):
            rb.append(float(i), float(i * 10))
        rb.resize(4)
        assert rb.capacity == 4
        assert rb.count == 3
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [2.0, 3.0, 4.0])

    def test_append_after_resize(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.resize(5)
        rb.append(3.0, 30.0)
        rb.append(4.0, 40.0)
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [1.0, 2.0, 3.0, 4.0])


class TestRingBufferLoadFromArray:
    def test_load_basic(self):
        rb = RingBuffer(2, 5)
        arr = np.array([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]])
        rb.load_from_array(arr)
        assert rb.count == 3
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [1.0, 2.0, 3.0])

    def test_load_larger_than_capacity(self):
        rb = RingBuffer(2, 3)
        arr = np.array([[1.0, 2.0, 3.0, 4.0, 5.0], [10.0, 20.0, 30.0, 40.0, 50.0]])
        rb.load_from_array(arr)
        # load_from_array expands capacity to fit all data
        assert rb.count == 5
        assert rb.capacity == 5
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [1.0, 2.0, 3.0, 4.0, 5.0])

    def test_load_empty(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        rb.load_from_array(np.array([[],[]]))
        assert rb.count == 0

    def test_append_after_load(self):
        rb = RingBuffer(2, 5)
        arr = np.array([[1.0, 2.0], [10.0, 20.0]])
        rb.load_from_array(arr)
        rb.append(3.0, 30.0)
        assert rb.count == 3
        data = rb.get_ordered_data()
        np.testing.assert_array_equal(data[0], [1.0, 2.0, 3.0])


class TestRingBufferGetPaddedData:
    def test_empty_returns_zeros(self):
        rb = RingBuffer(2, 5)
        padded = rb.get_padded_data()
        assert padded.shape == (2, 5)
        np.testing.assert_array_equal(padded, np.zeros((2, 5)))

    def test_partial_fill_right_aligned(self):
        rb = RingBuffer(2, 5)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        padded = rb.get_padded_data()
        assert padded.shape == (2, 5)
        # Data should be at the right end
        assert padded[0, -1] == 2.0
        assert padded[0, -2] == 1.0
        assert padded[0, 0] == 0.0  # zero-padded

    def test_full_buffer_right_aligned(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        padded = rb.get_padded_data()
        np.testing.assert_array_equal(padded[0], [1.0, 2.0, 3.0])

    def test_wrapped_buffer_right_aligned(self):
        rb = RingBuffer(2, 3)
        rb.append(1.0, 10.0)
        rb.append(2.0, 20.0)
        rb.append(3.0, 30.0)
        rb.append(4.0, 40.0)
        padded = rb.get_padded_data()
        # Should show [2, 3, 4] in chronological order
        np.testing.assert_array_equal(padded[0], [2.0, 3.0, 4.0])
        # Newest at [-1]
        assert padded[0, -1] == 4.0
        # Oldest at [-count] = [-3] = [0]
        assert padded[0, -3] == 2.0
