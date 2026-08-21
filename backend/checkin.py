"""Asynchronous conference check-in and badge-print workflow.

This local prototype uses asyncio.Queue as the vendor message-queue adapter.
The boundary is deliberately isolated so it can later be replaced by
RabbitMQ, SQS, Azure Service Bus, or the vendor's real queue without changing
the check-in state machine.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass

from .database import get_db_connection


@dataclass
class PrintRequest:
    job_id: str
    attendee_id: str
    attendee_name: str
    qr_code: str


class BadgeQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None

    async def start(self):
        self.ensure_tables()
        self.seed_attendees()
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        if self.worker_task and not self.worker_task.done():
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        self.worker_task = None

    def ensure_tables(self):
        conn = get_db_connection()
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS event_attendees (
            attendee_id TEXT PRIMARY KEY,
            attendee_name TEXT NOT NULL,
            qr_code TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'not_checked_in',
            job_id TEXT,
            checked_in_at TEXT
        );

        CREATE TABLE IF NOT EXISTS badge_print_jobs (
            job_id TEXT PRIMARY KEY,
            attendee_id TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );
        """)
        conn.commit()
        conn.close()

    def seed_attendees(self):
        conn = get_db_connection()
        conn.executemany(
            """INSERT OR IGNORE INTO event_attendees
               (attendee_id, attendee_name, qr_code)
               VALUES (?, ?, ?)""",
            [
                ("A001", "Aisha Mokoena", "QR-A001"),
                ("A002", "Daniel Naidoo", "QR-A002"),
                ("A003", "Lebo Dlamini", "QR-A003"),
            ],
        )
        conn.commit()
        conn.close()

    def request_checkin(self, qr_code: str):
        conn = get_db_connection()
        row = conn.execute(
            """SELECT attendee_id, attendee_name, qr_code, status, job_id
               FROM event_attendees WHERE qr_code = ?""",
            (qr_code,),
        ).fetchone()

        if not row:
            conn.close()
            raise ValueError("Attendee QR code not found")

        attendee_id, attendee_name, qr_code, status, existing_job_id = row

        # This is the idempotency gate. A second scan while pending OR after
        # completion cannot create another print job.
        if status in ("pending", "checked_in"):
            conn.close()
            return {
                "attendee_id": attendee_id,
                "attendee_name": attendee_name,
                "status": status,
                "job_id": existing_job_id,
                "duplicate": True,
                "message": "No second badge was queued.",
            }

        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        conn.execute(
            """UPDATE event_attendees
               SET status='pending', job_id=?
               WHERE attendee_id=?""",
            (job_id, attendee_id),
        )
        conn.execute(
            """INSERT INTO badge_print_jobs
               (job_id, attendee_id, status, created_at)
               VALUES (?, ?, 'queued', ?)""",
            (job_id, attendee_id, now),
        )
        conn.commit()
        conn.close()

        self.queue.put_nowait(
            PrintRequest(job_id, attendee_id, attendee_name, qr_code)
        )

        return {
            "attendee_id": attendee_id,
            "attendee_name": attendee_name,
            "status": "pending",
            "job_id": job_id,
            "duplicate": False,
            "message": "Print request queued. Waiting for asynchronous confirmation.",
        }

    async def _worker(self):
        while True:
            request = await self.queue.get()
            try:
                # Simulates the vendor processing the queue message.
                # Replace this boundary with a real vendor queue publisher/
                # consumer when credentials/infrastructure are available.
                await asyncio.sleep(0.35)
                await self.receive_vendor_webhook(request.job_id, "completed")
            finally:
                self.queue.task_done()

    async def receive_vendor_webhook(self, job_id: str, status: str):
        """Process the vendor callback exactly once for a print job."""
        conn = get_db_connection()
        job = conn.execute(
            "SELECT attendee_id, status FROM badge_print_jobs WHERE job_id=?",
            (job_id,),
        ).fetchone()

        if not job:
            conn.close()
            raise ValueError("Unknown print job")

        attendee_id, current_status = job

        # Idempotent webhook handling: repeated/out-of-order completion
        # notifications cannot create another check-in or badge job.
        if current_status == "completed":
            conn.close()
            return

        completed_at = datetime.now(timezone.utc).isoformat()

        if status == "completed":
            conn.execute(
                """UPDATE badge_print_jobs
                   SET status='completed', completed_at=?
                   WHERE job_id=?""",
                (completed_at, job_id),
            )
            conn.execute(
                """UPDATE event_attendees
                   SET status='checked_in', checked_in_at=?
                   WHERE attendee_id=? AND job_id=? AND status='pending'""",
                (completed_at, attendee_id, job_id),
            )
        else:
            conn.execute(
                """UPDATE badge_print_jobs
                   SET status='failed', completed_at=?
                   WHERE job_id=?""",
                (completed_at, job_id),
            )
            conn.execute(
                """UPDATE event_attendees
                   SET status='not_checked_in'
                   WHERE attendee_id=? AND job_id=?""",
                (attendee_id, job_id),
            )

        conn.commit()
        conn.close()

    def get_attendee(self, qr_code: str):
        conn = get_db_connection()
        row = conn.execute(
            """SELECT attendee_id, attendee_name, status, job_id, checked_in_at
               FROM event_attendees WHERE qr_code=?""",
            (qr_code,),
        ).fetchone()
        conn.close()

        if not row:
            return None

        return {
            "attendee_id": row[0],
            "attendee_name": row[1],
            "status": row[2],
            "job_id": row[3],
            "checked_in_at": row[4],
        }

    def list_attendees(self):
        conn = get_db_connection()
        rows = conn.execute(
            """SELECT attendee_id, attendee_name, qr_code, status, job_id,
                      checked_in_at
               FROM event_attendees ORDER BY attendee_id"""
        ).fetchall()
        conn.close()

        return [
            {
                "attendee_id": r[0],
                "attendee_name": r[1],
                "qr_code": r[2],
                "status": r[3],
                "job_id": r[4],
                "checked_in_at": r[5],
            }
            for r in rows
        ]
