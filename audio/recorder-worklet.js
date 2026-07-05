class RecorderProcessor extends AudioWorkletProcessor {

    process(inputs) {

        const input = inputs[0];

        if (!input.length)
            return true;

        const channel = input[0];

        this.port.postMessage(channel);

        return true;
    }

}

registerProcessor(
    "recorder-worklet",
    RecorderProcessor
);