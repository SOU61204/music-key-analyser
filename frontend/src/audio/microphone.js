class MicrophoneStreamer {
  constructor(socket) {
    this.socket = socket;

    this.audioContext = null;
    this.microphone = null;
    this.workletNode = null;
    this.stream = null;

    this.inputRate = 48000;
    this.targetRate = 22050;
  }

  async start() {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
      },
    });

    this.audioContext = new AudioContext();

    this.inputRate = this.audioContext.sampleRate;

    console.log(
      "Browser Sample Rate:",
      this.inputRate
    );

    // Load the AudioWorklet processor
    await this.audioContext.audioWorklet.addModule(
      "/audio/recorder-worklet.js"
    );

    this.microphone =
      this.audioContext.createMediaStreamSource(
        this.stream
      );

    this.workletNode = new AudioWorkletNode(
      this.audioContext,
      "recorder-worklet"
    );

    // Receive PCM from the worklet
    this.workletNode.port.onmessage = (event) => {

      const input = event.data;

      const output = this.resample(
        input,
        this.inputRate,
        this.targetRate
      );

      if (
        this.socket.readyState === WebSocket.OPEN
      ) {
        this.socket.send(output.buffer);
      }
    };

    this.microphone.connect(this.workletNode);

    // Keep the worklet alive
    this.workletNode.connect(
      this.audioContext.destination
    );

    console.log("🎤 Streaming microphone...");
  }

  stop() {
    if (this.workletNode) {
      this.workletNode.disconnect();
      this.workletNode = null;
    }

    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }

    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }

    if (this.stream) {
      this.stream
        .getTracks()
        .forEach(track => track.stop());

      this.stream = null;
    }
  }

  resample(input, inputRate, outputRate) {

    if (inputRate === outputRate) {
      return new Float32Array(input);
    }

    const ratio = inputRate / outputRate;

    const newLength = Math.round(
      input.length / ratio
    );

    const output = new Float32Array(newLength);

    let offset = 0;

    for (let i = 0; i < newLength; i++) {

      const next = Math.round(
        (i + 1) * ratio
      );

      let sum = 0;
      let count = 0;

      for (
        let j = offset;
        j < next && j < input.length;
        j++
      ) {
        sum += input[j];
        count++;
      }

      output[i] =
        count > 0
          ? sum / count
          : 0;

      offset = next;
    }

    return output;
  }
}

export default MicrophoneStreamer;