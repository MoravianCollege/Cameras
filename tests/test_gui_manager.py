from Cameras.gui_manager import GUIManager
from unittest.mock import MagicMock, patch


# with patch.object(GUIManager, "get_alert_sound"):
manager = GUIManager()

manager.app = MagicMock()
manager.ding_sound = MagicMock()

@patch.object(manager, "run_camera_screen", side_effect=manager.run_camera_screen)
@patch.object(manager, "run_running_screen", side_effect=manager.run_running_screen)
@patch.object(manager, "run_results_screen")
@patch.object(manager, "update_camera_screen", side_effect=manager.update_camera_screen)
@patch.object(manager, "update_running_screen", side_effect=manager.update_running_screen)
@patch.object(manager, "update_result_screen")
@patch.object(manager, "do_processing", side_effect=manager.advance_screen)
def test_general_run_through(mock_run_camera, mock_run_running, mock_run_results, mock_camera_update, mock_running_update, mock_results_update, mock_processing):

    manager.start(0.01, 0.01)

    mock_run_camera.assert_called
    mock_camera_update.assert_called

    mock_run_running.assert_called
    mock_running_update.assert_called

    mock_run_results.assert_called
    mock_results_update.assert_called

    mock_processing.assert_called
    assert manager.current_screen == 3

    manager.return_to_start()
    assert manager.current_screen == 0
    assert manager.stop_processes

@patch.object(manager, "run_camera_screen")
@patch.object(manager, "run_running_screen")
@patch.object(manager, "run_results_screen")
def test_advance_method(mock_run_camera, mock_run_running, mock_run_results):

    manager.advance_screen()

    assert manager.current_screen == 1
    mock_run_camera.assert_called

    manager.advance_screen()

    assert manager.current_screen == 2
    mock_run_running.assert_called

    manager.advance_screen()
    assert manager.current_screen == 3
    mock_run_results.assert_called

    manager.advance_screen()
    assert manager.current_screen == 0

    manager.advance_screen(3)
    assert manager.current_screen == 3
    mock_run_results.assert_called

    manager.advance_screen(0)
    assert manager.current_screen == 0
#
@patch.object(manager, "run_camera_screen")
def test_start_method(mock_run_camera):
    manager.start(0.01, 0.01)

    assert manager.current_screen == 1
    assert mock_run_camera.called

    manager.return_to_start()
    assert manager.current_screen == 0
    assert manager.stop_processes