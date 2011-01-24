IntraFarmCopy MoinMoin Action Plugin
====================================

Copy a page from one wiki in a MoinMoin farm to another.  Install
as an action plugin as described in http://moinmo.in/ActionMarket
You must have

 * MoinMoin 1.9.x

The plugin can copy from any wiki but can only copy to one, which
is a configurable option.  Attachments will also be copied over.


License
-------

IntraFarmCopy is released under the modified BSD license.  See
IntraFarmCopy.py for the full license text.


Configuration
-------------

The plugin must be configured before use; one setting is required.

 * COPY_TO_WIKI_URL: set to the URL of the destination wiki
 * COPY_TO_PREFIX: to prefix copied page titles with a name or directory


Caveats
-------

The plugin assumes the logged-in user's credentials for the originating
wiki are also valid for the destination wiki.

It also assumes that being in the same farm means being on the same
hardware and an operating system-level copy can move attachments.