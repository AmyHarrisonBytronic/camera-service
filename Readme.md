A simple camera worker, using MQTT

worker will subscribe to a trigger topic and capture and send an image when it is requested by using the mqtt library 
the image will be sent over a set topic to the mqtt broker

needs to have some of the values turned into yaml imports
## Configuration

The service reads `app/dependencies/config.yaml` by default, or a file supplied
on the command line:

```bash
python app/main.py --config /path/to/config.yaml
```

`loadConfig.return_config_value` takes dotted paths — `camera.camera_type`,
`archiving.archive_directory`. Per-camera variants of the config ship
alongside the default: `config_flir.yaml`, `config_gige.yaml`,
`config_ljs.yaml`, `config_opencv.yaml`, `config_pylon.yaml`.

### Running under service-orchestrator

[service-orchestrator](https://github.com/Bytronic-Vision-Intelligence/service-orchestrator)
launches services as `app/main.py --config <path>` with a `.venv` in each
service directory. This service already satisfies that contract.

One caveat: the orchestrator maps a config section to a directory of the same
name, so the checkout must be named `camera-service`. Instances are numbered —
`camera-service-2` shares the `camera-service/` directory and receives
`config-2.yaml`.

`/config.yaml` and `/config-*.yaml` are gitignored, because the orchestrator
writes them into the repository root at startup.

## Development

```bash
python app/setup.py                      # creates .venv/ and installs requirements
.venv/bin/python -m pytest test
```

PySpin is deliberately absent from `requirements.txt`: it ships only as a
Windows wheel, so FLIR machines install it by hand. `cameras_flir.py` is
imported lazily, so every other camera type is unaffected.

OpenCV is pinned to `opencv-python-headless`. This service never calls
`imshow`/`waitKey`, and the plain build needs `libGL.so.1`, which no CI runner
or container provides.

### Running CI locally

`docker-local/` runs `.github/workflows/` on your machine through
[nektos/act](https://github.com/nektos/act). It needs Docker running and is
gitignored in some sibling repos — here it is tracked.

```bash
./docker-local/run.sh -l                        # list jobs
./docker-local/run.sh                           # full push event
./docker-local/run.sh --matrix os:ubuntu-latest # one matrix leg
./docker-local/run.sh --fresh                   # wipe the toolcache first
```

Jobs run one at a time. act shares a single `act-toolcache` volume across job
containers, so concurrent matrix legs corrupt each other's
`/opt/hostedtoolcache` — which surfaces as `Fatal Python error: Bus error`
while loading a native module. Real GitHub gives each leg its own runner.

The `windows-latest` leg runs on a Linux image, so it proves job ordering, not
Windows behaviour. And act bind-mounts the working tree rather than doing a
fresh checkout, so anything depending on what git actually committed can pass
locally and still fail on GitHub.
