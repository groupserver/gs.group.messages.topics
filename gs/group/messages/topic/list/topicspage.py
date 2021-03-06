# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
from logging import getLogger
log = getLogger('gs.group.messages.topic.list.page')
from zope.cachedescriptors.property import Lazy
from zope.component import getMultiAdapter, createObject
from gs.core import to_ascii
from gs.group.base.page import GroupPage
from gs.group.member.canpost.interfaces import IGSPostingUser
from Products.GSSearch.queries import MessageQuery
from .topicssearch import TopicsSearch


class TopicsPage(GroupPage):
    """List of latest topics in the group."""
    topNTopics = 64

    def __init__(self, context, request):
        GroupPage.__init__(self, context, request)

        try:
            self.start = int(self.request.form.get('start', 0))
        except ValueError:
            self.start = 0
        try:
            self.end = int(self.request.form.get('end', 20))
        except ValueError:
            self.end = 20

        # Swap the start and end, if necessary
        if self.start > self.end:
            tmp = self.end
            self.end = self.start
            self.start = tmp
        nTopics = (self.end - self.start)
        if (nTopics > self.topNTopics):
            m = 'Request for %d topics (%d--%d) from %s (%s) on ' \
                '%s (%s) is too high; returning %d.' % \
                (nTopics, self.start, self.end, self.groupInfo.name,
                 self.groupInfo.id, self.siteInfo.name,
                 self.siteInfo.id, self.topNTopics)
            log.warn(m)
            self.end = self.start + self.topNTopics

        # Ensure we do not walk off the end of the array.
        if self.start > self.numTopics:
            self.start = max((0, self.numTopics - self.topNTopics))

    @Lazy
    def messageQuery(self):
        retval = MessageQuery(self.context)
        return retval

    @Lazy
    def numTopics(self):
        lists = self.context.messages.getProperty('xwf_mailing_list_ids')
        retval = self.messageQuery.topic_count(self.siteInfo.id, lists)
        return retval

    @Lazy
    def summaryLength(self):
        assert hasattr(self, 'start')
        assert hasattr(self, 'end')
        assert self.start <= self.end
        retval = self.end - self.start
        assert retval >= 0
        return retval

    @Lazy
    def topicsSearch(self):
        searchTokens = createObject('groupserver.SearchTextTokens', '')
        retval = TopicsSearch(self.groupInfo.groupObj, searchTokens,
                              self.summaryLength, self.start)
        return retval

    @Lazy
    def topics(self):
        retval = [t for t in self.topicsSearch.topics()]
        return retval

    @Lazy
    def numSticky(self):
        sts = [st for st in self.topics if st['sticky']]
        retval = len(sts)
        return retval

    @Lazy
    def userPostingInfo(self):
        '''Get the User Posting Info

        The reason that I do not assign to a self.userPostingInfo
        variable is that self.context is a bit weird until *after*
        "__init__" has run. Ask me not questions I tell you no lies.
        '''
        g = self.groupInfo.groupObj
        ui = createObject('groupserver.LoggedInUser', self.context)
        retval = getMultiAdapter((g, ui), IGSPostingUser)
        assert retval, 'Posting user is %s' % retval
        return retval

    def get_later_url(self):
        newStart = self.start - self.summaryLength
        if newStart < 0:
            newStart = 0
        newEnd = newStart + self.summaryLength

        if newStart != self.start and newStart:
            url = 'topics.html?start=%d&end=%d' % (newStart, newEnd)
        elif newStart != self.start and not newStart:
            url = 'topics.html'
        else:
            url = ''
        retval = to_ascii(url)
        return retval

    def get_earlier_url(self):
        newStart = self.end - self.numSticky
        newEnd = newStart + self.summaryLength
        if newStart < self.numTopics:
            url = 'topics.html?start=%d&end=%d' % (newStart, newEnd)
        else:
            url = ''
        retval = to_ascii(url)
        return retval

    def get_last_url(self):
        newStart = self.numTopics - self.summaryLength
        newEnd = self.numTopics
        url = 'topics.html?start=%d&end=%d' % (newStart, newEnd)
        retval = to_ascii(url)
        return retval
