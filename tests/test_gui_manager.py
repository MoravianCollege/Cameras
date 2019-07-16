from gui_manager import GUIManager
from unittest.mock import MagicMock, patch

manager = GUIManager()

manager.app = MagicMock()

@patch.object(manager, "run_camera_screen", side_effect=manager.run_camera_screen)
@patch.object(manager, "run_running_screen", side_effect=manager.run_running_screen)
@patch.object(manager, "update_camera_screen", side_effect=manager.update_camera_screen)
@patch.object(manager, "update_running_screen", side_effect=manager.update_running_screen)
@patch.object(manager, "do_processing", side_effect=manager.advance_screen)
def test_general_run_through(mock_run_camera, mock_run_running, mock_camera_update, mock_running_update, mock_processing):

    # camera_update = manager.update_camera_screen
    # with patch.object(manager, "update_camera_screen") as mock_camera_update:
    #     def side_effect(status, frame):
    #         return camera_update(status, frame)
    #     mock_camera_update.side_effect = side_effect

    manager.start(1.0, 1.0)

    assert mock_run_camera.called
    assert mock_camera_update.called

    assert mock_run_running.called
    assert mock_running_update.called

    assert mock_processing.called
    assert manager.current_screen == 3

    manager.return_to_start()
    assert manager.current_screen == 0
    assert manager.stop_processes