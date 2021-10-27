import logging
import re
import asyncio
import asyncssh
import sys
import aiohttp
from datetime import datetime, timezone
from functools import partial
from purl import URL

# Map hostname to SSHClient
workers = {}
# Maps UUID4 to SSH channel
processes = {}


logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, session, base):
        self.session = session
        self.base = URL(base).add_path_segment("job")

    async def get(self, pk):
        url = self.base.add_path_segment(pk).add_path_segment("")
        async with self.session.get(url.as_string()) as response:
            response.raise_for_status()

    async def update(self, pk, payload):
        url = self.base.add_path_segment(pk).add_path_segment("")
        async with self.session.patch(url.as_string(), json=payload) as response:
            response.raise_for_status()

    async def process(self, url, payload):
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()


class BrokerSSHServerSession(asyncssh.SSHServerSession):
    def __init__(self, api):
        self.api = api

    def connection_made(self, channel):
        self.channel = channel

    def pty_requested(self, term_type, term_size, term_modes):
        return False

    def shell_requested(self):
        return False

    def subsystem_requested(self, subsystem):
        return False

    async def exec_requested(self, pk):
        try:
            job = await self.api.get(pk)
        except aiohttp.ClientError as e:
            await self.channel.close()
            await self.channel.wait_closed()
            logger.error(f"Failed to fetch job: {e}")
            return False
        worker = job.get("worker")
        wid = worker.get("id")
        if wid not in workers:
            connection, client = await asyncssh.create_connection(
                WorkerSSHClient, worker.get("hostname"), worker.get("port")
            )
            workers[wid] = (connection, client)
        else:
            connection, client = workers[wid]
        if pk not in processes:
            session_factory = partial(WorkerSSHClientSession, self.api, job)
            self.process = await connection.create_session(
                session_factory, command=job.get("command"), encoding="utf-8"
            )
            processes[pk] = self.process
        else:
            self.process = processes[pk]
        return True

    def eof_received(self):
        return True

    def break_received(self, msec):
        return False

    def signal_received(self, signal):
        self.process.channel.send_signal(signal)


class BrokerSSHServer(asyncssh.SSHServer):
    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api

    def connection_made(self, conn):
        self.connnection = conn

    async def begin_auth(self, username):
        # TODO: Fetch config for username from Django
        async with self.api.get("...") as response:
            user = await response.json()
        self.connection.set_authorized_keys("")
        return True

    def public_key_auth_supported(self):
        return True

    def session_requested(self):
        return BrokerSSHServerSession(self.api)


class WorkerSSHClientSession(asyncssh.SSHClientSession):
    def __init__(self, api, job, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api = api
        self.pk = job.get("id")
        self.process = job.get("process")
        self.filters = [re.compile(p) for p in job.get("filters", [])]

    def connection_made(self, chan):
        self.channel = chan

    async def session_started(self):
        logger.debug(f"session_started: {self}")
        payload = {"started": datetime.now(timezone.utc).isoformat()}
        await self.api.update(self.pk, payload)

    async def connection_lost(self, exc):
        logger.debug(f"connection_lost: {self}")
        payload = {"finished": datetime.now(timezone.utc).isoformat(), "running": False}
        await self.api.update(self.pk, payload)

    async def exit_status_received(self, status):
        logger.debug(f"exit_status_received: {self}, {status}")
        try:
            await self.api.update(self.pk, {"returncode": status})
        except aiohttp.ClientError as e:
            logger.error(f"Failed to update returncode: {e}")

    async def data_received(self, data, datatype):
        logger.debug(f"data_received: {self}, {data}, {datatype}")
        if not self.process:
            return
        if not any([p.match(data) for p in self.filters]):
            return
        payload = {"data": data, "datatype": datatype}
        # Fire&Forget: Send off task but don't wait for it. This is to prevent
        # a bottleneck when a lot of data is received.
        asyncio.create_task(self.api.process(self.processing, payload))


class WorkerSSHClient(asyncssh.SSHClient):
    def validate_host_public_key(self, host, addr, port, key):
        return True

    def connection_made(self, conn):
        self.connection = conn
        print("Connection made to %s." % conn.get_extra_info("peername")[0])

    def connection_lost(self, exc):
        logger.error(f"Connection lost to {self}")
        del workers["TODO"]

    def auth_completed(self):
        workers["TODO"] = self
        print("Authentication successful.")


loop = asyncio.get_event_loop()

timeout = aiohttp.ClientTimeout(total=60)
session = aiohttp.ClientSession(timeout=timeout)
server_factory = partial(BrokerSSHServer, session)
try:
    loop.run_until_complete(
        asyncssh.create_server(
            server_factory, "", 8022, server_host_keys=["ssh_host_key"]
        )
    )
except (OSError, asyncssh.Error) as exc:
    sys.exit("Error starting server: " + str(exc))

loop.run_forever()
