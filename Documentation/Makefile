# dependencies: pandoc, texlive
#
src  = $(wildcard *.rst)
pdf  = $(patsubst %.rst,%.pdf,$(src))

default: all
all: $(pdf)
pdf: $(pdf)

%.pdf: %.rst
	pandoc --to=latex -o $@ $^

clean:
	rm -f $(pdf)
