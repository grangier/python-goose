# -*- coding: utf-8 -*-
"""Beautiful Soup bonus library: Unicode, Dammit

This class forces XML data into a standard format (usually to UTF-8 or
Unicode).  It is heavily based on code from Mark Pilgrim's Universal
Feed Parser. It does not rewrite the XML or HTML to reflect a new
encoding; that's the tree builder's job.
"""

import codecs
from htmlentitydefs import codepoint2name
import re

# Autodetects character encodings. Very useful.
# Download from http://chardet.feedparser.org/
#  or 'apt-get install python-chardet'
#  or 'easy_install chardet'
try:
    import chardet
    #import chardet.constants
    #chardet.constants._debug = 1
except ImportError:
    chardet = None

# Available from http://cjkpython.i18n.org/.
try:
    import iconv_codec
except ImportError:
    pass


class EntitySubstitution(object):

    """Substitute XML or HTML entities for the corresponding characters."""

    def _populate_class_variables():
        lookup = {}
        reverse_lookup = {}
        characters = []
        for codepoint, name in list(codepoint2name.items()):
            if codepoint == 34:
                # There's no point in turning the quotation mark into
                # &quot;, unless it happens within an attribute value, which
                # is handled elsewhere.
                continue
            character = unichr(codepoint)
            characters.append(character)
            lookup[character] = name
            reverse_lookup[name] = character
        re_definition = "[%s]" % "".join(characters)
        return lookup, reverse_lookup, re.compile(re_definition)
    (CHARACTER_TO_HTML_ENTITY, HTML_ENTITY_TO_CHARACTER,
     CHARACTER_TO_HTML_ENTITY_RE) = _populate_class_variables()

    CHARACTER_TO_XML_ENTITY = {
        "'": "apos",
        '"': "quot",
        "&": "amp",
        "<": "lt",
        ">": "gt",
        }

    BARE_AMPERSAND_OR_BRACKET = re.compile("([<>]|"
                                           "&(?!#\d+;|#x[0-9a-fA-F]+;|\w+;)"
                                           ")")

    @classmethod
    def _substitute_html_entity(cls, matchobj):
        entity = cls.CHARACTER_TO_HTML_ENTITY.get(matchobj.group(0))
        return "&%s;" % entity

    @classmethod
    def _substitute_xml_entity(cls, matchobj):
        """Used with a regular expression to substitute the
        appropriate XML entity for an XML special character."""
        entity = cls.CHARACTER_TO_XML_ENTITY[matchobj.group(0)]
        return "&%s;" % entity

    @classmethod
    def substitute_xml(cls, value, make_quoted_attribute=False):
        """Substitute XML entities for special XML characters.

        :param value: A string to be substituted. The less-than sign will
          become &lt;, the greater-than sign will become &gt;, and any
          ampersands that are not part of an entity defition will
          become &amp;.

        :param make_quoted_attribute: If True, then the string will be
         quoted, as befits an attribute value.

         Ordinarily, the string will be quoted using double quotes.

          Bob's Bar -> "Bob's Bar"

         If the string contains double quotes, it will be quoted using
         single quotes.

          Welcome to "my bar" -> 'Welcome to "my bar"'

         If the string contains both single and double quotes, the
         double quotes will be escaped, and the string will be quoted
         using double quotes.

          Welcome to "Bob's Bar" -> "Welcome to &quot;Bob's bar&quot;
        """
        if make_quoted_attribute:
            quote_with = '"'
            if '"' in value:
                if "'" in value:
                    # The string contains both single and double
                    # quotes.  Turn the double quotes into
                    # entities. We quote the double quotes rather than
                    # the single quotes because the entity name is
                    # "&quot;" whether this is HTML or XML.  If we
                    # quoted the single quotes, we'd have to decide
                    # between &apos; and &squot;.
                    replace_with = "&quot;"
                    value = value.replace('"', replace_with)
                else:
                    # There are double quotes but no single quotes.
                    # We can use single quotes to quote the attribute.
                    quote_with = "'"

        # Escape angle brackets, and ampersands that aren't part of
        # entities.
        value = cls.BARE_AMPERSAND_OR_BRACKET.sub(
            cls._substitute_xml_entity, value)
        if make_quoted_attribute:
            return quote_with + value + quote_with
        else:
            return value

    @classmethod
    def substitute_html(cls, s):
        """Replace certain Unicode characters with named HTML entities.

        This differs from data.encode(encoding, 'xmlcharrefreplace')
        in that the goal is to make the result more readable (to those
        with ASCII displays) rather than to recover from
        errors. There's absolutely nothing wrong with a UTF-8 string
        containg a LATIN SMALL LETTER E WITH ACUTE, but replacing that
        character with "&eacute;" will make it more readable to some
        people.
        """
        return cls.CHARACTER_TO_HTML_ENTITY_RE.sub(
            cls._substitute_html_entity, s)


