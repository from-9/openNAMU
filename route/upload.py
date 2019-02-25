from .tool.func import *

def upload_2(conn):
    curs = conn.cursor()

    if ban_check() == 1:
        return re_error('/ban')
    
    if flask.request.method == 'POST':
        if captcha_post(flask.request.form.get('g-recaptcha-response', '')) == 1:
            return re_error('/error/13')
        else:
            captcha_post('', 0)

        data = flask.request.files.get('f_data', None)
        if not data:
            return re_error('/error/9')

        if int(wiki_set(3)) * 1024 * 1024 < flask.request.content_length:
            return re_error('/error/17')
        
        value = os.path.splitext(data.filename)[1]
        if not value in ['.jpeg', '.jpg', '.gif', '.png', '.webp', '.JPEG', '.JPG', '.GIF', '.PNG', '.WEBP']:
            return re_error('/error/14')
    
        if flask.request.form.get('f_name', None):
            name = flask.request.form.get('f_name', None) + value
        else:
            name = data.filename
        
        piece = os.path.splitext(name)
        if re.search('[^ㄱ-힣0-9a-zA-Z_\- ]', piece[0]):
            return re_error('/error/22')

        e_data = sha224(piece[0]) + piece[1]

        curs.execute("select title from data where title = ?", ['file:' + name])
        if curs.fetchall():
            return re_error('/error/16')
            
        ip = ip_check()

        if flask.request.form.get('f_lice', None):
            lice = flask.request.form.get('f_lice', None)
        else:
            if custom()[2] == 0:
                lice = ip
            else:
                lice = '[[user:' + ip + ']]'
            
        if os.path.exists(os.path.join(app_var['path_data_image'], e_data)):
            os.remove(os.path.join(app_var['path_data_image'], e_data))
            
            data.save(os.path.join(app_var['path_data_image'], e_data))
        else:
            data.save(os.path.join(app_var['path_data_image'], e_data))
            
        curs.execute("select title from data where title = ?", ['file:' + name])
        if curs.fetchall(): 
            curs.execute("delete from data where title = ?", ['file:' + name])
        
        curs.execute("insert into data (title, data) values (?, ?)", ['file:' + name, '[[file:' + name + ']][br][br]{{{[[file:' + name + ']]}}}[br][br]' + lice])
        curs.execute("insert into acl (title, dec, dis, why, view) values (?, 'admin', '', '', '')", ['file:' + name])

        history_plus(
            'file:' + name, '[[file:' + name + ']][br][br]{{{[[file:' + name + ']]}}}[br][br]' + lice,
            get_time(), 
            ip, 
            '(upload)',
            '0'
        )
        
        conn.commit()
        
        return redirect('/w/file:' + name)      
    else:
        return easy_minify(flask.render_template(skin_check(), 
            imp = [load_lang('upload'), wiki_set(), custom(), other2([0, 0])],
            data =  '''
                    <form method="post" enctype="multipart/form-data" accept-charset="utf8">
                        <input type="file" name="f_data">
                        <hr class=\"main_hr\">
                        <input placeholder="''' + load_lang('name') + '''" name="f_name" type="text">
                        <hr class=\"main_hr\">
                        <input placeholder="''' + load_lang('license') + '''" name="f_lice" type="text">
                        <hr class=\"main_hr\">
                        ''' + captcha_get() + '''
                        <button id="save" type="submit">''' + load_lang('save') + '''</button>
                    </form>
                    ''',
            menu = [['other', load_lang('return')]]
        ))  