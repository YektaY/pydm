import numpy as np
import pytest
from unittest.mock import patch

from pydm.widgets.image import ImageUpdateThread, PyDMImageView


@pytest.fixture
def image_view(qtbot):
    """Create a PyDMImageView widget for testing."""
    view = PyDMImageView()
    qtbot.addWidget(view)
    return view


def test_rgb_image_ignores_colormap_levels(image_view):
    """Verify that RGB images use their own data range for levels instead of
    the colormap min/max settings intended for mono images.

    Parameters
    ----------
    image_view : PyDMImageView
        Fixture-provided image view widget.
    """
    image_view.cm_min = 0.0
    image_view.cm_max = 4095.0
    image_view._normalize_data = False
    image_view.needs_redraw = True
    image_view._image_width = 4

    rgb_img = np.random.randint(0, 256, (4, 4, 3), dtype=np.uint8)
    image_view.image_waveform = rgb_img

    thread = ImageUpdateThread(image_view)
    emitted = []
    thread.updateSignal.connect(lambda data: emitted.append(data))
    thread.run()

    assert len(emitted) == 1
    mini, maxi, _ = emitted[0]
    assert mini == rgb_img.min()
    assert maxi == rgb_img.max()


def test_mono_image_uses_colormap_levels(image_view):
    """Verify that mono images respect colormap min/max when normalize is off.

    Parameters
    ----------
    image_view : PyDMImageView
        Fixture-provided image view widget.
    """
    image_view.cm_min = 0.0
    image_view.cm_max = 4095.0
    image_view._normalize_data = False
    image_view.needs_redraw = True
    image_view._image_width = 4

    mono_img = np.random.randint(0, 4096, (4, 4), dtype=np.uint16)
    image_view.image_waveform = mono_img

    thread = ImageUpdateThread(image_view)
    emitted = []
    thread.updateSignal.connect(lambda data: emitted.append(data))
    thread.run()

    assert len(emitted) == 1
    mini, maxi, _ = emitted[0]
    assert mini == 0.0
    assert maxi == 4095.0
