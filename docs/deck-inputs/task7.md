# Deck Input - Task 7: Futuristic Offline HUD, Voice Engine & Niche Routines

## Slide Metadata
- **Slide Title**: Futuristic Offline HUD, Voice Engine & Niche Routines
- **Topic**: User Interface, Speech Processing & Autonomous Routines
- **Time Allocation**: 2 Minutes

---

## Slide Content & Bullets

### 1. Futuristic Cyberpunk Local HUD (`127.0.0.1:8765`)
- Built using **pure HTML, CSS, and Vanilla JavaScript** with **zero build step and zero external CDN dependencies**.
- 100% offline functionality.
- Key features:
  - Real-time animated transcript with typing effect.
  - Live execution plan tree showing step status (`pending`, `executing`, `completed`, `rolled_back`).
  - Interactive diff approval cards for Tier L2/L3 requests.
  - Telemetry strip: CPU load, RAM usage, battery percentage, and audit chain integrity badge.

### 2. Multi-Modal Voice Engine (`lazy-voice`)
- Wake phrase detection: *"wake up, daddy's home"* (configurable via Vosk grammar recognition).
- Speech-to-Text: Offline Vosk acoustic model.
- Text-to-Speech: Low-latency `espeak-ng` synthesis.
- Graceful text fallback ensures full system usability on headless or muted systems.

### 3. Niche Intelligence & Overnight Chores (`lazy-routines`)
- **Niche Feed Ranker**: Pure Python TF-IDF cosine similarity with online-learned user accept/dismiss weights and 20% exploration share.
- **Morning Briefing Generator**: Synthesizes tasks, pending approvals, completed overnight chores, and cited niche articles.

---

## Speaker Talking Points
1. "The user experience of Lazy OS is designed to feel like operating an advanced cockpit. The HUD connects over local WebSockets to provide instant visual feedback on every step."
2. "Notice that there are no external CDNs or cloud dependencies. Even if the network cable is unplugged, the speech engine, the local HUD, and the neural planner work flawlessly."
3. "Our niche feed reader extracts structured knowledge while citing source IDs, ensuring the user stays informed without being overwhelmed by hallucinations."

---

## Evidence & Verification References
- [hud/](file:///c:/Users/len/OS/hud/): Static HUD HTML, CSS, and JS assets.
- [src/lazy/voice/](file:///c:/Users/len/OS/src/lazy/voice/): Wake detector, STT, and TTS engines.
- [src/lazy/routines/](file:///c:/Users/len/OS/src/lazy/routines/): Morning briefing generator and niche feed ranker.
- [tests/results/M3.1.log](file:///c:/Users/len/OS/tests/results/M3.1.log): HUD offline validation test log.
- [tests/results/M3.4.log](file:///c:/Users/len/OS/tests/results/M3.4.log): Niche feed TF-IDF ranking and feedback tests.
