import 'package:flutter_test/flutter_test.dart';
import 'package:kite_mobile/capture/voice_entry.dart';

void main() {
  test('test_long_press_records', () {
    // 对齐契约 filter: apps/mobile/test/capture/voice_entry_test.dart::test_long_press_records
    final e = VoiceEntry();
    e.onStart();
    expect(e.state, VoiceState.recording);
    final id = e.onSubmit();
    expect(e.state, VoiceState.submitted);
    expect(e.submitted, [id]);
  });

  test('取消不留存', () {
    final e = VoiceEntry();
    e.onStart();
    e.onCancel();
    expect(e.state, VoiceState.cancelled);
    expect(e.submitted, isEmpty);
  });
}
