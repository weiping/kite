// 语音速记入口状态机：长按开始录音，松手提交，可中途取消。
// 纯逻辑（平台录音 IO 在上层 widget），可单测。
// 满足 REQ-CAP-VOICE（入口）/ REQ-CAP-VOICE-RAW（取消不持久化）。

enum VoiceState { idle, recording, submitted, cancelled }

class VoiceEntry {
  VoiceState _state = VoiceState.idle;
  VoiceState get state => _state;
  final List<String> _submitted = [];

  /// 长按开始：进入录音态。
  void onStart() {
    if (_state == VoiceState.idle) _state = VoiceState.recording;
  }

  /// 松手提交：返回捕获 id，转入 submitted。
  String onSubmit() {
    if (_state != VoiceState.recording) {
      throw StateError('not recording');
    }
    final id = 'cap-${_submitted.length}';
    _submitted.add(id);
    _state = VoiceState.submitted;
    return id;
  }

  /// 中途取消：不产生任何持久化记录（charter 第1条）。
  void onCancel() {
    if (_state == VoiceState.recording) _state = VoiceState.cancelled;
  }

  List<String> get submitted => List.unmodifiable(_submitted);
}
