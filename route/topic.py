from .tool.func import *

def topic_2(conn, topic_num):
    curs = conn.cursor()

    admin = admin_check(3)
    topic_num = str(topic_num)

    if flask.request.method == 'POST':
        name = flask.request.form.get('topic', 'test')
        sub = flask.request.form.get('title', 'test')
    else:
        curs.execute(db_change("select title, sub from rd where code = ?"), [topic_num])
        name = curs.fetchall()
        if name:
            sub = name[0][1]
            name = name[0][0]
        else:
            return redirect('/')

    ban = acl_check(name, 'topic', topic_num)

    if flask.request.method == 'POST':
        if captcha_post(flask.request.form.get('g-recaptcha-response', '')) == 1:
            return re_error('/error/13')
        else:
            captcha_post('', 0)

        ip = ip_check()
        today = get_time()

        if ban == 1:
            return re_error('/ban')

        curs.execute(db_change("select id from topic where code = ? order by id + 0 desc limit 1"), [topic_num])
        old_num = curs.fetchall()
        if old_num:
            num = int(old_num[0][0]) + 1
        else:
            num = 1

        num = str(num)

        match = re.search('^user:([^/]+)', name)
        if match:
            y_check = 0
            if ip_or_user(match.groups()[0]) == 1:
                curs.execute(db_change("select ip from history where ip = ? limit 1"), [match.groups()[0]])
                u_data = curs.fetchall()
                if u_data:
                    y_check = 1
                else:
                    curs.execute(db_change("select ip from topic where ip = ? limit 1"), [match.groups()[0]])
                    u_data = curs.fetchall()
                    if u_data:
                        y_check = 1
            else:
                curs.execute(db_change("select id from user where id = ?"), [match.groups()[0]])
                u_data = curs.fetchall()
                if u_data:
                    y_check = 1

            if y_check == 1:
                curs.execute(db_change('insert into alarm (name, data, date) values (?, ?, ?)'), [
                    match.groups()[0],
                    ip + ' | <a href="/thread/' + topic_num + '#' + num + '">' + name + ' | ' + sub + ' | #' + num + '</a>',
                    today
                ])

        cate_re = re.compile('\[\[((?:분류|category):(?:(?:(?!\]\]).)*))\]\]', re.I)
        data = cate_re.sub('[br]', flask.request.form.get('content', 'Test'))

        for rd_data in re.findall("(?:#([0-9]+))", data):
            curs.execute(db_change("select ip from topic where code = ? and id = ?"), [topic_num, rd_data])
            ip_data = curs.fetchall()
            if ip_data and ip_or_user(ip_data[0][0]) == 0:
                curs.execute(db_change('insert into alarm (name, data, date) values (?, ?, ?)'), [
                    ip_data[0][0],
                    ip + ' | <a href="/thread/' + topic_num + '#' + num + '">' + name + ' | ' + sub + ' | #' + num + '</a>',
                    today
                ])

        data = re.sub("(?P<in>#(?:[0-9]+))", '[[\g<in>]]', data)
        data = savemark(data)

        rd_plus(topic_num, today, name, sub)
        curs.execute(db_change("insert into topic (id, data, date, ip, code) values (?, ?, ?, ?, ?)"), [
            num,
            data,
            today,
            ip,
            topic_num
        ])
        conn.commit()

        return redirect('/thread/' + topic_num + '?where=bottom')
    else:
        data = ''

        if ban == 1:
            display = 'display: none;'
        else:
            display = ''

        data += '''
            <div id="top_topic"></div>
            <div id="main_topic"></div>
            <div id="plus_topic"></div>
            <script>topic_top_load("''' + topic_num + '''");</script>
            <a href="/thread/''' + topic_num + '/tool">(' + load_lang('topic_tool') + ''')</a>
            <hr class=\"main_hr\">
            <form style="''' + display + '''" method="post">
                <textarea rows="10" id="content" placeholder="''' + load_lang('content') + '''" name="content"></textarea>
                <hr class=\"main_hr\">
                ''' + captcha_get() + (ip_warring() if display == '' else '') + '''
                <input style="display: none;" name="topic" value="''' + name + '''">
                <input style="display: none;" name="title" value="''' + sub + '''">
                <button type="submit">''' + load_lang('send') + '''</button>
                <button id="preview" type="button" onclick="load_preview(\'\')">''' + load_lang('preview') + '''</button>
            </form>
            <hr class=\"main_hr\">
            <div id="see_preview"></div>
        '''

        return easy_minify(flask.render_template(skin_check(),
            imp = [name, wiki_set(), custom(), other2([' (' + load_lang('discussion') + ')', 0])],
            data = '''
                <h2 id="topic_top_title">''' + sub + '''</h2>
                ''' + data,
            menu = [['topic/' + url_pas(name), load_lang('list')]]
        ))