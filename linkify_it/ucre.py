from uc_micro.categories import Cc, Cf, P, Z
from uc_micro.properties import Any

SRC_ANY = Any.REGEX
SRC_CC = Cc.REGEX
SRC_CF = Cf.REGEX
SRC_P = P.REGEX
SRC_Z = Z.REGEX

# \p{\Z\P\Cc\CF} (white spaces + control + format + punctuation)
SRC_ZPCC = "|".join([SRC_Z, SRC_P, SRC_CC])

# \p{\Z\Cc} (white spaces + control)
SRC_ZCC = "|".join([SRC_Z, SRC_CC])

# Experimental. List of chars, completely prohibited in links
# because can separate it from other part of text
TEXT_SEPARATORS = "[><\uff5c]"

# All possible word characters (everything without punctuation, spaces & controls)
# Defined via punctuation & spaces to save space
# Should be something like \p{\L\N\S\M} (\w but without `_`)
SRC_PSEUDO_LETTER = "(?:(?!" + TEXT_SEPARATORS + "|" + SRC_ZPCC + ")" + SRC_ANY + ")"
# The same as abothe but without [0-9]
# var SRC_PSEUDO_LETTER_non_d = '(?:(?![0-9]|' + SRC_ZPCC + ')' + SRC_ANY + ')'

# =============================================================================

SRC_IP4 = (
    "(?:(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|"
    + "2[0-4][0-9]|[01]?[0-9][0-9]?)"
)

# Prohibit any of "@/[]()" in user/pass to avoid wrong domain fetch.
SRC_AUTH = "(?:(?:(?!" + SRC_ZCC + "|[@/\\[\\]()]).)+@)?"

SRC_PORT = (
    "(?::(?:6(?:[0-4]\\d{3}|5(?:[0-4]\\d{2}|5(?:[0-2]\\d|3[0-5])))|[1-5]?\\d{1,4}))?"
)

SRC_HOST_TERMINATOR = (
    "(?=$|"
    + TEXT_SEPARATORS
    + "|"
    + SRC_ZPCC
    + ")(?!-|_|:\\d|\\.-|\\.(?!$|"
    + SRC_ZPCC
    + "))"
)


# Allow anything in markdown spec, forbid quote (") at the first position
# because emails enclosed in quotes are far more common
SRC_EMAIL_NAME = '[\\-:&=\\+\\$,\\.a-zA-Z0-9_][\\-:&=\\+\\$,\\"\\.a-zA-Z0-9_]*'

SRC_XN = "xn--[a-z0-9\\-]{1,59}"

# More to read about domain names
# http:#serverfault.com/questions/638260/

# Allow letters & digits (http:#test1)
SRC_DOMAIN_ROOT = "(?:" + SRC_XN + "|" + SRC_PSEUDO_LETTER + "{1,63}" + ")"

SRC_DOMAIN = (
    "(?:"
    + SRC_XN
    + "|"
    + "(?:"
    + SRC_PSEUDO_LETTER
    + ")"
    + "|"
    + "(?:"
    + SRC_PSEUDO_LETTER
    + "(?:-|"
    + SRC_PSEUDO_LETTER
    + "){0,61}"
    + SRC_PSEUDO_LETTER
    + ")"
    + ")"
)

SRC_HOST = (
    "(?:"
    +
    # Don't need IP check, because digits are already allowed in normal domain names
    # SRC_IP4 +
    # '|' +
    "(?:(?:(?:"
    + SRC_DOMAIN
    + ")\\.)*"
    + SRC_DOMAIN  # _root
    + ")"
    + ")"
)

TPL_HOST_FUZZY = (
    "(?:" + SRC_IP4 + "|" + "(?:(?:(?:" + SRC_DOMAIN + ")\\.)+(?:%TLDS%))" + ")"
)

TPL_HOST_NO_IP_FUZZY = "(?:(?:(?:" + SRC_DOMAIN + ")\\.)+(?:%TLDS%))"

SRC_HOST_STRICT = SRC_HOST + SRC_HOST_TERMINATOR

TPL_HOST_FUZZY_STRICT = TPL_HOST_FUZZY + SRC_HOST_TERMINATOR

SRC_HOST_PORT_STRICT = SRC_HOST + SRC_PORT + SRC_HOST_TERMINATOR

TPL_HOST_PORT_FUZZY_STRICT = TPL_HOST_FUZZY + SRC_PORT + SRC_HOST_TERMINATOR

TPL_HOST_PORT_NO_IP_FUZZY_STRICT = TPL_HOST_NO_IP_FUZZY + SRC_PORT + SRC_HOST_TERMINATOR

# =============================================================================

# Rude test fuzzy links by host, for quick deny
TPL_HOST_FUZZY_TEST = (
    "localhost|www\\.|\\.\\d{1,3}\\.|(?:\\.(?:%TLDS%)(?:" + SRC_ZPCC + "|>|$))"
)

