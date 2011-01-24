"""
Copy a page from one wiki to another in the same MoinMoin farm.
MediaWiki 1.9.x
Ryan Lee (ryanlee@zepheira.com)

Copyright (c) 2011, Zepheira, LLC
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
 * Neither the name of Zepheira, LLC nor the names of its contributors may
   be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import os, shutil

from MoinMoin.Page import Page
from MoinMoin.PageEditor import PageEditor
from MoinMoin.action import AttachFile

from MoinMoin.web.contexts import ScriptContext
from MoinMoin import user 

COPY_TO_WIKI_URL = ''
COPY_TO_PREFIX = ''

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
            pe.saveText(u'[[%s:%s]]' % (request.cfg.interwikiname, pagename), 0, comment="Automated IntraFarmCopy pointing to original page")
        except pe.Unchanged:
            return action_error(u'Could not save initial page')
	except pe.AccessDenied:
            return action_error(u'Could not acquire credentials')
        # make next revision content of this page
        try:
            pe.saveText(Page(request, pagename).get_raw_body(), 0, comment="Automated IntraFarmCopy importing contents from original page at [[%s:%s]]" % (request.cfg.interwikiname, pagename))
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
