# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal


class DjangoUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj, *args):
        self.obj = obj
        UnicodeDecodeError.__init__(self, *args)

    def __str__(self):
        original = UnicodeDecodeError.__str__(self)
        return '%s. You passed in %r (%s)' % (original, self.obj,
                type(self.obj))


class StrAndUnicode(object):
    """
    A class whose __str__ returns its __unicode__ as a UTF-8 bytestring.

    Useful as a mix-in.
    """
    def __str__(self):
        return self.__unicode__()


def smart_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a str object representing 's'. Treats bytestrings using the
    'encoding' codec.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    return force_unicode(s, encoding, strings_only, errors)


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    force_unicode(strings_only=True).
    """
    return isinstance(obj, (
        type(None),
        int,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal)
    )


def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_unicode, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, str):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if isinstance(s, bytes):
            s = s.decode(encoding, errors)
        elif not isinstance(s, str):
            if hasattr(s, '__unicode__'):
                s = str(s.__unicode__())
            else:
                s = str(s)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise DjangoUnicodeDecodeError(s, *e.args)
        else:
            s = ' '.join([force_unicode(arg, encoding, strings_only,
                    errors) for arg in s])
    return s


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (type(None), int)):
        return s
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if not isinstance(s, str):
        try:
            return str(s).encode(encoding, errors)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                return b' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return str(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)
