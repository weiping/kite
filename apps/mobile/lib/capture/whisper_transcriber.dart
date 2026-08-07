import 'package:sherpa_onnx/sherpa_onnx.dart' as sherpa;

/// whisper-small 端侧转写（DEC-CAP-TRANSCRIPTION 选 A 端侧）。
/// init(modelDir) 加载模型；transcribe(wavPath) → 文本。
/// 满足离线优先（charter 第3条）+ 不出站（第1条）+ 可追溯（原文来自 whisper）。
class WhisperTranscriber {
  sherpa.OfflineRecognizer? _recognizer;
  final String _language;

  WhisperTranscriber({String language = 'zh'}) : _language = language;

  bool get isReady => _recognizer != null;

  /// 加载 whisper 模型。modelDir 含 encoder.int8.onnx / decoder.int8.onnx / tokens.txt。
  void init(String modelDir) {
    final config = sherpa.OfflineRecognizerConfig(
      model: sherpa.OfflineModelConfig(
        whisper: sherpa.OfflineWhisperModelConfig(
          encoder: '$modelDir/encoder.int8.onnx',
          decoder: '$modelDir/decoder.int8.onnx',
          language: _language,
          task: 'transcribe',
        ),
        tokens: '$modelDir/tokens.txt',
        numThreads: 2,
        debug: false,
      ),
    );
    _recognizer = sherpa.OfflineRecognizer(config);
  }

  /// 转写 wav 文件 → 文本。需先 init；samples 空返回 null。
  String? transcribe(String wavPath) {
    final rec = _recognizer;
    if (rec == null) return null;
    final wave = sherpa.readWave(wavPath);
    if (wave.samples.isEmpty) return null;
    final stream = rec.createStream();
    stream.acceptWaveform(samples: wave.samples, sampleRate: wave.sampleRate);
    rec.decode(stream);
    return rec.getResult(stream).text;
  }
}
