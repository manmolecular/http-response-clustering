#!/usr/bin/env python3
from typing import List

from cluster.configurations.default_values import DefaultPlates, TrashHeaders


class HttpParser:
    def __init__(
        self,
        process_cookie: bool = False,
        process_trash_headers: bool = False,
        remove_digits: bool = False,
        remove_special: bool = False,
    ):
        self.process_cookie = process_cookie
        self.process_trash_headers = process_trash_headers
        self.remove_digits = remove_digits
        self.remove_special = remove_special

    @staticmethod
    def _check_if_trash_header(
        raw_header: str, trash_headers: List[str] = None
    ) -> bool:
        """
        Check if current header is a trash header (we need to remove it)
        @param raw_header: header to check
        @param trash_headers: list of trash headers to compare with
        @return: answer to question - is the current header trash or not?
        """
        if not trash_headers:
            trash_headers = TrashHeaders.HEADERS
        for trash_header in trash_headers:
            if f"{trash_header.lower()}:" in raw_header.lower():
                return True
        return False

    @staticmethod
    def _remove_special_chars_from_word(raw_word: str, separator: str = " ") -> str:
        """
        Remove some special chars from words
        @param raw_word: raw word to remove chars from
        @param separator: word string separator
        @return: cleaned-up line
        """
        if raw_word.startswith(DefaultPlates.RANDOM_REPLACER):
            separator = ""
        string_wo_special = ""
        for char in raw_word:
            if char.isalnum():
                string_wo_special += char
            else:
                string_wo_special += separator
        return string_wo_special

    @staticmethod
    def _remove_special_chars_from_line(raw_line: str) -> str:
        """
        Remove some special chars from lines
        @param raw_line: raw line to remove chars from
        @return: cleaned-up line
        """
        raw_words = raw_line.split()
        for index, word in enumerate(raw_words):
            raw_words[index] = HttpParser._remove_special_chars_from_word(word)
        return " ".join(raw_words)

    @staticmethod
    def _remove_digits_from_line(raw_line: str, separator: str = "") -> str:
        """
        Remove digits from lines
        @param raw_line: raw line to remove digits from
        @param separator: word string separator
        @return: cleaned-up line
        """
        raw_words = raw_line.split()
        for index, word in enumerate(raw_words):
            raw_words[index] = separator.join(filter(lambda x: x.isalpha(), word))
        return " ".join(raw_words)

    @staticmethod
    def _process_cookie(raw_line: str) -> str:
        """
        Process cookies
        @param raw_line: line that represents cookies
        @return: updated line
        """
        cookies = raw_line.lower().replace("set-cookie: ", "")
        cookie_pairs = cookies.split(";")
        for index, cookie_pair in enumerate(cookie_pairs):
            cookie_pair = cookie_pair.split("=")
            if len(cookie_pair) < 2:
                continue
            cookie_pair[1] = DefaultPlates.COOKIE_REPLACER
            cookie_pairs[index] = cookie_pair[0] + "=" + cookie_pair[1]
        return "Set-Cookie: " + ";".join(cookie_pairs)

    @staticmethod
    def _process_random_value(raw_line: str) -> str or None:
        """
        Process some values that are not really important, like ETag values
        @param raw_line: line that represents some header-line
        @return: updated line
        """
        raw_line = raw_line.split(": ")
        if len(raw_line) < 2:
            return
        raw_line[1] = (
            DefaultPlates.RANDOM_REPLACER
            + HttpParser._remove_special_chars_from_word(
                raw_line[0], separator=""
            ).lower()
        )
        return raw_line[0] + ": " + raw_line[1]

    def process_headers(self, host_str_repr: str) -> str or None:
        """
        Process headers from current host's data
        @param host_str_repr: string representation of host data
        @return: raw headers as a string
        """
        if "HTTP/".lower() not in host_str_repr.lower():
            return ""
        host_data = host_str_repr.replace("\\r\\n", "\r\n")
        raw_lines = host_data.splitlines()
        if len(raw_lines) == 1:
            return host_data
        headers = list()
        for raw_line in raw_lines:
            if raw_line == "":
                break
            if self.process_cookie:
                if "set-cookie" in raw_line.lower():
                    raw_line = HttpParser._process_cookie(raw_line)
            if self.process_trash_headers:
                if [
                    bad_tag
                    for bad_tag in TrashHeaders.HEADERS
                    if bad_tag.lower() in raw_line.lower()
                ]:
                    raw_line = HttpParser._process_random_value(raw_line) or raw_line
            if self.remove_special:
                raw_line = HttpParser._remove_special_chars_from_line(raw_line)
            if self.remove_digits:
                raw_line = HttpParser._remove_digits_from_line(raw_line)

            headers.append(raw_line)

        headers_str = " ".join(headers)

        return headers_str
