# Negative Lookup Tables
###### This is a concept for my idea of negative lookup tables.

When encountering a password hash and one wants to perform a dictionary attack, there are hundreds of word lists to choose from. It would be convenient if one could rule out word lists. Negative lookup tables can tell if a hash can not be created with a word list in about O(log n) time. There is some chance of false positives, but no chance of false negatives. Thus the negatives are used to guarantee some property.

### How they work

Store the first x bytes of every hash created with the word list, using unique values, sorted. When encountering a new hash, one can take the first few bytes and perform a binary search. If the bytes are not in the file, the hash can't be created using the word list.

The number of bytes (x) to store is chosen as follows:

* Take the total space of possible values (256 to the power of x).

* Take the total space needed by x first bytes of the hash. This is (the number of words in the word list * x), minus the number of expected collisions.
* Now make sure the bytes from the hashes take up less than 50% of the total possible space.

Let's say the bytes take up 50% of the space. For every hash that is searched, there is a 50% chance of a false positive. So when we get a positive answer from a lookup, the answer is useless. However, if we get a negative answer (the bytes can not be found), we know for sure the hash could not be created using the word list!
That's why they are called negative lookup tables; it's useless if we get a positive result, but we can guarantee a property if we get a negative result (in this case, that the whole word list can not generate the hash).

### Using the POC

The POC (negativeTablePOC.py) creates a negative lookup table for the rockyou.txt word list. It's then possible to perform lookups with in this table. When a negative result is returned, one can say for sure that the hash can not be created using the word list.

To use the POC, first download the rockyou.txt word list from a site like:

https://wiki.skullsecurity.org/Passwords

Put the rockyou.txt file next to negativeTablePOC.py and run it (python negativeTablePOC.py). Now comment out line 172 and play with the lookups.

### Sample output

```
$ python negativeTablePOC.py 
Creating table for file: rockyou.txt
Choosing table size..
Using 4 bytes gives me 4294967296 values of space
I estimate 2254631.96874 collisions
Leaving about 137666865.031 values used
This table will be filled by about 0.032053064795
Starting loading wordlist..
Performing two lookups
True
False
```
