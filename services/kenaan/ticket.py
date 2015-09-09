
import urlparse

from twisted.internet import reactor, task, defer
from twisted.spread import pb
from twisted.python import log, failure
try:
    from amptrac import client as amptrac
except ImportError as e:
    amptrac = None
    amptracError = e

import config


class Ticket(pb.Copyable, pb.RemoteCopy):
    def __init__(self, tracker, id, author, kind, component, subject):
        self.tracker = tracker
        self.id = id
        self.author = author
        self.kind = kind
        self.component = component
        self.subject = subject

    def __repr__(self):
        return 'Ticket(%r, %d, %r, %r, %r, %r)' % (
            self.tracker, self.id, self.author, self.kind,
            self.component, self.subject)
pb.setUnjellyableForClass(Ticket, Ticket)



class TicketChangeListener:
    """
    Mixin for a PB Referenceable which accepts ticket change notifications.
    """
    def remote_ticket(self, ticket):
        log.msg(str(ticket))
        self.proto.ticket(ticket)



class TicketChange:
    ticketMessageFormat = (
        'new %(component)s %(kind)s https://tm.tl/#%(id)d by %(author)s: %(subject)s')

    def ticket(self, ticket):
        for (url, channels) in config.TICKET_RULES:
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
            if '@' in netloc:
                netloc = netloc.split('@', 1)[1]
            url = urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
            if ticket.tracker == url:
                for channel in channels:
                    self.join(channel)
                    self.msg(
                        channel,
                        self.ticketMessageFormat % vars(ticket),
                        config.LINE_LENGTH)



class TicketReview:
    """
    Automated review ticket reporting.
    """

    _ticketCall = None

    def signedOn(self):
        self._ticketCall = task.LoopingCall(self.reportAllReviewTickets)
        self._ticketCall.start(60 * 60 * 5)


    def privmsg(self, user, channel, message):
        if 'review branches' in message:
            for (url, channels) in config.TICKET_RULES:
                for existing_channel in channels:
                    if existing_channel == channel:
                        d = self.reportReviewTickets(url, channel)
                        d.addErrback(
                            log.err,
                            "Failed to satisfy review ticket request from "
                            "%r to %r" % (url, channel))


    def connectionLost(self, reason):
        if self._ticketCall is not None:
            self._ticketCall.stop()


    def reportAllReviewTickets(self):
        """
        Call L{reportReviewTickets} with each element of L{config.TICKET_RULES}.
        """
        for (url, channels) in config.TICKET_RULES:
            for channel in channels:
                d = self.reportReviewTickets(url, channel)
                d.addErrback(
                    log.err,
                    "Failed to report review tickets from %r to %r" % (
                        url, channel))


    def reportReviewTickets(self, trackerRoot, channel):
        """
        Retrieve the list of tickets currently up for review from the
        tracker at the given location and report them to the given channel.

        @param trackerRoot: The base URL of the trac instance from which to
        retrieve ticket information.  C{"http://example.com/trac/"}, for
        example.

        @param channel: The channel to which to send the results.

        @return: A Deferred which fires when the report has been completed.
        """
        if amptrac is None:
            f = failure.Failure(amptracError)
            log.err(f, "amptrac not present, can't report tickets.")
            return defer.fail(f)

        d = amptrac.connect(reactor)
        d.addCallback(self._getReviewTickets)
        d.addCallback(self._reportReviewTickets, channel)
        return d


    def _getReviewTickets(self, client):
        """
        Retrieve the list of tickets currently up for review from the
        tracker at the given location.

        @return: A Deferred which fires with a C{list} of C{int}s.  Each
        element is the number of a ticket up for review.
        """
        return client.reviewTickets()


    def _reportReviewTickets(self, reviewTicketInfo, channel):
        """
        Format the given list of ticket numbers and send it to the given channel.
        """
        tickets = self._formatTicketNumbers(reviewTicketInfo)
        self.join(channel)
        if tickets:
            message = "Tickets pending review: https://tm.tl/" + tickets
        else:
            message = "No tickets pending review!"
        self.msg(channel, message)


    def _formatTicketNumbers(self, reviewTicketInfo):
        tickets = []
        for ticket in reviewTicketInfo:
            if ticket['owner']:
                tickets.append('#%d (%s)' % (ticket['id'], ticket['owner']))
            else:
                tickets.append('#%d' % (ticket['id'],))
        return ', '.join(tickets).encode('utf-8')



def _sendTicket(ticket):
    cf = pb.PBClientFactory()
    reactor.connectTCP(config.BOT_HOST, config.BOT_PORT, cf)

    def cbRoot(rootObj):
        return rootObj.callRemote('ticket', ticket)

    rootD = cf.getRootObject()
    rootD.addCallback(cbRoot)
    rootD.addErrback(log.err)
    rootD.addCallback(lambda ign: reactor.stop())

def main(tracker, id, author, kind, component, subject):
    reactor.callWhenRunning(_sendTicket, Ticket(tracker, int(id), author, kind, component, subject))
    reactor.run()
