OUT =doc

default:
	echo “specify target”

.PHONY: doc
doc:
	bash ./doc/generate_doxygen.sh $(OUT)

remote:
	bash ./doc/publish-doxygen.sh 

