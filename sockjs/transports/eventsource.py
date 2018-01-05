""" iframe-eventsource transport """
from aiohttp import web, hdrs
from sockjs.protocol import ENCODING

from .base import StreamingTransport
from .utils import CACHE_CONTROL, session_cookie


class EventsourceTransport(StreamingTransport):

    def send(self, text):
        blob = ''.join(('data: ', text, '\r\n\r\n')).encode(ENCODING)
        self.response.write(blob)

        self.size += len(blob)
        if self.size > self.maxsize:
            return True
        else:
            return False

    async def process(self):
        headers = list(
            ((hdrs.CONTENT_TYPE, 'text/event-stream'),
             (hdrs.CACHE_CONTROL, CACHE_CONTROL)) +
            session_cookie(self.request))

        # open sequence (sockjs protocol)
        resp = self.response = web.StreamResponse(headers=headers)
        await resp.prepare(self.request)
        resp.write(b'\r\n')

        # handle session
        await self.handle_session()

        return resp
