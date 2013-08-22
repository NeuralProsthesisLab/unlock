
all: offline-analysis clean-junk

offline-analysis:
	pdflatex offline-analysis.tex
	pdflatex offline-analysis.tex
	htlatex offline-analysis.tex
	htlatex offline-analysis.tex

unlock:
	pdflatex unlock.tex
	pdflatex unlock.tex
	htlatex unlock.tex
	htlatex unlock.tex

clean-junk:
	rm -rf *.dvi *.idv *.lg *.aux *.log *.out *.haux  *.htoc *.image.tex *.css *.4ct *.4tc *.xref

clean:
	rm *.pdf *.html



