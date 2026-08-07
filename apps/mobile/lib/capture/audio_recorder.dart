import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart' as rec;

/// 端侧录音封装（record 库）。平台层 IO：麦克风。
/// 用 rec alias 避免与本类名冲突。start/stop/cancel。
class VoiceRecorder {
  final rec.AudioRecorder _rec = rec.AudioRecorder();
  bool _recording = false;

  Future<bool> hasPermission() => _rec.hasPermission();

  Future<void> start() async {
    if (!await _rec.hasPermission()) return;
    final dir = await getTemporaryDirectory();
    final path = '${dir.path}/kite_recording.m4a';
    await _rec.start(const rec.RecordConfig(encoder: rec.AudioEncoder.aacLc), path: path);
    _recording = true;
  }

  Future<String?> stop() async {
    if (!_recording) return null;
    _recording = false;
    return _rec.stop();
  }

  Future<void> cancel() async {
    if (_recording) {
      await _rec.cancel();
      _recording = false;
    }
  }
}
