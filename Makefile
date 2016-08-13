# supportive Makefile for binec

ROFF=ronn
RFLAGS=--manual=BINENC --organization=nope --date=$(shell date -I)
RONNPAGES=$(wildcard *.ronn)
MANPAGES=$(RONNPAGES:.ronn=)

.PHONY: all clean

all: man

man: $(MANPAGES)
	@echo $(MANPAGES)

%.1: %.1.ronn
	$(ROFF) -r $(RFLAGS) $<
