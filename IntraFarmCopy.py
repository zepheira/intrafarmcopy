import os, shutil

from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from MoinMoin.action import AttachFile

from MoinMoin.web.contexts import ScriptContext
from MoinMoin import user 

COPY_TO_WIKI_URL = 'http://community.zepheira.com/wiki/team/'
COPY_TO_PREFIX = 'Archive/'

def execute(pagename, request):
    """                                                                         
    Handle action=IntraFarmCopy
    """

    if not request.user.may.read(pagename):
        Page(request, pagename).send_page()
        return

    # Which local farm wiki - assume team for now                               
    to_wiki_url = COPY_TO_WIKI_URL 
    # New page name                                               
    to_wiki_pagename = '%s%s' % (COPY_TO_PREFIX, pagename)

    # create page at local wiki if it doesn't exist                             
    to_request = ScriptContext(to_wiki_url)
    # login this user remotely
    to_uid = user.getUserId(to_request, request.user.name)
    to_user = user.User(to_request, id=to_uid, name=request.user.name, password=request.user.password, auth_method="moin")
    to_request.user = to_user

    try:
        page = Page(to_request, to_wiki_pagename)
    except:
        return action_error(u'Error accessing destination page')
    if not page.exists():
        pe = PageEditor(to_request, to_wiki_pagename)
        # make initial revision pointer to original                             
        try:
            pe.saveText(u'[[%s:%s]]' % (request.cfg.interwikiname, pagename), 0, comment="Automated InterWikiPort pointing to original page")
        except pe.Unchanged:
            return action_error(u'Could not save initial page')
	except pe.AccessDenied:
            return action_error(u'Could not acquire credentials')
        # make next revision content of this page
        try:
            pe.saveText(Page(request, pagename).get_raw_body(), 0, comment="Automated InterWikiPort importing contents from original page at [[%s:%s]]" % (request.cfg.interwikiname, pagename))
        except pe.Unchanged:
            return action_error(u'Could not save destination page text')
	# send attachments over
        attachments = AttachFile._get_files(request, pagename)
	for attachname in attachments:
	    filename = AttachFile.getFilename(request, pagename, attachname)
	    if not os.path.isfile(filename):
	        continue
	    to_filename = AttachFile.getFilename(to_request, to_wiki_pagename, attachname)
	    shutil.copyfile(filename, to_filename)
	    AttachFile._addLogEntry(to_request, 'ATTNEW', to_wiki_pagename, attachname) 
        # redirect user to view new page in other wiki                          
        request.http_redirect('%s%s' % (to_wiki_url, to_wiki_pagename))
	return
    else:
	return action_error(u'Destination page already exists!')

def action_error(msg):
    request.theme.add_msg(msg, "error")
    return Page(request, pagename).send_page()
