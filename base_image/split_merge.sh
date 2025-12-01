split -b 90M mypython.tar mypython.tar_part_
cat mypython.tar_part_* > mypython.tar
