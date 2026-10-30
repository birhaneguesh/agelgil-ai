import asyncio
import signal
import sys

_STOP = asyncio.Event()


async def main() -> None:
    print("writer: ready", flush=True)
    n = 0
    while not _STOP.is_set():
        try:
            await asyncio.wait_for(_STOP.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            n += 1
            print(f"writer: heartbeat {n}", flush=True)
    print("writer: stopped", flush=True)


def _sig(_signum, _frame) -> None:
    _STOP.set()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
