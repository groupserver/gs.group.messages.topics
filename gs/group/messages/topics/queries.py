# coding=utf-8
import sqlalchemy as sa
from gs.database import getTable, getSession


class TopicsQuery(object):
    def __init__(self):
        self.topicTable = getTable('topic')
        self.postTable = getTable('post')

    def marshal_topic_info(self, x):
        assert x
        retval = {
            'topic_id': x['topic_id'],
            'group_id': x['group_id'],
            'site_id': x['site_id'],
            'subject': x['original_subject'],
            'sticky': x['sticky'],
            'num_posts': x['num_posts'],
            'keywords': x['keywords'],
            'first_post_id': x['first_post_id'],
            'last_post_id': x['last_post_id'],
            'last_post_date': x['last_post_date'],
            'last_post_user_id': x['user_id']}
        assert type(retval) == dict
        assert retval
        return retval

    @property
    def cols(self):
        tt = self.topicTable
        pt = self.postTable
        s1 = sa.select([pt.c.user_id],
                        tt.c.last_post_id == pt.c.post_id).label('user_id')
        retval = [tt.c.topic_id.distinct(), tt.c.last_post_id,
                    tt.c.first_post_id, tt.c.group_id, tt.c.site_id,
                    tt.c.original_subject, tt.c.last_post_date, tt.c.keywords,
                    tt.c.num_posts, tt.c.sticky, s1]
        return retval

    def add_standard_where_clauses(self, statement, siteId, groupId, hidden):
        statement.append_whereclause(self.topicTable.c.site_id == siteId)
        statement.append_whereclause(self.topicTable.c.group_id == groupId)
        if hidden:
            c = self.topicTable.c.hidden != None  # lint:ok
        else:
            c = self.topicTable.c.hidden == None  # lint:ok
        statement.append_whereclause(c)  # lint:ok

    def sticky_topics(self, siteId, groupId):
        tt = self.topicTable

        s = sa.select(self.cols, order_by=sa.desc(tt.c.last_post_date))
        self.add_standard_where_clauses(s, siteId, groupId, False)
        s.append_whereclause(tt.c.sticky != None)  # lint:ok

        session = getSession()
        r = session.execute(s)

        retval = [self.marshal_topic_info(x)for x in r]
        assert type(retval) == list
        return retval

    def recent_non_sitcky_topics(self, siteId, groupId, limit, offset):
        tt = self.topicTable
        s = sa.select(self.cols, order_by=sa.desc(tt.c.last_post_date),
                            limit=limit, offset=offset)
        self.add_standard_where_clauses(s, siteId, groupId, False)
        s.append_whereclause(tt.c.sticky == None)  # lint:ok

        session = getSession()
        r = session.execute(s)

        retval = [self.marshal_topic_info(x)for x in r]
        assert type(retval) == list
        return retval

    def search(self, searchTokens, siteId, groupId, limit=12, offset=0):
        tt = self.topicTable
        pt = self.postTable
        # SELECT topic.topic_id from topic, post
        #   WHERE topic.topic_id = post.topic_id
        #     AND topic.site_id = siteId
        #     AND topic.group_id = groupId
        #     AND post.fts_vectors @@ to_tsquery(kw1 & kw2 & ... & kwn)
        #   ORDER_BY DESC(topic.last_post_date)
        #   LIMIT = limit
        #   OFFSET = offset;
        s = sa.select(self.cols, order_by=sa.desc(tt.c.last_post_date),
                            limit=limit, offset=offset)
        s.append_whereclause(tt.c.topic_id == pt.c.topic_id)
        self.add_standard_where_clauses(s, siteId, groupId, False)

        if searchTokens.keywords:
            q = ' & '.join(searchTokens.keywords)
            s.append_whereclause(pt.c.fts_vectors.match(q))

        session = getSession()
        r = session.execute(s)
        retval = [self.marshal_topic_info(x) for x in r]
        assert type(retval) == list
        return retval
