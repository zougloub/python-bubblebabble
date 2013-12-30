#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Implementation of The Bubble Babble Binary Data Encoding
# http://web.mit.edu/kenta/www/one/bubblebabble/spec/jrtrjwzi/draft-huima-01.txt

__author__ = "Jérôme Carretero <cJ-bb@zougloub.eu>"
__copyright__ = "Copyright 2013, %s" % __author__
__license__ = "Public Domain"

vow = "aeiouy";
con = "bcdfghklmnprstvzx";

def encode(s):
	"""
	:param s: input encoded message as bytes
	:rtype: str
	"""
	s = bytearray(s)
	C = 1
	rounds = 1 + len(s) // 2;
	out = [con[-1]]

	for i in range(rounds):
		if i + 1 < rounds or len(s) % 2 == 1:
			out.append(vow[(((s[2 * i] >> 6) & 3) + C) % 6])
			out.append(con[(s[2 * i] >> 2) & 15]);
			out.append(vow[((s[2 * i] & 3) + C // 6) % 6]);

			if i + 1 < rounds:
				out.append(con[(s[2 * i + 1] >> 4) & 15]);
				out.append("-");
				out.append(con[s[2 * i + 1] & 15]);
				C = (C * 5 + s[2 * i] * 7 + s[2 * i + 1]) % 36;
		else:
			out.append(vow[C % 6]);
			out.append(con[-1]);
			out.append(vow[C // 6]);

	out.append(con[-1]);

	return "".join(out)

def _decode_3way(a, b, c, pos, C):
	h2 = (a - (C%6) + 6) % 6
	assert h2 < 4, "Corrupt char at %d" % (pos)
	assert b < 16, "Corrupt char at %d" % (pos+1)
	m4 = b
	l2 = (c - ((C//6) % 6)) % 6
	assert l2 < 4, "Corrupt char at %d" % (pos+2)
	return (h2<<6) | (m4<<2) | l2

def _decode_2way(a, b, pos):
	assert a < 16, "Corrupt char at %d" % pos
	assert b < 16, "Corrupt char at %d" % (pos+1)
	return (a<<4)|b

def _decode_tuple(t, pos):
	a = vow.index(t[0])
	b = con.index(t[1])
	c = vow.index(t[2])

	if len(t) > 4:
		d = con.index(t[3])
		e = con.index(t[5])
		return a, b, c, d, e

	return a, b, c

def decode(encoded):
	"""
	:rtype: bytes
	"""
	c = 1
	out = bytearray()
	l = len(encoded)

	assert encoded[0] == 'x', "Must begin with an 'x'"
	assert encoded[-1] == 'x', "Must end with an 'x'"
	assert l % 6 == 5, "Bad length"

	pos = 1
	while pos < (l//6) * 6:
		t = _decode_tuple(encoded[pos:pos+6], pos)
		b1 = _decode_3way(t[0], t[1], t[2], pos, c)
		b2 = _decode_2way(t[3], t[4], pos+2)
		c = ((c * 5) + (b1 * 7) + b2) % 36
		out.append(b1)
		out.append(b2)
		pos += 6

	t = _decode_tuple(encoded[pos:pos+6], pos)
	if t[1] == 16:
		assert t[0] == c % 6, "Corrupt char at %d" % (pos)
		assert t[2] == c // 6, "Corrupt char at %d" % (pos+2)
	else:
		b1 = _decode_3way(t[0], t[1], t[2], pos, c)
		out.append(b1)

	return bytes(out)


if __name__ == '__main__':
	for a in (b'', b'1234567890', b'Pineapple'):
		b = encode(a)
		c = decode(b)
		print("%s -> %s -> %s" % (a, b, c))