class UnicodeDammit:
    """A class for detecting the encoding of a *ML document and
    converting it to a Unicode string. If the source encoding is
    windows-1252, can replace MS smart quotes with their HTML or XML
    equivalents."""

    # This dictionary maps commonly seen values for "charset" in HTML
    # meta tags to the corresponding Python codec names. It only covers
    # values that aren't in Python's aliases and can't be determined
    # by the heuristics in find_codec.
    CHARSET_ALIASES = {"macintosh": "mac-roman",
                       "x-sjis": "shift-jis"}

    ENCODINGS_WITH_SMART_QUOTES = [
        "windows-1252",
        "iso-8859-1",
        "iso-8859-2",
        ]

    def __init__(self, markup, override_encodings=[],
                 smart_quotes_to=None, isHTML=False):
        self.declared_html_encoding = None
        self.markup, document_encoding, sniffed_encoding = \
                     self._detectEncoding(markup, isHTML)
        self.smart_quotes_to = smart_quotes_to
        self.tried_encodings = []
        if markup == '' or isinstance(markup, unicode):
            self.original_encoding = None
            self.unicode_markup = unicode(markup)
            return

        u = None
        for proposed_encoding in (
            override_encodings + [document_encoding, sniffed_encoding]):
            if proposed_encoding is not None:
                u = self._convert_from(proposed_encoding)
                if u:
                    break

        # If no luck and we have auto-detection library, try that:
        if not u and chardet and not isinstance(self.markup, unicode):
            u = self._convert_from(chardet.detect(self.markup)['encoding'])

        # As a last resort, try utf-8 and windows-1252:
        if not u:
            for proposed_encoding in ("utf-8", "windows-1252"):
                u = self._convert_from(proposed_encoding)
                if u:
                    break

        self.unicode_markup = u
        if not u:
            self.original_encoding = None

    def _sub_ms_char(self, match):
        """Changes a MS smart quote character to an XML or HTML
        entity."""
        orig = match.group(1)
        sub = self.MS_CHARS.get(orig)
        if type(sub) == tuple:
            if self.smart_quotes_to == 'xml':
                sub = '&#x'.encode() + sub[1].encode() + ';'.encode()
            else:
                sub = '&'.encode() + sub[0].encode() + ';'.encode()
        else:
            sub = sub.encode()
        return sub

    def _convert_from(self, proposed):
        proposed = self.find_codec(proposed)
        if not proposed or proposed in self.tried_encodings:
            return None
        self.tried_encodings.append(proposed)
        markup = self.markup

        # Convert smart quotes to HTML if coming from an encoding
        # that might have them.
        if (self.smart_quotes_to is not None
            and proposed.lower() in self.ENCODINGS_WITH_SMART_QUOTES):
            smart_quotes_re = b"([\x80-\x9f])"
            smart_quotes_compiled = re.compile(smart_quotes_re)
            markup = smart_quotes_compiled.sub(self._sub_ms_char, markup)

        try:
            u = self._to_unicode(markup, proposed)
            self.markup = u
            self.original_encoding = proposed
        except Exception as e:
            return None
        return self.markup

    def _to_unicode(self, data, encoding):
        '''Given a string and its encoding, decodes the string into Unicode.
        %encoding is a string recognized by encodings.aliases'''

        # strip Byte Order Mark (if present)
        if (len(data) >= 4) and (data[:2] == '\xfe\xff') \
               and (data[2:4] != '\x00\x00'):
            encoding = 'utf-16be'
            data = data[2:]
        elif (len(data) >= 4) and (data[:2] == '\xff\xfe') \
                 and (data[2:4] != '\x00\x00'):
            encoding = 'utf-16le'
            data = data[2:]
        elif data[:3] == '\xef\xbb\xbf':
            encoding = 'utf-8'
            data = data[3:]
        elif data[:4] == '\x00\x00\xfe\xff':
            encoding = 'utf-32be'
            data = data[4:]
        elif data[:4] == '\xff\xfe\x00\x00':
            encoding = 'utf-32le'
            data = data[4:]
        newdata = unicode(data, encoding)
        return newdata

    def _detectEncoding(self, xml_data, isHTML=False):
        """Given a document, tries to detect its XML encoding."""
        xml_encoding = sniffed_xml_encoding = None
        try:
            if xml_data[:4] == '\x4c\x6f\xa7\x94':
                # EBCDIC
                xml_data = self._ebcdic_to_ascii(xml_data)
            elif xml_data[:4] == '\x00\x3c\x00\x3f':
                # UTF-16BE
                sniffed_xml_encoding = 'utf-16be'
                xml_data = unicode(xml_data, 'utf-16be').encode('utf-8')
            elif (len(xml_data) >= 4) and (xml_data[:2] == '\xfe\xff') \
                     and (xml_data[2:4] != '\x00\x00'):
                # UTF-16BE with BOM
                sniffed_xml_encoding = 'utf-16be'
                xml_data = unicode(xml_data[2:], 'utf-16be').encode('utf-8')
            elif xml_data[:4] == '\x3c\x00\x3f\x00':
                # UTF-16LE
                sniffed_xml_encoding = 'utf-16le'
                xml_data = unicode(xml_data, 'utf-16le').encode('utf-8')
            elif (len(xml_data) >= 4) and (xml_data[:2] == '\xff\xfe') and \
                     (xml_data[2:4] != '\x00\x00'):
                # UTF-16LE with BOM
                sniffed_xml_encoding = 'utf-16le'
                xml_data = unicode(xml_data[2:], 'utf-16le').encode('utf-8')
            elif xml_data[:4] == '\x00\x00\x00\x3c':
                # UTF-32BE
                sniffed_xml_encoding = 'utf-32be'
                xml_data = unicode(xml_data, 'utf-32be').encode('utf-8')
            elif xml_data[:4] == '\x3c\x00\x00\x00':
                # UTF-32LE
                sniffed_xml_encoding = 'utf-32le'
                xml_data = unicode(xml_data, 'utf-32le').encode('utf-8')
            elif xml_data[:4] == '\x00\x00\xfe\xff':
                # UTF-32BE with BOM
                sniffed_xml_encoding = 'utf-32be'
                xml_data = unicode(xml_data[4:], 'utf-32be').encode('utf-8')
            elif xml_data[:4] == '\xff\xfe\x00\x00':
                # UTF-32LE with BOM
                sniffed_xml_encoding = 'utf-32le'
                xml_data = unicode(xml_data[4:], 'utf-32le').encode('utf-8')
            elif xml_data[:3] == '\xef\xbb\xbf':
                # UTF-8 with BOM
                sniffed_xml_encoding = 'utf-8'
                xml_data = unicode(xml_data[3:], 'utf-8').encode('utf-8')
            else:
                sniffed_xml_encoding = 'ascii'
                pass
        except:
            xml_encoding_match = None
        xml_encoding_re = '^<\?.*encoding=[\'"](.*?)[\'"].*\?>'.encode()
        xml_encoding_match = re.compile(xml_encoding_re).match(xml_data)
        if not xml_encoding_match and isHTML:
            meta_re = '<\s*meta[^>]+charset=([^>]*?)[;\'">]'.encode()
            regexp = re.compile(meta_re, re.I)
            xml_encoding_match = regexp.search(xml_data)
        if xml_encoding_match is not None:
            xml_encoding = xml_encoding_match.groups()[0].decode(
                'ascii').lower()
            if isHTML:
                self.declared_html_encoding = xml_encoding
            if sniffed_xml_encoding and \
               (xml_encoding in ('iso-10646-ucs-2', 'ucs-2', 'csunicode',
                                 'iso-10646-ucs-4', 'ucs-4', 'csucs4',
                                 'utf-16', 'utf-32', 'utf_16', 'utf_32',
                                 'utf16', 'u16')):
                xml_encoding = sniffed_xml_encoding
        return xml_data, xml_encoding, sniffed_xml_encoding

    def find_codec(self, charset):
        return self._codec(self.CHARSET_ALIASES.get(charset, charset)) \
               or (charset and self._codec(charset.replace("-", ""))) \
               or (charset and self._codec(charset.replace("-", "_"))) \
               or charset

    def _codec(self, charset):
        if not charset:
            return charset
        codec = None
        try:
            codecs.lookup(charset)
            codec = charset
        except (LookupError, ValueError):
            pass
        return codec

    EBCDIC_TO_ASCII_MAP = None

    def _ebcdic_to_ascii(self, s):
        c = self.__class__
        if not c.EBCDIC_TO_ASCII_MAP:
            emap = (0,1,2,3,156,9,134,127,151,141,142,11,12,13,14,15,
                    16,17,18,19,157,133,8,135,24,25,146,143,28,29,30,31,
                    128,129,130,131,132,10,23,27,136,137,138,139,140,5,6,7,
                    144,145,22,147,148,149,150,4,152,153,154,155,20,21,158,26,
                    32,160,161,162,163,164,165,166,167,168,91,46,60,40,43,33,
                    38,169,170,171,172,173,174,175,176,177,93,36,42,41,59,94,
                    45,47,178,179,180,181,182,183,184,185,124,44,37,95,62,63,
                    186,187,188,189,190,191,192,193,194,96,58,35,64,39,61,34,
                    195,97,98,99,100,101,102,103,104,105,196,197,198,199,200,
                    201,202,106,107,108,109,110,111,112,113,114,203,204,205,
                    206,207,208,209,126,115,116,117,118,119,120,121,122,210,
                    211,212,213,214,215,216,217,218,219,220,221,222,223,224,
                    225,226,227,228,229,230,231,123,65,66,67,68,69,70,71,72,
                    73,232,233,234,235,236,237,125,74,75,76,77,78,79,80,81,
                    82,238,239,240,241,242,243,92,159,83,84,85,86,87,88,89,
                    90,244,245,246,247,248,249,48,49,50,51,52,53,54,55,56,57,
                    250,251,252,253,254,255)
            import string
            c.EBCDIC_TO_ASCII_MAP = string.maketrans(
            ''.join(map(chr, list(range(256)))), ''.join(map(chr, emap)))
        return s.translate(c.EBCDIC_TO_ASCII_MAP)

    MS_CHARS = {b'\x80': ('euro', '20AC'),
                b'\x81': ' ',
                b'\x82': ('sbquo', '201A'),
                b'\x83': ('fnof', '192'),
                b'\x84': ('bdquo', '201E'),
                b'\x85': ('hellip', '2026'),
                b'\x86': ('dagger', '2020'),
                b'\x87': ('Dagger', '2021'),
                b'\x88': ('circ', '2C6'),
                b'\x89': ('permil', '2030'),
                b'\x8A': ('Scaron', '160'),
                b'\x8B': ('lsaquo', '2039'),
                b'\x8C': ('OElig', '152'),
                b'\x8D': '?',
                b'\x8E': ('#x17D', '17D'),
                b'\x8F': '?',
                b'\x90': '?',
                b'\x91': ('lsquo', '2018'),
                b'\x92': ('rsquo', '2019'),
                b'\x93': ('ldquo', '201C'),
                b'\x94': ('rdquo', '201D'),
                b'\x95': ('bull', '2022'),
                b'\x96': ('ndash', '2013'),
                b'\x97': ('mdash', '2014'),
                b'\x98': ('tilde', '2DC'),
                b'\x99': ('trade', '2122'),
                b'\x9a': ('scaron', '161'),
                b'\x9b': ('rsaquo', '203A'),
                b'\x9c': ('oelig', '153'),
                b'\x9d': '?',
                b'\x9e': ('#x17E', '17E'),
                b'\x9f': ('Yuml', ''),}
