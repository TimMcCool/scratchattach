// Attach to scratchattach websocket
// https://github.com/TimMcCool/scratchattach/issues/492

const cloudUrl = 'ws://127.0.0.1:8080';  // = localhost:8080. This only works if you have a websocket running locally (probably using scratchattach)
// const cloudUrl = 'wss://clouddata.turbowarp.org';  // use this if you want to use the turbowarp server.

let this_project_id = '100';

async function getFName() {
    const id = await EditorPreload.getInitialFile()
    if (id === null) return this_project_id
    const file = await EditorPreload.getFile(id)
    return file.name;
}

function getUsername() {
    return window.localStorage['tw:username'] ?? "player";
}

const intervalId = setInterval(async () => {
    if (vm.runtime.ioDevices.cloud.provider) {
        // Stop the interval from running again
        clearInterval(intervalId);
        this_project_id = await getFName();

        console.log('found cloud', vm.runtime.ioDevices.cloud.provider, 'set project id to', this_project_id);

        const provider = vm.runtime.ioDevices.cloud.provider;
        const channel = provider._channel;
        const socket = new WebSocket(cloudUrl);

        provider.updateVariable = (name, value) => {
            console.log("Set", name, "=", value);
            channel.postMessage({name, value});

            socket.send(JSON.stringify({
                method: 'set',
                user: getUsername(),
                project_id: this_project_id,
                name: name,
                value: value
            }));
        };

        socket.addEventListener("open", (event) => {
            socket.send(JSON.stringify({
                method: 'handshake',
                user: getUsername(),
                project_id: this_project_id

            }));
        });

        socket.addEventListener("message", (event) => {
            const raw = event.data;
            let data;
            try {
                data = JSON.parse(raw);
            } catch (e) {
                data = {};
            }

            // only assume method, name, and value to be specified
            const {method, project_id, name, value, timestamp, user} = data;

            if (project_id && project_id != this_project_id) {
                console.log("Ignored message from server:", raw);
                return;
            }

            if (method == 'set') {
                console.log(`set ${name} to ${value} (${raw})`);
                const stage = vm.runtime.getTargetForStage();
                stage.lookupVariableByNameAndType(name).value = value;
            } else {
                console.log("Message from server ", raw);
            }
        });
    }
}, 1000); // Check every 1000 ms
