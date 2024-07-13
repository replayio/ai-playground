thisFile=$(readlink -f "$BASH_SOURCE")
thisDir=$(dirname "$thisFile")

code --diff $thisDir/file1.txt $thisDir/file2.txt
