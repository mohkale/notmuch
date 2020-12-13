#!/bin/sh

FILE_EXCLUDE='corpora'
AUTHOR_EXCLUDE='uncrustify'
# based on the FSF guideline, for want of a better idea.
THRESHOLD=15

git ls-files | grep -v -e "$FILE_EXCLUDE" | xargs -n 1 -d \\n \
                                                  git blame -w --line-porcelain -- | \
    sed -n "/$AUTHOR_EXCLUDE/d; s/^[aA][uU][tT][hH][Oo][rR] //p" | \
    sort -fd | uniq -ic | awk "\$1 >= $THRESHOLD" | sort -nr
