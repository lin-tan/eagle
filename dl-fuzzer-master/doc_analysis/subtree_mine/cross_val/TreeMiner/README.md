1) The input must be in the following format:

id id length string_encoding

where id is repeated twice (the same value for the tree number), 

length is the number of items to follow on the line

string_encoding is the coding of the tree 

example: 

    0 0 7 1 2 -1 3 4 -1 -1
    1 1 11 2 1 2 -1 4 -1 -1 2 -1 3 -1
    2 2 15 1 3 2 -1 -1 5 1 2 -1 3 4 -1 -1 -1 -1

the first tree's string encoding has length 7 (including -1's), and so on.
This DB has 3 trees. 

This DB can also be converted to binary format if desired.

2) run treeminer as follows:

        treeminer -i XXX -s MINSUP
                where XXX is the full name of the DB
                      MINSUP is minsup in decimals (0.5 is 50%)
        other options are as follows:
                 -o print frequent trees to STDOUT
                 -S use absolute support value
		 -b if database is in binary format

The output has info about the freq trees at diff levels and the total
time taken.
