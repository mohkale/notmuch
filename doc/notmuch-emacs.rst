.. _notmuch-emacs:

==========================
Emacs Frontend for Notmuch
==========================

About this Manual
=================

This manual covers only the Emacs interface to Notmuch. For information
on the command line interface, see section “Description” in the Notmuch
Manual Pages. To save typing, we will sometimes use *notmuch* in this
manual to refer to the Emacs interface to Notmuch. When this distinction
is important, we’ll refer to the Emacs interface as
*notmuch-emacs*.

Notmuch-emacs is highly customizable via the the Emacs customization
framework (or just by setting the appropriate variables). We try to
point out relevant variables in this manual, but in order to avoid
duplication of information, you can usually find the most detailed
description in the variables' docstring.

notmuch-hello
=============

.. index::
   single: notmuch-hello
   single: notmuch

``notmuch-hello`` is the main entry point for Notmuch. You can start it
with ``M-x notmuch`` or ``M-x notmuch-hello``. The startup screen looks
something like the following. There are some hints at the bottom of the
screen. There are three main parts to the notmuch-hello screen,
discussed below. The **bold** text indicates buttons you can click with
a mouse or by positioning the cursor and pressing ``<return>``

|   Welcome to **notmuch** You have 52 messages.
|
| Saved searches: **[edit]**
|
|	  52 **inbox**           52 **unread**
|
| Search: ____________________________________
|
| All tags: **[show]**
|
|	 Hit \`?' for context-sensitive help in any Notmuch screen.
|		      Customize Notmuch or this page.

You can change the overall appearance of the notmuch-hello screen by
customizing the variables

.. emacsvar:: notmuch-hello-sections

       |docstring::notmuch-hello-sections|

.. emacsvar:: notmuch-hello-thousands-separator

       |docstring::notmuch-hello-thousands-separator|

.. emacsvar:: notmuch-show-logo

       |docstring::notmuch-show-logo|

.. emacsvar:: notmuch-column-control

    Controls the number of columns for saved searches/tags in notmuch view.

    This variable has three potential types of values:

    .. describe:: t

       Automatically calculate the number of columns possible based
       on the tags to be shown and the window width.

    .. describe:: integer <n>

       A lower bound on the number of characters that will
       be used to display each column.

    .. describe:: float <f>

       A fraction of the window width that is the lower bound on the
       number of characters that should be used for each column.

    So:

    - if you would like two columns of tags, set this to 0.5.

    - if you would like a single column of tags, set this to 1.0.

    - if you would like tags to be 30 characters wide, set this to 30.

    - if you don't want to worry about all of this nonsense, leave
      this set to `t`.

.. emacsvar:: notmuch-show-empty-saved-searches

   |docstring::notmuch-show-empty-saved-searches|

notmuch-hello key bindings
--------------------------

``<tab>``
    Move to the next widget (button or text entry field)

``<backtab>``
    Move to the previous widget.

``<return>``
    Activate the current widget.

``g`` ``=``
    Refresh the buffer; mainly update the counts of messages for various
    saved searches.

``G``
    Import mail, See :ref:`importing`

``m``
    Compose a message

``s``
    Search the notmuch database using :ref:`notmuch-search`

``v``
    Print notmuch version

``q``
    Quit

.. _saved-searches:

Saved Searches
--------------

Since notmuch is entirely search-based, it's often useful to organize
mail around common searches.  To facilitate this, the first section of
notmuch-hello presents a customizable set of saved searches.  Saved
searches can also be accessed from anywhere in notmuch by pressing
``j`` to access :ref:`notmuch-jump`.

The saved searches default to various common searches such as
``tag:inbox`` to access the inbox and ``tag:unread`` to access all
unread mail, but there are several options for customization:

.. emacsvar:: notmuch-saved-searches

    The list of saved searches, including names, queries, and
    additional per-query options.

.. emacsvar:: notmuch-saved-search-sort-function

    This variable controls how saved searches should be sorted. A value
    of ``nil`` displays the saved searches in the order they are stored
    in ‘notmuch-saved-searches’.

Search Box
----------

The search box lets the user enter a Notmuch query. See section
“Description” in Notmuch Query Syntax, for more info on Notmuch query
syntax. A history of recent searches is also displayed by default. The
latter is controlled by the variable `notmuch-hello-recent-searches-max`.

.. emacsvar:: notmuch-hello-recent-searches-max

              |docstring::notmuch-hello-recent-searches-max|

Known Tags
----------

One special kind of saved search provided by default is for each
individual tag defined in the database. This can be controlled via the
following variables.

.. emacsvar:: notmuch-hello-tag-list-make-query

    Control how to construct a search (“virtual folder”) from a given
    tag.

.. emacsvar:: notmuch-hello-hide-tags

    Which tags not to display at all.

.. _notmuch-search:

notmuch-search
==============

``notmuch-search-mode`` is used to display the results from executing
a query via ``notmuch-search``. The syntax for these queries is the
the same as :ref:`saved-searches`. For details of this syntax see
info:notmuch-search-terms

By default the output approximates that of the command line See section
“Description” in notmuch search command.

The main purpose of the ``notmuch-search-mode`` buffer is to act as a
menu of results that the user can explore further by pressing
``<return>`` on the appropriate line.

``n,C-n,<down>``
    Move to next line

``p,C-p,<up>``
    Move to previous line

``<return>``
    Open thread on current line in :ref:`notmuch-show` mode

``g`` ``=``
    Refresh the buffer

``?``
    Display full set of key bindings

The presentation of results can be controlled by the following
variables.

.. emacsvar:: notmuch-search-result-format

    Control how each thread of messages is presented in the
    ``notmuch-show-mode`` buffer

.. emacsvar:: notmuch-search-oldest-first

    Display the oldest threads at the top of the buffer

It is also possible to customize how the name of buffers containing
search results is formatted using the following variables:

.. emacsvar:: notmuch-search-buffer-name-format

       |docstring::notmuch-search-buffer-name-format|

.. emacsvar:: notmuch-saved-search-buffer-name-format

       |docstring::notmuch-saved-search-buffer-name-format|


.. _notmuch-show:

notmuch-show
============

``notmuch-show-mode`` is used to display a single thread of email from
your email archives.

By default, various components of email messages, (citations,
signatures, already-read messages), are hidden. You can make
these parts visible by clicking with the mouse button or by
pressing RET after positioning the cursor on a hidden part.

``<space>``
    Scroll the current message (if necessary),
    advance to the next message, or advance to the next thread (if
    already on the last message of a thread).

``c``
    :ref:`show-copy`

``N``
    Move to next message

``P``
    Move to previous message (or start of current message)

``n``
    Move to next matching message

``p``
    Move to previous matching message

``+,-``
    Add or remove arbitrary tags from the current message.

``!``
    |docstring::notmuch-show-toggle-elide-non-matching|

``?``
    Display full set of key bindings

Display of messages can be controlled by the following variables; see also :ref:`show-large`.

.. emacsvar:: notmuch-message-headers

       |docstring::notmuch-message-headers|

.. emacsvar:: notmuch-message-headers-visible

       |docstring::notmuch-message-headers-visible|

.. emacsvar:: notmuch-show-header-line

       |docstring::notmuch-show-header-line|

.. emacsvar:: notmuch-multipart/alternative-discouraged

   Which mime types to hide by default for multipart messages.

   Can either be a list of mime types (as strings) or a function
   mapping a plist representing the current message to such a list.
   The following example function would discourage `text/html` and
   `multipart/related` generally, but discourage `text/plain` should
   the message be sent from `whatever@example.com`.

   .. code:: lisp

      (defun my--determine-discouraged (msg)
        (let* ((headers (plist-get msg :headers))
               (from (or (plist-get headers :From) "")))
          (cond
           ((string-match "whatever@example.com" from)
            (list "text/plain"))
           (t
            (list "text/html" "multipart/related")))))

.. _show-large:

Dealing with large messages and threads
---------------------------------------

If you are finding :ref:`notmuch-show` is annoyingly slow displaying
large messages, you can customize
:emacsvar:`notmuch-show-max-text-part-size`.  If you want to speed up the
display of large threads (with or without large messages), there are
several options.  First, you can display the same query in one of the
other modes. :ref:`notmuch-unthreaded` is the most robust for
extremely large queries, but :ref:`notmuch-tree` is also be faster
than :ref:`notmuch-show` in general, since it only renders a single
message a time. If you prefer to stay with the rendered thread
("conversation") view of :ref:`notmuch-show`, you can customize the
variables :emacsvar:`notmuch-show-depth-limit`,
:emacsvar:`notmuch-show-height-limit` and
:emacsvar:`notmuch-show-max-text-part-size` to limit the amount of
rendering done initially. Note that these limits are implicitly
*OR*-ed together, and combinations might have surprising effects.

.. emacsvar:: notmuch-show-depth-limit

       |docstring::notmuch-show-depth-limit|

.. emacsvar:: notmuch-show-height-limit

       |docstring::notmuch-show-height-limit|

.. emacsvar:: notmuch-show-max-text-part-size

       |docstring::notmuch-show-max-text-part-size|

.. _show-copy:

Copy to kill-ring
-----------------

You can use the usually Emacs ways of copying text to the kill-ring,
but notmuch also provides some shortcuts. These keys are available in
:ref:`notmuch-show`, and :ref:`notmuch-tree`. A subset are available
in :ref:`notmuch-search`.

``c F``	``notmuch-show-stash-filename``
   |docstring::notmuch-show-stash-filename|

``c G`` ``notmuch-show-stash-git-send-email``
   |docstring::notmuch-show-stash-git-send-email|

``c I`` ``notmuch-show-stash-message-id-stripped``
   |docstring::notmuch-show-stash-message-id-stripped|

``c L`` ``notmuch-show-stash-mlarchive-link-and-go``
   |docstring::notmuch-show-stash-mlarchive-link-and-go|

``c T`` ``notmuch-show-stash-tags``
   |docstring::notmuch-show-stash-tags|

``c c`` ``notmuch-show-stash-cc``
   |docstring::notmuch-show-stash-cc|

``c d`` ``notmuch-show-stash-date``
   |docstring::notmuch-show-stash-date|

``c f`` ``notmuch-show-stash-from``
   |docstring::notmuch-show-stash-from|

``c i`` ``notmuch-show-stash-message-id``
   |docstring::notmuch-show-stash-message-id|

``c l`` ``notmuch-show-stash-mlarchive-link``
   |docstring::notmuch-show-stash-mlarchive-link|

``c s`` ``notmuch-show-stash-subject``
   |docstring::notmuch-show-stash-subject|

``c t`` ``notmuch-show-stash-to``
   |docstring::notmuch-show-stash-to|

``c ?``
    Show all available copying commands

.. _notmuch-tree:

notmuch-tree
============

``notmuch-tree-mode`` displays the results of a "notmuch tree" of your
email archives. Each line in the buffer represents a single
message giving the relative date, the author, subject, and any
tags.

``c``
    :ref:`show-copy`

``<return>``
   Displays that message.

``N``
    Move to next message

``P``
    Move to previous message

``n``
    Move to next matching message

``p``
    Move to previous matching message

``o`` ``notmuch-tree-toggle-order``
   |docstring::notmuch-tree-toggle-order|

``l`` ``notmuch-tree-filter``
   Filter or LIMIT the current search results based on an additional query string

``t`` ``notmuch-tree-filter-by-tag``
   Filter the current search results based on an additional tag


``g`` ``=``
    Refresh the buffer

``?``
    Display full set of key bindings

As is the case with :ref:`notmuch-search`, the presentation of results
can be controlled by the variable ``notmuch-search-oldest-first``.

.. _notmuch-unthreaded:

notmuch-unthreaded
------------------

``notmuch-unthreaded-mode`` is similar to :any:`notmuch-tree` in that
each line corresponds to a single message, but no thread information
is presented.

Keybindings are the same as :any:`notmuch-tree`.

Global key bindings
===================

Several features are accessible from most places in notmuch through the
following key bindings:

``j``
    Jump to saved searches using :ref:`notmuch-jump`.

``k``
    Tagging operations using :ref:`notmuch-tag-jump`

``C-_`` ``C-/`` ``C-x u``: Undo previous tagging operation using :ref:`notmuch-tag-undo`

.. _notmuch-jump:

notmuch-jump
------------

Saved searches configured through :ref:`saved-searches` can
include a "shortcut key" that's accessible through notmuch-jump.
Pressing ``j`` anywhere in notmuch followed by the configured shortcut
key of a saved search will immediately jump to that saved search.  For
example, in the default configuration ``j i`` jumps immediately to the
inbox search.  When you press ``j``, notmuch-jump shows the saved
searches and their shortcut keys in the mini-buffer.

.. _notmuch-tag-jump:

notmuch-tag-jump
----------------

Tagging operations configured through ``notmuch-tagging-keys`` can
be accessed via :kbd:`k` in :ref:`notmuch-show`,
:ref:`notmuch-search` and :ref:`notmuch-tree`.  With a
prefix (:kbd:`C-u k`), notmuch displays a menu of the reverses of the
operations specified in ``notmuch-tagging-keys``; i.e. each
``+tag`` is replaced by ``-tag`` and vice versa.

.. emacsvar:: notmuch-tagging-keys

  |docstring::notmuch-tagging-keys|

.. _notmuch-tag-undo:

notmuch-tag-undo
----------------

Each notmuch buffer supporting tagging operations (i.e buffers in
:any:`notmuch-show`, :any:`notmuch-search`, :any:`notmuch-tree`, and
:any:`notmuch-unthreaded` mode) keeps a local stack of tagging
operations. These can be undone via :emacscmd:`notmuch-tag-undo`. By default
this is bound to the usual Emacs keys for undo.

.. emacscmd:: notmuch-tag-undo

   |docstring::notmuch-tag-undo|

Buffer navigation
=================

.. emacscmd:: notmuch-cycle-notmuch-buffers

   |docstring::notmuch-cycle-notmuch-buffers|

Configuration
=============

.. _importing:

Importing Mail
--------------

.. emacscmd:: notmuch-poll

   |docstring::notmuch-poll|

.. emacsvar:: notmuch-poll-script

   |docstring::notmuch-poll-script|

Sending Mail
------------

.. emacsvar:: mail-user-agent

       Emacs consults the variable :code:`mail-user-agent` to choose a mail
       sending package for commands like :code:`report-emacs-bug` and
       :code:`compose-mail`.  To use ``notmuch`` for this, customize this
       variable to the symbol :code:`notmuch-user-agent`.

.. emacsvar:: message-dont-reply-to-names

       When composing mail replies, Emacs's message mode uses the
       variable :code:`message-dont-reply-to-names` to exclude
       recipients matching a given collection of regular expressions
       or satisfying an arbitrary predicate.  Notmuch's MUA inherits
       this standard mechanism and will honour your customization of
       this variable.

Init File
---------

When Notmuch is loaded, it will read the ``notmuch-init-file``
(``~/.emacs.d/notmuch-config`` by default) file. This is normal Emacs Lisp
file and can be used to avoid cluttering your ``~/.emacs`` with Notmuch
stuff. If the file with ``.elc``, ``.elc.gz``, ``.el`` or ``.el.gz``
suffix exist it will be read instead (just one of these, chosen in this
order). Most often users create ``~/.emacs.d/notmuch-config.el`` and just
work with it. If Emacs was invoked with the ``-q`` or ``--no-init-file``
options, ``notmuch-init-file`` is not read.