TPL_EMAIL_FUZZY = (
    "(^|"
    + TEXT_SEPARATORS
    + '|"|\\(|'
    + SRC_ZCC
    + ")"
    + "("
    + SRC_EMAIL_NAME
    + "@"
    + TPL_HOST_FUZZY_STRICT
    + ")"
)


def re_src_path(opts):
    try:
        _ = opts["---"]
    # KeyError: Not found key:"---"
    # TypeError: opts is None
    except (KeyError, TypeError):
        long_dash_flag = False
    else:
        long_dash_flag = True

    if long_dash_flag:
        options = "\\-(?!--(?:[^-]|$))(?:-*)|"  # `---` => long dash, terminate
    else:
        options = "\\-+|"

    src_path = (
        "(?:"
        + "[/?#]"
        + "(?:"
        + "(?!"
        + SRC_ZCC
        + "|"
        + TEXT_SEPARATORS
        + "|[()[\\]{}.,\"'?!\\-]).|"
        + "\\[(?:(?!"
        + SRC_ZCC
        + "|\\]).)*\\]|"
        + "\\((?:(?!"
        + SRC_ZCC
        + "|[)]).)*\\)|"
        + "\\{(?:(?!"
        + SRC_ZCC
        + "|[}]).)*\\}|"
        + '\\"(?:(?!'
        + SRC_ZCC
        + '|["]).)+\\"|'
        + "\\'(?:(?!"
        + SRC_ZCC
        + "|[']).)+\\'|"
        + "\\'(?="
        + SRC_PSEUDO_LETTER
        + "|[-]).|"
        + "\\.{2,}[a-zA-Z0-9%/&]|"
        # google has many dots in "google search" links (#66, #81).
        # github has ... in commit range links,
        # ReSTRICT to
        # - english
        # - percent-encoded
        # - parts of file path
        # - params separator
        # until more examples found.
        + "\\.(?!"
        + SRC_ZCC
        + "|[.]).|"
        + options
        + "\\,(?!"
        + SRC_ZCC
        + ").|"  # allow `,,,` in paths
        + "\\!+(?!"
        + SRC_ZCC
        + "|[!]).|"  # allow `!!!` in paths, but not at the end
        + "\\?(?!"
        + SRC_ZCC
        + "|[?])."
        + ")+"
        + "|\\/"
        + ")?"
    )

    return src_path


def build_re(opts):
    regex = {
        "src_Any": SRC_ANY,
        "src_Cc": SRC_CC,
        "src_Cf": SRC_CF,
        "src_Z": SRC_Z,
        "src_P": SRC_P,
        "src_ZPCc": SRC_ZPCC,
        "src_ZCc": SRC_ZCC,
        "src_pseudo_letter": SRC_PSEUDO_LETTER,
        "src_ip4": SRC_IP4,
        "src_auth": SRC_AUTH,
        "src_port": SRC_PORT,
        "src_host_terminator": SRC_HOST_TERMINATOR,
        "src_path": re_src_path(opts),
        "src_email_name": SRC_EMAIL_NAME,
        "src_xn": SRC_XN,
        "src_domain_root": SRC_DOMAIN_ROOT,
        "src_domain": SRC_DOMAIN,
        "src_host": SRC_HOST,
        "tpl_host_fuzzy": TPL_HOST_FUZZY,
        "tpl_host_no_ip_fuzzy": TPL_HOST_NO_IP_FUZZY,
        "src_host_strict": SRC_HOST_STRICT,
        "tpl_host_fuzzy_strict": TPL_HOST_FUZZY_STRICT,
        "src_host_port_strict": SRC_HOST_PORT_STRICT,
        "tpl_host_port_fuzzy_strict": TPL_HOST_PORT_FUZZY_STRICT,
        "tpl_host_port_no_ip_fuzzy_strict": TPL_HOST_PORT_FUZZY_STRICT,
        # Main rules
        "tpl_host_fuzzy_test": TPL_HOST_FUZZY_TEST,
        "tpl_email_fuzzy": TPL_EMAIL_FUZZY,
        # Fuzzy link can't be prepended with .:/\- and non punctuation.
        # but can start with > (markdown blockquote)
        "tpl_link_fuzzy": (
            "(^|(?![.:/\\-_@])(?:[$+<=>^`|\uff5c]|"
            + SRC_ZPCC
            + "))"
            + "((?![$+<=>^`|\uff5c])"
            + TPL_HOST_PORT_FUZZY_STRICT
            + re_src_path(opts)
            + ")"
        ),
        # Fuzzy link can't be prepended with .:/\- and non punctuation.
        # but can start with > (markdown blockquote)
        "tpl_link_no_ip_fuzzy": (
            "(^|(?![.:/\\-_@])(?:[$+<=>^`|\uff5c]|"
            + SRC_ZPCC
            + "))"
            + "((?![$+<=>^`|\uff5c])"
            + TPL_HOST_PORT_NO_IP_FUZZY_STRICT
            + re_src_path(opts)
            + ")"
        ),
    }

    return regex
