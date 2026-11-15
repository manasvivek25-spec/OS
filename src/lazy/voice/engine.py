"""Unified Voice Engine for Lazy OS (wake phrase, STT, TTS, text fallback, and latency probes)."""
from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from lazy.voice.stt import STTEngine
from lazy.voice.tts import TTSEngine
from lazy.voice.wake import WakeDetector


class VoiceEngine:
    """Coordinates voice wake detection, STT transcription, TTS synthesis, and latency probes."""

    def __init__(
        self,
        wake_detector: Optional[WakeDetector] = None,
        stt_engine: Optional[STTEngine] = None,
        tts_engine: Optional[TTSEngine] = None,
        config_path: Optional[Path | str] = None,
    ):
        self.wake_detector = wake_detector or WakeDetector(config_path=config_path)
        self.stt = stt_engine or STTEngine()
        self.tts = tts_engine or TTSEngine()

        # Latency probe collectors
        self.stt_latencies: List[float] = []
        self.wake_latencies: List[float] = []
        self.tts_latencies: List[float] = []

    def process_audio(self, audio_path: Path | str) -> Dict[str, Any]:
        """Process input speech audio file: STT transcription + wake phrase detection."""
        transcript, stt_ms = self.stt.transcribe_wav(audio_path)
        self.stt_latencies.append(stt_ms)

        wake_ok, directive, wake_ms = self.wake_detector.extract_directive(transcript)
        self.wake_latencies.append(wake_ms)

        return {
            "source": "voice",
            "audio_path": str(audio_path),
            "transcript": transcript,
            "wake_detected": wake_ok,
            "directive": directive,
            "stt_latency_ms": round(stt_ms, 2),
            "wake_latency_ms": round(wake_ms, 2),
            "total_latency_ms": round(stt_ms + wake_ms, 2),
        }

    def speak(self, text: str, output_path: Optional[Path | str] = None) -> Dict[str, Any]:
        """Synthesize text into speech audio and record TTS latency probe."""
        if not output_path:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            output_path = tmp.name
            tmp.close()

        out_file, tts_ms = self.tts.synthesize_wav(text, output_path)
        self.tts_latencies.append(tts_ms)

        return {
            "text": text,
            "audio_path": str(out_file),
            "tts_latency_ms": round(tts_ms, 2),
        }

    def text_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback pathway when voice is disabled, optional, or silent."""
        cleaned, _ = self.stt.text_fallback(text)
        return {
            "source": "text",
            "transcript": cleaned,
            "wake_detected": True,
            "directive": cleaned,
            "total_latency_ms": 0.01,
        }

    def get_latency_summary(self) -> Dict[str, Any]:
        """Calculate statistical distribution (mean, p50, p95) for all voice probes."""
        def calc_stats(samples: List[float]) -> Dict[str, float]:
            if not samples:
                return {"count": 0, "mean": 0.0, "p50": 0.0, "p95": 0.0}
            s = sorted(samples)
            mean = sum(s) / len(s)
            p50 = s[len(s) // 2]
            p95 = s[int(len(s) * 0.95)]
            return {
                "count": len(s),
                "mean": round(mean, 2),
                "p50": round(p50, 2),
                "p95": round(p95, 2),
            }

        return {
            "stt": calc_stats(self.stt_latencies),
            "wake": calc_stats(self.wake_latencies),
            "tts": calc_stats(self.tts_latencies),
        }
